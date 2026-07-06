"""Read-only operational endpoints.

These handlers expose the service's internals — job counts, queue depths,
cache size, metrics, worker liveness — for dashboards and on-call debugging.
Nothing here mutates job state; the only write anywhere is the explicit
cache purge, which merely drops already-expired entries.
"""

from __future__ import annotations

import logging
from typing import Any

from taskqueue.core.job import JobState
from taskqueue.core.metrics import Registry
from taskqueue.core.queue import PriorityQueue
from taskqueue.storage.cache import Cache
from taskqueue.storage.store import Store
from taskqueue.workers.heartbeat import HeartbeatMonitor

log = logging.getLogger(__name__)


class AdminHandlers:
    def __init__(
        self,
        store: Store,
        queue: PriorityQueue,
        cache: Cache,
        heartbeats: HeartbeatMonitor,
        registry: Registry,
    ):
        self._store = store
        self._queue = queue
        self._cache = cache
        self._heartbeats = heartbeats
        self._registry = registry

    def stats(self) -> tuple[int, dict[str, Any]]:
        """A single snapshot of queue health for dashboards."""
        job_counts = {state.value: self._store.count(state) for state in JobState}
        body = {
            "jobs": {
                "by_state": job_counts,
                "total": self._store.count(),
            },
            "queue": {
                "depth": len(self._queue),
                "by_priority": self._queue.depth_by_priority(),
            },
            "cache_entries": len(self._cache),
            "metrics": self._registry.snapshot(),
        }
        return 200, body

    def workers(self) -> tuple[int, dict[str, Any]]:
        """Known workers split into alive and stale sets."""
        known = self._heartbeats.known_workers()
        stale = self._heartbeats.stale_workers()
        stale_set = set(stale)
        alive = [worker_id for worker_id in known if worker_id not in stale_set]
        body = {
            "known": known,
            "alive": alive,
            "stale": sorted(stale),
        }
        return 200, body

    def purge_cache(self) -> tuple[int, dict[str, Any]]:
        """Drop expired cache entries; report how many were removed."""
        purged = self._cache.purge_expired()
        if purged:
            log.info("purged %d expired cache entries", purged)
        return 200, {"purged": purged, "remaining": len(self._cache)}
