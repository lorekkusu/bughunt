"""Worker heartbeat tracking.

Each worker thread records a heartbeat every tick; the supervisor asks which
workers have gone stale (no heartbeat within ``STALE_AFTER_S`` seconds) and
restarts them. All timestamps are epoch seconds.
"""

from __future__ import annotations

import threading
import time
from typing import Optional

#: A worker is considered dead after this many seconds without a heartbeat.
STALE_AFTER_S = 30.0


class HeartbeatMonitor:
    def __init__(self, stale_after_s: float = STALE_AFTER_S):
        self._stale_after_s = stale_after_s
        self._last_seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def record(self, worker_id: str) -> None:
        """Note that *worker_id* is alive right now."""
        with self._lock:
            self._last_seen[worker_id] = time.time()

    def is_stale(self, worker_id: str, now: Optional[float] = None) -> bool:
        """True if *worker_id* has not heartbeated within the staleness window."""
        current = now if now is not None else time.time()
        with self._lock:
            last = self._last_seen.get(worker_id)
        if last is None:
            return True
        return current - last > self._stale_after_s

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
