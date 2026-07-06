"""CodeRabbit CLI adapter.

CodeRabbit is fundamentally different from the other subjects: it reviews a
**git diff**, not a working tree, and it runs its **own** review engine (it does
NOT accept our standard prompt — the `-c` flag only adds side instructions). So
this provider is marked `native = true` in config and its results are labelled
`native` (not directly comparable to the standard-v1 prompt on the prompt axis,
but recall against the same planted bugs is still meaningful).

To make it review the WHOLE project (matching the full-tree tools), we turn the
disposable copy into a one-commit git repo on top of an empty base commit, then
diff the project against that empty base — so every file reads as "added". The
copy already lives in an OS temp dir with no answer key reachable, so git-init
inside it does not weaken isolation.

Requirements: the `git` and `coderabbit` binaries on PATH, and `coderabbit auth`
already logged in. Free accounts work but consume a per-account "CLI allowance"
and may rate-limit. CodeRabbit reports no token usage, so there is no cost/token
column for it (speed only).

Output: `coderabbit review --agent` emits JSONL — status lines plus
`{"type":"finding","severity","fileName","codegenInstructions",...}` objects and
a final `{"type":"complete","findings":N}`. We concatenate the finding objects
into the text the judge scores.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from .base import Provider, ReviewResult

_BASE_BRANCH = "bughunt-empty-base"


def _git_env() -> dict:
    # Isolate from the user's global/system git config (signing, hooks, identity)
    # so the throwaway repo commits cleanly and non-interactively everywhere.
    return {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "bughunt",
        "GIT_AUTHOR_EMAIL": "bughunt@localhost",
        "GIT_COMMITTER_NAME": "bughunt",
        "GIT_COMMITTER_EMAIL": "bughunt@localhost",
    }


def _git(args: list[str], cwd: Path, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


class CodeRabbitProvider(Provider):
    name = "coderabbit"

    def _prepare_git(self, copy: Path) -> str | None:
        """Turn the copy into: empty base commit -> full-project commit.

        Returns None on success, or an error string if git setup failed.
        """
        env = _git_env()
        steps = [
            ["init", "-q"],
            ["commit", "-q", "--allow-empty", "-m", "empty base"],  # base commit
            ["branch", _BASE_BRANCH],                               # base -> empty
            ["add", "-A"],
            ["commit", "-q", "-m", "project under review"],         # full project
        ]
        for args in steps:
            proc = _git(args, copy, env)
            if proc.returncode != 0:
                return f"git {' '.join(args)} failed: {proc.stderr.strip()}"
        return None

    def run_review(
        self, project_copy: Path, model: str, effort: str, prompt: str
    ) -> ReviewResult:
        t0 = time.monotonic()

        # 0) fast auth pre-check: if the CLI session has expired, a review would
        #    otherwise hang ~5 min waiting for a headless browser login to time
        #    out. Fail fast instead so a dropped session doesn't stall a sweep.
        auth = subprocess.run(
            ["coderabbit", "auth", "status"], stdin=subprocess.DEVNULL,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if "signed out" in auth.stdout.lower() or auth.returncode != 0:
            return ReviewResult(
                findings_text="",
                raw_output="[coderabbit auth] not signed in — run `coderabbit auth login`\n" + auth.stdout,
                command="coderabbit auth status",
                returncode=1,
                elapsed_s=round(time.monotonic() - t0, 1),
                usage=None,
                cost_usd=None,
            )

        # 1) git setup. Diff-mode projects arrive as a ready git repo (main +
        #    PR branch checked out) — CodeRabbit's home turf, diff against main.
        #    Whole-tree projects get the empty-base treatment so every file
        #    reads as "added".
        if (project_copy / ".git").exists():
            base_branch = "main"
        else:
            base_branch = _BASE_BRANCH
            git_err = self._prepare_git(project_copy)
            if git_err:
                return ReviewResult(
                    findings_text="",
                    raw_output=f"[git setup failed]\n{git_err}",
                    command="git init + empty base + project commit",
                    returncode=1,
                    elapsed_s=round(time.monotonic() - t0, 1),
                    usage=None,
                    cost_usd=None,
                )

        # 2) run the native review against the base branch.
        #    `prompt` is ignored on purpose — CodeRabbit uses its own engine.
        cmd = [
            "coderabbit", "review",
            "--base", base_branch,
            "--agent",
            "--type", "all",
        ]
        if effort == "light":
            cmd.append("--light")

        proc = subprocess.run(
            cmd, cwd=project_copy, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        elapsed = time.monotonic() - t0

        findings: list[dict] = []
        completed = False
        error_msg = None
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = obj.get("type")
            if t == "finding":
                findings.append(obj)
            elif t == "complete":
                completed = True
            elif t == "error" or (t == "status" and obj.get("status") == "error"):
                error_msg = obj.get("message") or obj.get("error")

        findings_text = _format_findings(findings)

        # returncode: non-zero if the CLI errored, or if it never reported completion.
        rc = proc.returncode
        if rc == 0 and not completed and not findings:
            rc = 1  # no findings AND no completion event => treat as a failed review

        raw = proc.stdout
        tail = proc.stderr.strip()
        if error_msg:
            raw = f"{raw}\n[error] {error_msg}"
        if rc != 0 and tail:
            raw = f"{raw}\n[stderr]\n{tail}"

        return ReviewResult(
            findings_text=findings_text,
            raw_output=raw,
            command=f"coderabbit review --base {base_branch} --agent --type all"
                    + (" --light" if effort == "light" else ""),
            returncode=rc,
            elapsed_s=elapsed,
            usage=None,      # CodeRabbit reports no token usage
            cost_usd=None,   # -> no cost column (speed only)
        )


def _format_findings(findings: list[dict]) -> str:
    """Render CodeRabbit's JSON findings into text the judge can score."""
    if not findings:
        return "No findings reported."
    blocks = []
    for i, f in enumerate(findings, 1):
        sev = f.get("severity", "?")
        fname = f.get("fileName", "?")
        body = f.get("codegenInstructions", "").strip()
        block = f"### Finding {i} — severity: {sev} — file: {fname}\n{body}"
        sugg = f.get("suggestions") or []
        if sugg:
            block += "\n\nSuggested fix:\n" + str(sugg[0]).strip()
        blocks.append(block)
    return "\n\n".join(blocks)
