"""Configuration loading.

The config file is deliberately simple — flat ``key: value`` lines (a strict
subset of YAML) — so the service has no third-party dependencies. Unknown keys
are rejected to catch typos early.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

from taskqueue.core.errors import ConfigError


@dataclass(frozen=True)
class Config:
    queue_max_size: int = 10_000
    lease_ttl_s: float = 60.0
    retry_base_s: float = 1.0
    retry_cap_s: float = 60.0
    max_attempts: int = 5
    status_ttl_s: float = 30.0
    poll_interval_s: float = 0.5
    workers: int = 4
    rate_limit_per_minute: int = 120
    events_path: str = "events.jsonl"
    audit_log_path: str = "audit.log"
    plugins: str = ""

    def plugin_modules(self) -> list[str]:
        return [name.strip() for name in self.plugins.split(",") if name.strip()]


_FIELD_TYPES = {f.name: f.type for f in fields(Config)}


def _coerce(name: str, raw: str):
    kind = _FIELD_TYPES[name]
    try:
        if kind == "int":
            return int(raw)
        if kind == "float":
            return float(raw)
        return raw
    except ValueError as exc:
        raise ConfigError(f"bad value for {name!r}: {raw!r}") from exc


def load(path: str | Path) -> Config:
    """Parse *path* into a :class:`Config`, applying defaults for absent keys."""
    text = Path(path).read_text(encoding="utf-8")
    values = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ConfigError(f"line {lineno}: expected 'key: value', got {line!r}")
        key, _, raw = line.partition(":")
        key = key.strip()
        if key not in _FIELD_TYPES:
            raise ConfigError(f"line {lineno}: unknown key {key!r}")
        values[key] = _coerce(key, raw.strip())
    return Config(**values)
