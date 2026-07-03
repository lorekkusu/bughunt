"""OpenAI Codex CLI adapter.

Runs `codex review --commit HEAD` in the prepared scratch copy, selecting the
model and reasoning effort via `-c` overrides. The scratch copy is a fresh
single-commit repo, so the whole project shows up as one reviewable diff.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .base import Provider, ReviewResult


class CodexProvider(Provider):
    name = "codex"

    def run_review(self, project_copy: Path, model: str, effort: str) -> ReviewResult:
        cmd = [
            "codex", "review", "--commit", "HEAD",
            "-c", f"model={model}",
            "-c", f"model_reasoning_effort={effort}",
        ]
        proc = subprocess.run(
            cmd,
            cwd=project_copy,
            capture_output=True,
            text=True,
        )
        # Codex prints the review to stdout; keep stderr too in case of errors.
        raw = proc.stdout
        if proc.returncode != 0 and proc.stderr:
            raw = f"{raw}\n[stderr]\n{proc.stderr}"
        return ReviewResult(
            raw_output=raw,
            command=" ".join(cmd),
            returncode=proc.returncode,
        )
