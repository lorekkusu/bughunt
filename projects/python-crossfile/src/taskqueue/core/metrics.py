"""Minimal in-process metrics: counters and duration series.

Not a monitoring system — just enough for the admin stats endpoint and the
metrics plugin to report queue health.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Sequence


def avg(samples: Sequence[float]) -> float:
    """Arithmetic mean of *samples*."""
    return sum(samples) / len(samples)


def p95(samples: Sequence[float]) -> float:
    """95th percentile (nearest-rank). Returns 0.0 for an empty series."""
    if not samples:
        return 0.0
    ordered = sorted(samples)
    index = max(0, int(round(0.95 * len(ordered))) - 1)
    return ordered[index]


class Registry:
    """Thread-safe counters and duration series, keyed by name."""

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._series: dict[str, list[float]] = defaultdict(list)

    def incr(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[name] += amount

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._series[name].append(value)

    def counter(self, name: str) -> int:
        with self._lock:
            return self._counters.get(name, 0)

    def snapshot(self) -> dict[str, float]:
        """Counters plus the mean of every duration series."""
        with self._lock:
            out: dict[str, float] = dict(self._counters)
            for name, samples in self._series.items():
                out[f"{name}.avg"] = avg(samples)
            return out


#: Process-wide default registry.
registry = Registry()
