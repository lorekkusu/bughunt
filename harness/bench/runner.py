"""Orchestrate one benchmark run: prepare copy -> review -> judge -> result."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from . import judge
from .config import Config, load_manifest
from .providers import get_provider
from .providers.base import ReviewResult

_IGNORE = shutil.ignore_patterns(
    ".git", ".venv", "__pycache__", ".pytest_cache", "*.pyc", "*.db", "uploads"
)


@dataclass
class RunResult:
    project: str
    provider: str
    model: str
    effort: str
    judge_model: str
    started: str
    review: ReviewResult
    verdict: judge.Verdict
    manifest: dict
    scratch: Path
    notes: list[str] = field(default_factory=list)

    # ----- derived metrics -----
    @property
    def total_planted(self) -> int:
        return len(self.manifest.get("planted_bugs", []))

    @property
    def found(self) -> int:
        return len(self.verdict.found_ids)

    @property
    def recall(self) -> float:
        return self.found / self.total_planted if self.total_planted else 0.0

    @property
    def false_positives(self) -> int:
        return len(self.verdict.false_positives)

    def severity_breakdown(self) -> dict[str, tuple[int, int]]:
        """severity -> (found, total)."""
        by_sev: dict[str, list[int]] = {}
        found = set(self.verdict.found_ids)
        for bug in self.manifest.get("planted_bugs", []):
            sev = bug.get("severity", "?")
            slot = by_sev.setdefault(sev, [0, 0])
            slot[1] += 1
            if bug["id"] in found:
                slot[0] += 1
        return {k: (v[0], v[1]) for k, v in by_sev.items()}


def _prepare_copy(cfg: Config, project: dict, tag: str) -> Path:
    src = cfg.projects_dir / project["path"]
    if not src.exists():
        raise SystemExit(f"project path not found: {src}")
    cfg.scratch_dir.mkdir(parents=True, exist_ok=True)
    dest = cfg.scratch_dir / tag
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=_IGNORE)

    # fresh single-commit repo so `codex review --commit HEAD` sees the whole project
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    subprocess.run(
        ["git",
         "-c", "commit.gpgsign=false",
         "-c", "user.name=bughunt",
         "-c", "user.email=bughunt@localhost",
         "commit", "-q", "-m", "snapshot"],
        cwd=dest, check=True,
    )
    return dest


def run_once(
    cfg: Config,
    project_name: str,
    provider_name: str,
    model: str,
    effort: str,
    judge_model: str | None = None,
    keep_scratch: bool = False,
) -> RunResult:
    project = cfg.project(project_name)
    judge_model = judge_model or cfg.judge_model
    started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag = f"{project_name}__{provider_name}__{model}__{effort}__{datetime.now():%Y%m%d-%H%M%S}"

    scratch = _prepare_copy(cfg, project, tag)

    provider = get_provider(provider_name)
    review = provider.run_review(scratch, model, effort)

    notes: list[str] = []
    if review.returncode != 0:
        notes.append(
            f"⚠️ provider exited with code {review.returncode} "
            f"(model {model!r} may not support effort {effort!r})"
        )

    manifest = load_manifest(cfg.answers_dir / project["answer_key"])
    verdict = judge.score(manifest, review.raw_output, model=judge_model)

    if not keep_scratch:
        shutil.rmtree(scratch, ignore_errors=True)

    return RunResult(
        project=project_name,
        provider=provider_name,
        model=model,
        effort=effort,
        judge_model=judge_model,
        started=started,
        review=review,
        verdict=verdict,
        manifest=manifest,
        scratch=scratch,
        notes=notes,
    )
