"""Job priority levels and queue ordering.

The queue orders by priority rank first (high before normal before low), then
by submission time so equal-priority jobs run FIFO.
"""

from __future__ import annotations

PRIORITIES = ("high", "normal", "low")

_RANK = {name: rank for rank, name in enumerate(PRIORITIES)}

DEFAULT_PRIORITY = "normal"


def is_valid_priority(name: str) -> bool:
    return name in _RANK


def rank(name: str) -> int:
    """Numeric rank for a priority name (lower runs first)."""
    return _RANK[name]


def sort_key(job) -> tuple:
    """Ordering key used by the queue: (priority rank, submission time, id).

    The id tiebreak keeps the ordering total and deterministic even for jobs
    created within the same clock tick.
    """
    return (_RANK[job.priority], job.created_at, job.id)
