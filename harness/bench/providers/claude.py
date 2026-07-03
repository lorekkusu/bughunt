"""Anthropic Claude Code CLI adapter.

Runs the shared standard prompt through `claude -p --output-format json` with
`--permission-mode bypassPermissions` (no prompts) on the disposable fresh copy.
We do NOT use `--mode plan`: at higher effort it produces a sprawling *plan*
instead of a findings list, which the judge can't map to the planted bugs
(spurious 0% runs). The JSON wrapper reports the review text (`result`), full
token `usage`, and `total_cost_usd` (an API-equivalent cost we use directly).

The Claude Code CLI supports `--effort` (low/medium/high/xhigh/max; available
levels depend on the model), so this provider sweeps effort just like codex.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .base import Provider, ReviewResult


class ClaudeProvider(Provider):
    name = "claude"

    def run_review(
        self, project_copy: Path, model: str, effort: str, prompt: str
    ) -> ReviewResult:
        cmd = [
            "claude", "-p",
            "--output-format", "json",
            "--model", model,
            "--permission-mode", "bypassPermissions",
        ]
        if effort and effort != "default":
            cmd += ["--effort", effort]
        cmd.append(prompt)
        t0 = time.monotonic()
        proc = subprocess.run(cmd, cwd=project_copy, capture_output=True, text=True, encoding="utf-8", errors="replace")
        elapsed = time.monotonic() - t0

        findings = proc.stdout
        usage: dict | None = None
        cost: float | None = None
        try:
            wrapper = json.loads(proc.stdout)
            findings = wrapper.get("result", proc.stdout)
            cost = wrapper.get("total_cost_usd")
            u = wrapper.get("usage") or {}
            # normalize to the harness usage shape (cache_read -> cached_input)
            usage = {
                "input_tokens": u.get("input_tokens", 0),
                "cached_input_tokens": u.get("cache_read_input_tokens", 0),
                "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0),
                "output_tokens": u.get("output_tokens", 0),
            }
        except json.JSONDecodeError:
            pass

        raw = proc.stdout
        if proc.returncode != 0 and proc.stderr:
            raw = f"{raw}\n[stderr]\n{proc.stderr}"

        return ReviewResult(
            findings_text=findings,
            raw_output=raw,
            command=(
                f"claude -p --output-format json --model {model} "
                f"--permission-mode bypassPermissions --effort {effort} <prompt>"
            ),
            returncode=proc.returncode,
            elapsed_s=elapsed,
            usage=usage,
            cost_usd=cost,
        )
