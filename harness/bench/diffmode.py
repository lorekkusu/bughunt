"""Diff-mode projects: materialize a PR checkout from base tree + overlay.

A diff-mode project (``review_mode = "diff"`` in config.toml) pairs a base tree
under ``projects/<name>/`` with ``patches/<name>/``:

    patches/<name>/
    ├── manifest.toml   # [pr] branch/title/description + [files] ops
    └── overlay/        # head-state version of every changed/added file

The harness materializes the review checkout as a real git repo:

    copy base tree -> git init -> commit as `main`
    -> git checkout -b <pr.branch> -> copy overlay over the tree
    -> apply [files] deletions/renames -> commit (title + description)

so the diff under review is always produced by git itself (never stored, never
able to drift), and the PR description is readable via ``git log``. The copy
lives in an OS temp dir (see runner._prepare_copy), so initializing git inside
it cannot expose the answer key.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tomllib
from pathlib import Path


class DiffSetupError(RuntimeError):
    pass


def _git_env() -> dict:
    # Isolate from the user's global/system git config (signing, hooks,
    # identity) so the throwaway repo commits cleanly everywhere.
    return {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "bughunt",
        "GIT_AUTHOR_EMAIL": "bughunt@localhost",
        "GIT_COMMITTER_NAME": "bughunt",
        "GIT_COMMITTER_EMAIL": "bughunt@localhost",
    }


def _git(repo: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", *args], cwd=repo, env=_git_env(),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise DiffSetupError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")


def load_patch_manifest(patch_dir: Path) -> dict:
    manifest_path = patch_dir / "manifest.toml"
    if not manifest_path.exists():
        raise DiffSetupError(f"no manifest.toml under {patch_dir}")
    return tomllib.loads(manifest_path.read_text(encoding="utf-8"))


def apply_pr(copy: Path, patch_dir: Path) -> None:
    """Turn a plain base-tree copy into a git repo with the PR checked out."""
    manifest = load_patch_manifest(patch_dir)
    pr = manifest.get("pr", {})
    branch = pr.get("branch", "pr-under-review")
    title = pr.get("title", "changes under review")
    description = pr.get("description", "").strip()
    message = f"{title}\n\n{description}" if description else title

    _git(copy, "init", "-q")
    _git(copy, "add", "-A")
    _git(copy, "commit", "-qm", "base")
    _git(copy, "branch", "-m", "main")
    _git(copy, "checkout", "-qb", branch)

    overlay = patch_dir / "overlay"
    if not overlay.is_dir():
        raise DiffSetupError(f"no overlay/ under {patch_dir}")
    shutil.copytree(overlay, copy, dirs_exist_ok=True)

    ops = manifest.get("files", {})
    for rel in ops.get("deleted", []):
        target = copy / rel
        if not target.exists():
            raise DiffSetupError(f"[files].deleted lists missing path: {rel}")
        target.unlink()
    for pair in ops.get("renamed", []):
        old, new = pair["from"], pair["to"]
        (copy / new).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(copy / old, copy / new)

    _git(copy, "add", "-A")
    _git(copy, "commit", "-qm", message)


# --------------------------------------------------------------------------- #
# validation (bench validate)
# --------------------------------------------------------------------------- #
def validate(src: Path, patch_dir: Path, manifest: dict) -> list[str]:
    """Static consistency checks for a diff-mode project.

    *manifest* here is the ANSWER-KEY manifest (planted_bugs/base_bugs/noise);
    the patch manifest is loaded from *patch_dir*. Returns human-readable
    problem strings (empty = OK).
    """
    problems: list[str] = []

    try:
        patch = load_patch_manifest(patch_dir)
    except DiffSetupError as exc:
        return [str(exc)]

    overlay = patch_dir / "overlay"
    if not overlay.is_dir():
        return [f"no overlay/ under {patch_dir}"]

    added = set(patch.get("files", {}).get("added", []))
    overlay_files = [p for p in overlay.rglob("*") if p.is_file()]
    if not overlay_files:
        problems.append("overlay/ is empty")

    for f in overlay_files:
        rel = f.relative_to(overlay).as_posix()
        base_file = src / rel
        if rel in added:
            if base_file.exists():
                problems.append(f"{rel}: listed in [files].added but exists in base")
            continue
        if not base_file.exists():
            problems.append(f"{rel}: not in base tree and not listed in [files].added")
        elif base_file.read_bytes() == f.read_bytes():
            problems.append(f"{rel}: overlay file is identical to base (no-op)")

    # answer-key paths must exist on the side they describe
    head_has = lambda rel: (overlay / rel).exists() or (src / rel).exists()
    for bug in manifest.get("planted_bugs", []):
        if not head_has(bug["file"]):
            problems.append(f"{bug['id']}: file not in head tree: {bug['file']}")
        ev = bug.get("evidence_file")
        if ev and not head_has(ev):
            problems.append(f"{bug['id']}: evidence_file not in head tree: {ev}")
    for bug in manifest.get("base_bugs", []):
        if not (src / bug["file"]).exists():
            problems.append(f"{bug['id']}: file not in base tree: {bug['file']}")
    for item in manifest.get("noise", []):
        if not head_has(item["file"]):
            problems.append(f"{item['id']}: file not in head tree: {item['file']}")

    return problems


def run_tests(copy: Path) -> tuple[bool, str]:
    """Run the project's test suite in *copy*; returns (passed, tail_of_output)."""
    proc = subprocess.run(
        ["uv", "run", "pytest", "-q"], cwd=copy,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-5:])
    return proc.returncode == 0, tail
