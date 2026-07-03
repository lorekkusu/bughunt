"""Provider adapter interface.

A provider knows how to run one tool's code review over a prepared copy of a
project (a fresh single-commit git repo in a scratch dir) and return its raw
textual findings. Scoring is done separately by the judge.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReviewResult:
    raw_output: str      # everything the tool emitted (findings + any noise)
    command: str         # the command line that was run (for the report)
    returncode: int      # non-zero usually means the tool/model errored


class Provider:
    #: short name used in config, CLI flags, and the registry
    name: str = "base"

    def run_review(self, project_copy: Path, model: str, effort: str) -> ReviewResult:
        """Run a review of the project checked out at `project_copy`."""
        raise NotImplementedError
