"""Config + answer-key loading."""

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
    reports_dir: Path
    judge_model: str

    @property
    def project_names(self) -> list[str]:
        return [p["name"] for p in self.raw.get("projects", [])]

    def project(self, name: str) -> dict:
        for p in self.raw.get("projects", []):
            if p["name"] == name:
                return p
        raise SystemExit(f"Unknown project {name!r}. Known: {', '.join(self.project_names)}")

    @property
    def provider_names(self) -> list[str]:
        return list(self.raw.get("providers", {}).keys())

    def provider_cfg(self, name: str) -> dict:
        try:
            return self.raw["providers"][name]
        except KeyError:
            raise SystemExit(f"Unknown provider {name!r}. Known: {', '.join(self.provider_names)}")


def load_config(path: Path | None = None) -> Config:
    path = path or (HARNESS_DIR / "config.toml")
    raw = tomllib.loads(path.read_text())
    paths = raw.get("paths", {})

    def resolve(key: str, default: str) -> Path:
        return (HARNESS_DIR / paths.get(key, default)).resolve()

    return Config(
        raw=raw,
        projects_dir=resolve("projects_dir", "../projects"),
        answers_dir=resolve("answers_dir", "../answers"),
        scratch_dir=resolve("scratch_dir", "../projects/.bench"),
        reports_dir=resolve("reports_dir", "reports"),
        judge_model=raw.get("judge", {}).get("model", "opus"),
    )


def load_manifest(answer_key_path: Path) -> dict:
    """Read the YAML frontmatter manifest from an answer-key markdown file."""
    text = answer_key_path.read_text()
    if not text.startswith("---"):
        raise SystemExit(f"{answer_key_path} has no YAML frontmatter manifest")
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm)
