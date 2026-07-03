"""Cursor Agent CLI adapter.

Runs the shared standard prompt through `cursor-agent -p --output-format json`
on the prepared fresh copy. We do NOT use `--mode plan` (it can emit a "plan"
instead of a findings list); the copy is disposable, so `--force --trust` lets
it run headlessly without approval prompts. Cursor's own models (Composer 2.5 /
2.5 Fast, and others) are exposed via `--model`.

The JSON wrapper reports the review text (`result`) and `usage`
(inputTokens/outputTokens/cacheReadTokens). There is no cost field — cost is
computed by the runner from token usage + pricing.json (Composer prices).
Cursor Agent has no per-run effort flag, so the effort label is ignored.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .base import Provider, ReviewResult


class CursorAgentProvider(Provider):
    name = "cursor-agent"

    def run_review(
        self, project_copy: Path, model: str, effort: str, prompt: str
    ) -> ReviewResult:
        cmd = [
            "cursor-agent", "-p",
            "--output-format", "json",
            "--model", model,
            "--force", "--trust",
            prompt,
        ]
        t0 = time.monotonic()
        proc = subprocess.run(cmd, cwd=project_copy, capture_output=True, text=True, encoding="utf-8", errors="replace")
        elapsed = time.monotonic() - t0

        findings = proc.stdout
        usage: dict | None = None
        try:
            wrapper = json.loads(proc.stdout)
            findings = wrapper.get("result", proc.stdout)
            u = wrapper.get("usage") or {}
            usage = {
                "input_tokens": u.get("inputTokens", 0),
                "cached_input_tokens": u.get("cacheReadTokens", 0),
                "output_tokens": u.get("outputTokens", 0),
            }
        except json.JSONDecodeError:
            pass

        raw = proc.stdout
        if proc.returncode != 0 and proc.stderr:
            raw = f"{raw}\n[stderr]\n{proc.stderr}"

        return ReviewResult(
            findings_text=findings,
            raw_output=raw,
            command=f"cursor-agent -p --output-format json --model {model} --force --trust <prompt>",
            returncode=proc.returncode,
            elapsed_s=elapsed,
            usage=usage,
            cost_usd=None,  # computed by runner from usage + pricing.json
        )
