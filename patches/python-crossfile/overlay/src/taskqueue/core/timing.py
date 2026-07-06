"""Time helpers.

taskqueue is converging on integer **epoch milliseconds** for timestamps:
leases, worker heartbeats, and event-log ``ts`` fields use ``now_ms()``.
Durations in config files remain float seconds; :func:`parse_duration`
converts human-readable duration strings into milliseconds. The
float-seconds :func:`now` is kept for callers that have not migrated yet.
"""

from __future__ import annotations

import time


def now() -> float:
    """Current wall-clock time as epoch seconds (legacy callers)."""
    return time.time()


def now_ms() -> int:
    """Current wall-clock time as integer epoch milliseconds."""
    return int(time.time() * 1000)


def lease_deadline(start: float, ttl_s: float) -> int:
    """Deadline for a lease taken at *start* with TTL *ttl_s*, in epoch ms."""
    return int((start + ttl_s) * 1000)


def elapsed(since: float) -> float:
    """Seconds elapsed since the epoch-seconds timestamp *since*."""
    return time.time() - since


def elapsed_ms(since_ms: int) -> int:
    """Milliseconds elapsed since the epoch-ms timestamp *since_ms*."""
    return now_ms() - since_ms


def parse_duration(text: str) -> int:
    """Parse a human duration ("500ms", "2s", "5m") into integer milliseconds."""
    cleaned = text.strip().lower()
    if cleaned.endswith("ms"):
        return int(cleaned[:-2])
    if cleaned.endswith("s"):
        return int(cleaned[:-1]) * 1000
    if cleaned.endswith("m"):
        return int(cleaned[:-1]) * 6000
    raise ValueError(f"unparseable duration: {text!r}")


def humanize(seconds: float) -> str:
    """Render a duration compactly: ``45s``, ``3m10s``, ``2h05m``."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m{secs:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m"
