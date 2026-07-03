"""OpenAI Codex CLI adapter.

Runs the shared standard prompt through `codex exec --json` (read-only sandbox),
which streams JSONL events. We collect the agent's message text (the review) and
the `turn.completed` usage totals (including reasoning tokens), so we get real
per-run token accounting for cost estimation.

We deliberately use `codex exec` (not `codex review`) because it is the only mode
that reports token usage and because sending the SAME prompt to every tool/model
is what makes the benchmark comparable.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .base import Provider, ReviewResult

_USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


class CodexProvider(Provider):
    name = "codex"

    def run_review(
        self, project_copy: Path, model: str, effort: str, prompt: str
    ) -> ReviewResult:
        cmd = [
            "codex", "exec", "--json", "--skip-git-repo-check", "-s", "read-only",
            "-c", f"model={model}",
            "-c", f"model_reasoning_effort={effort}",
            prompt,
        ]
        t0 = time.monotonic()
        proc = subprocess.run(cmd, cwd=project_copy, capture_output=True, text=True, encoding="utf-8", errors="replace")
        elapsed = time.monotonic() - t0

        texts: list[str] = []
        usage: dict | None = None
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            etype = ev.get("type")
            if etype == "item.completed":
                item = ev.get("item", {})
                if item.get("type") == "agent_message" and item.get("text"):
                    texts.append(item["text"])
            elif etype == "turn.completed":
                u = ev.get("usage")
                if u:
                    if usage is None:
                        usage = {k: u.get(k, 0) for k in _USAGE_KEYS}
                    else:
                        for k in _USAGE_KEYS:
                            usage[k] += u.get(k, 0)

        findings = "\n\n".join(texts) if texts else proc.stdout
        raw = proc.stdout
        if proc.returncode != 0 and proc.stderr:
            raw = f"{raw}\n[stderr]\n{proc.stderr}"

        return ReviewResult(
            findings_text=findings,
            raw_output=raw,
            command=(
                f"codex exec --json -s read-only "
                f"-c model={model} -c model_reasoning_effort={effort} <prompt>"
            ),
            returncode=proc.returncode,
            elapsed_s=elapsed,
            usage=usage,
        )
