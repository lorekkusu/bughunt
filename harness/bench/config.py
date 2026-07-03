"""Config + answer-key + prompt + pricing loading."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

HARNESS_DIR = Path(__file__).resolve().parent.parent  # the harness/ directory


@dataclass
class Config:
    raw: dict
    projects_dir: Path
    answers_dir: Path
    scratch_dir: Path
    results_dir: Path
    reports_dir: Path
    pricing_file: Path
    prompt_file: Path
    prompt_id: str
    default_runs: int
    judge_model: str

    # ----- projects -----
    @property
    def project_names(self) -> list[str]:
        return [p["name"] for p in self.raw.get("projects", [])]

    def project(self, name: str) -> dict:
        for p in self.raw.get("projects", []):
            if p["name"] == name:
                return p
        raise SystemExit(f"Unknown project {name!r}. Known: {', '.join(self.project_names)}")

    # ----- providers -----
    @property
    def provider_names(self) -> list[str]:
        return list(self.raw.get("providers", {}).keys())

    def provider_cfg(self, name: str) -> dict:
        try:
            return self.raw["providers"][name]
        except KeyError:
            raise SystemExit(f"Unknown provider {name!r}. Known: {', '.join(self.provider_names)}")

    # ----- prompt -----
    def review_prompt(self) -> str:
        text = self.prompt_file.read_text(encoding="utf-8")
        # strip a leading HTML comment block (documentation), keep the literal prompt
        if text.lstrip().startswith("<!--"):
            _, _, text = text.partition("-->")
        return text.strip()


def load_config(path: Path | None = None) -> Config:
    path = path or (HARNESS_DIR / "config.toml")
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    paths = raw.get("paths", {})
    run = raw.get("run", {})

    def resolve(section: dict, key: str, default: str) -> Path:
        return (HARNESS_DIR / section.get(key, default)).resolve()

    return Config(
        raw=raw,
        projects_dir=resolve(paths, "projects_dir", "../projects"),
        answers_dir=resolve(paths, "answers_dir", "../answers"),
        scratch_dir=resolve(paths, "scratch_dir", "../projects/.bench"),
        results_dir=resolve(paths, "results_dir", "results"),
        reports_dir=resolve(paths, "reports_dir", "reports"),
        pricing_file=resolve(paths, "pricing_file", "pricing.json"),
        prompt_file=resolve(paths, "prompt_file", "review_prompt.md"),
        prompt_id=run.get("prompt_id", "standard-v1"),
        default_runs=int(run.get("default_runs", 5)),
        judge_model=raw.get("judge", {}).get("model", "opus"),
    )


def load_manifest(answer_key_path: Path) -> dict:
    """Read the YAML frontmatter manifest from an answer-key markdown file."""
    text = answer_key_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit(f"{answer_key_path} has no YAML frontmatter manifest")
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm)
