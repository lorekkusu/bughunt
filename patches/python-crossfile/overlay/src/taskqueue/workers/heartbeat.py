"""Worker heartbeat tracking.

Each worker thread records a heartbeat every tick; the supervisor asks which
workers have gone stale (no heartbeat within ``STALE_AFTER_MS`` milliseconds)
and restarts them. All timestamps are integer epoch milliseconds.
"""

from __future__ import annotations

import threading
from typing import Optional

from taskqueue.core import timing

#: A worker is considered dead after this long without a heartbeat (ms).
STALE_AFTER_MS = 30_000


class HeartbeatMonitor:
    def __init__(self, stale_after_ms: int = STALE_AFTER_MS):
        self._stale_after_ms = stale_after_ms
        self._last_seen: dict[str, int] = {}
        self._lock = threading.Lock()

    def record(self, worker_id: str) -> None:
        """Note that *worker_id* is alive right now."""
        with self._lock:
            self._last_seen[worker_id] = timing.now_ms()

    def is_stale(self, worker_id: str, now_ms: Optional[int] = None) -> bool:
        """True if *worker_id* has not heartbeated within the staleness window."""
        current = now_ms if now_ms is not None else timing.now_ms()
        with self._lock:
            last = self._last_seen.get(worker_id)
        if last is None:
            return True
        return current - last > self._stale_after_ms

    def stale_workers(self) -> list[str]:
        with self._lock:
            known = list(self._last_seen)
        return [worker_id for worker_id in known if self.is_stale(worker_id)]

    def forget(self, worker_id: str) -> None:
        """Drop a worker (after it is restarted under a new id)."""
        with self._lock:
            self._last_seen.pop(worker_id, None)

    def known_workers(self) -> list[str]:
        with self._lock:
            return sorted(self._last_seen)
