"""Time helpers.

All timestamps in taskqueue are wall-clock **epoch seconds** (floats from
``time.time()``): job timestamps, lease deadlines, event-log ``ts`` fields.
Durations are float seconds.
"""

from __future__ import annotations

import time


def now() -> float:
    """Current wall-clock time as epoch seconds."""
    return time.time()


def lease_deadline(start: float, ttl_s: float) -> float:
    """Deadline (epoch seconds) for a lease taken at *start* with TTL *ttl_s*."""
    return start + ttl_s


def elapsed(since: float) -> float:
    """Seconds elapsed since the epoch-seconds timestamp *since*."""
    return time.time() - since


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
