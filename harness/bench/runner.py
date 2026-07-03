"""Orchestrate a benchmark config: N rounds of prepare -> review -> judge,
then aggregate, persist a results JSON, and support skip-if-unchanged."""

from __future__ import annotations

import hashlib
import json
import shutil
import statistics
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from . import judge
from .config import Config, load_manifest
from .pricing import cost_usd
from .providers import get_provider

_SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "uploads"}
_SKIP_SUFFIX = {".pyc", ".db"}
_IGNORE = shutil.ignore_patterns(
    ".git", ".venv", "__pycache__", ".pytest_cache", "*.pyc", "*.db", "uploads"
)


# --------------------------------------------------------------------------- #
# data model
# --------------------------------------------------------------------------- #
@dataclass
class RoundResult:
    found: list[str]
    false_positives: int
    bonus: int
    elapsed_s: float
    usage: dict | None
    cost_usd: float | None
    returncode: int
    fp_items: list[dict] = field(default_factory=list)
    bonus_items: list[dict] = field(default_factory=list)


@dataclass
class ConfigResult:
    project: str
    provider: str
    model: str
    effort: str
    prompt_id: str
    judge_model: str
    code_hash: str
    runs: int
    created: str
    planted: list[dict]            # manifest planted_bugs (id, severity, title, ...)
    rounds: list[RoundResult]
    skipped: bool = False
    manual: bool = False           # produced by a human-triggered tool via `bench judge`

    # ---- derived ----
    @property
    def total_planted(self) -> int:
        return len(self.planted)

    def per_bug_counts(self) -> dict[str, int]:
        counts = {b["id"]: 0 for b in self.planted}
        for r in self.rounds:
            for bid in r.found:
                if bid in counts:
                    counts[bid] += 1
        return counts

    def recall_per_round(self) -> list[float]:
        n = self.total_planted or 1
        return [len(set(r.found) & {b["id"] for b in self.planted}) / n for r in self.rounds]

    @staticmethod
    def _stats(values: list[float]) -> dict:
        vals = [v for v in values if v is not None]
        if not vals:
            return {"mean": None, "min": None, "max": None}
        return {
            "mean": statistics.fmean(vals),
            "min": min(vals),
            "max": max(vals),
        }

    def metrics(self) -> dict:
        return {
            "recall": self._stats(self.recall_per_round()),
            "false_positives": self._stats([r.false_positives for r in self.rounds]),
            "bonus": self._stats([r.bonus for r in self.rounds]),
            "elapsed_s": self._stats([r.elapsed_s for r in self.rounds]),
            "output_tokens": self._stats(
                [r.usage.get("output_tokens") if r.usage else None for r in self.rounds]
            ),
            "total_tokens": self._stats(
                [
                    (r.usage.get("input_tokens", 0) + r.usage.get("output_tokens", 0))
                    if r.usage else None
                    for r in self.rounds
                ]
            ),
            "cost_usd": self._stats([r.cost_usd for r in self.rounds]),
        }

    # ---- persistence ----
    def to_dict(self) -> dict:
        d = {
            k: getattr(self, k)
            for k in (
                "project", "provider", "model", "effort", "prompt_id",
                "judge_model", "code_hash", "runs", "created", "planted", "manual",
            )
        }
        d["rounds"] = [asdict(r) for r in self.rounds]
        d["per_bug"] = self.per_bug_counts()
        d["metrics"] = self.metrics()
        return d

    @classmethod
    def from_dict(cls, d: dict, skipped: bool = False) -> "ConfigResult":
        rounds = [
            RoundResult(
                found=r.get("found", []),
                false_positives=r.get("false_positives", 0),
                bonus=r.get("bonus", 0),
                elapsed_s=r.get("elapsed_s", 0.0),
                usage=r.get("usage"),
                cost_usd=r.get("cost_usd"),
                returncode=r.get("returncode", 0),
                fp_items=r.get("fp_items", []),
                bonus_items=r.get("bonus_items", []),
            )
            for r in d.get("rounds", [])
        ]
        return cls(
            project=d["project"], provider=d["provider"], model=d["model"],
            effort=d["effort"], prompt_id=d.get("prompt_id", "?"),
            judge_model=d.get("judge_model", "?"), code_hash=d.get("code_hash", ""),
            runs=d.get("runs", len(rounds)), created=d.get("created", ""),
            planted=d.get("planted", []), rounds=rounds, skipped=skipped,
            manual=d.get("manual", False),
        )


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def project_code_hash(src: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(src.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        if set(rel.parts) & _SKIP_DIRS or f.suffix in _SKIP_SUFFIX:
            continue
        h.update(rel.as_posix().encode())
        h.update(b"\0")
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def results_path(cfg: Config, project: str, provider: str, model: str, effort: str) -> Path:
    return cfg.results_dir / project / provider / model / f"{effort}.json"


def _prepare_copy(cfg: Config, src: Path, tag: str) -> Path:
    # Isolate the review copy in an OS temp dir OUTSIDE the repo, so no tool can
    # reach the answer key — not via `../` traversal, and not via the repo's git
    # history (`git show HEAD:answers/...`). `tempfile` is cross-platform.
    base = Path(tempfile.mkdtemp(prefix="bughunt-review-"))
    dest = base / src.name
    shutil.copytree(src, dest, ignore=_IGNORE)
    return dest


# --------------------------------------------------------------------------- #
# main entry
# --------------------------------------------------------------------------- #
def run_config(
    cfg: Config,
    project_name: str,
    provider_name: str,
    model: str,
    effort: str,
    runs: int,
    prompt: str,
    pricing: dict,
    judge_model: str | None = None,
    force: bool = False,
    keep_scratch: bool = False,
    on_round=None,
) -> ConfigResult:
    project = cfg.project(project_name)
    src = cfg.projects_dir / project["path"]
    if not src.exists():
        raise SystemExit(f"project path not found: {src}")
    judge_model = judge_model or cfg.judge_model
    code_hash = project_code_hash(src)
    out_path = results_path(cfg, project_name, provider_name, model, effort)

    # skip-if-unchanged: same code + enough runs already recorded
    if out_path.exists() and not force:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        if existing.get("code_hash") == code_hash and existing.get("runs", 0) >= runs:
            return ConfigResult.from_dict(existing, skipped=True)

    manifest = load_manifest(cfg.answers_dir / project["answer_key"])
    provider = get_provider(provider_name)
    rounds: list[RoundResult] = []

    for i in range(runs):
        tag = f"{project_name}__{provider_name}__{model}__{effort}__r{i+1}__{datetime.now():%Y%m%d-%H%M%S}"
        copy = _prepare_copy(cfg, src, tag)
        review = provider.run_review(copy, model, effort, prompt)
        verdict = judge.score(manifest, review.findings_text, model=judge_model)
        # provider may report its own API-equivalent cost (e.g. claude CLI);
        # otherwise estimate from token usage + pricing.json
        cost = review.cost_usd if review.cost_usd is not None else cost_usd(model, review.usage, pricing)
        rounds.append(
            RoundResult(
                found=verdict.found_ids,
                false_positives=len(verdict.false_positives),
                bonus=len(verdict.bonus_bugs),
                elapsed_s=round(review.elapsed_s, 1),
                usage=review.usage,
                cost_usd=cost,
                returncode=review.returncode,
                fp_items=verdict.false_positives,
                bonus_items=verdict.bonus_bugs,
            )
        )
        if not keep_scratch:
            shutil.rmtree(copy.parent, ignore_errors=True)  # remove the whole temp dir
        if on_round:
            on_round(i + 1, runs, rounds[-1])

    result = ConfigResult(
        project=project_name, provider=provider_name, model=model, effort=effort,
        prompt_id=cfg.prompt_id, judge_model=judge_model, code_hash=code_hash,
        runs=runs, created=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        planted=manifest.get("planted_bugs", []), rounds=rounds,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return result


def judge_manual(
    cfg: Config,
    project_name: str,
    provider_name: str,
    model: str,
    effort: str,
    result_texts: list[str],
    prompt_id: str,
    judge_model: str | None = None,
) -> ConfigResult:
    """Score one or more human-produced review outputs (e.g. Cursor Bugbot)
    against the answer key. No copy/review step — the human already ran the tool.
    Each result text is one round. Cost/speed/token are unavailable (None)."""
    project = cfg.project(project_name)
    src = cfg.projects_dir / project["path"]
    if not src.exists():
        raise SystemExit(f"project path not found: {src}")
    judge_model = judge_model or cfg.judge_model
    code_hash = project_code_hash(src)
    manifest = load_manifest(cfg.answers_dir / project["answer_key"])

    rounds: list[RoundResult] = []
    for text in result_texts:
        verdict = judge.score(manifest, text, model=judge_model)
        rounds.append(
            RoundResult(
                found=verdict.found_ids,
                false_positives=len(verdict.false_positives),
                bonus=len(verdict.bonus_bugs),
                elapsed_s=None,   # not measurable for a manual tool
                usage=None,
                cost_usd=None,
                returncode=0,
                fp_items=verdict.false_positives,
                bonus_items=verdict.bonus_bugs,
            )
        )

    result = ConfigResult(
        project=project_name, provider=provider_name, model=model, effort=effort,
        prompt_id=prompt_id, judge_model=judge_model, code_hash=code_hash,
        runs=len(rounds), created=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        planted=manifest.get("planted_bugs", []), rounds=rounds, manual=True,
    )
    out_path = results_path(cfg, project_name, provider_name, model, effort)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return result
