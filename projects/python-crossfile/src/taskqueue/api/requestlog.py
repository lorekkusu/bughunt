"""In-memory ring buffer of recent requests, for on-call debugging.

Keeps the last N request outcomes (method, path, status, duration, caller)
in a bounded deque so "what just happened?" is answerable without grepping
server logs. This is best-effort observability: the buffer is per-process,
lost on restart, and never persisted — production auditing belongs to the
audit log, not here.
"""

from __future__ import annotations

import threading
import time
from collections import deque

#: Default number of requests retained.
DEFAULT_CAPACITY = 256


class RequestLog:
    """Bounded, thread-safe log of recent request outcomes.

    On locking: a ``deque`` with ``maxlen`` makes individual appends safe on
    their own, and readers never need a read-then-append pair to be atomic.
    The lock exists for the *readers*: :meth:`snapshot` and
    :meth:`error_rate` copy the deque while request threads keep appending,
    and iterating a deque that is concurrently mutated raises
    ``RuntimeError``. Holding the lock for both writes and copies makes
    every read a consistent point-in-time view.
    """

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        if capacity < 1:
            raise ValueError(f"capacity must be >= 1, got {capacity}")
        self._entries: deque[dict] = deque(maxlen=capacity)
        self._lock = threading.Lock()

    # --------------------------------------------------------------- writing

    def record(
        self,
        method: str,
        path: str,
        status: int,
        duration_s: float,
        caller: str,
    ) -> None:
        """Append one request outcome, evicting the oldest at capacity."""
        entry = {
            "ts": time.time(),
            "method": method,
            "path": path,
            "status": status,
            "duration_s": duration_s,
            "caller": caller,
        }
        with self._lock:
            self._entries.append(entry)

    # --------------------------------------------------------------- reading

    def snapshot(self, n: int = 50) -> list[dict]:
        """The last *n* requests, newest first.

        Returns copies of the stored entries so callers can annotate or
        mutate them without corrupting the buffer. ``n`` of zero or less
        yields an empty list; ``n`` beyond the buffer size yields everything
        retained.
        """
        if n <= 0:
            return []
        with self._lock:
            recent = list(self._entries)[-n:]
        recent.reverse()
        return [dict(entry) for entry in recent]

    def error_rate(self, window: int = 100) -> float:
        """Fraction of the last *window* requests with status >= 500.

        Returns ``0.0`` when the buffer is empty or *window* is zero or
        negative — an idle service is not an erroring one, and the guard
        keeps the division well-defined.
        """
        if window <= 0:
            return 0.0
        with self._lock:
            recent = list(self._entries)[-window:]
        if not recent:
            return 0.0
        errors = sum(1 for entry in recent if entry["status"] >= 500)
        return errors / len(recent)

    def __len__(self) -> int:
        """Number of requests currently retained."""
        with self._lock:
            return len(self._entries)
