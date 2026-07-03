"""Provider adapter interface.

A provider runs one tool's review over a prepared copy of a project, using the
shared standard prompt, and returns its findings text plus (if available) token
usage and wall-clock time. Scoring is done separately by the judge.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReviewResult:
    findings_text: str        # the review the judge scores
    raw_output: str           # full tool output (for the raw dump / debugging)
    command: str              # abbreviated command line (for the report)
    returncode: int           # non-zero usually means the tool/model errored
    elapsed_s: float          # wall-clock seconds for the review call
    usage: dict | None = None # {input_tokens, cached_input_tokens, output_tokens, reasoning_output_tokens}
    cost_usd: float | None = None  # provider-supplied API-equivalent cost; if None, runner computes from pricing.json


class Provider:
    #: short name used in config, CLI flags, and the registry
    name: str = "base"

    def run_review(
        self, project_copy: Path, model: str, effort: str, prompt: str
    ) -> ReviewResult:
        """Run a review of the project checked out at `project_copy`."""
        raise NotImplementedError
