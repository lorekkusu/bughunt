"""Read-only diagnostics over a running service's components.

Operators use the inspector to answer "what is the queue doing right now?"
without going through the API layer. Every method is a pure read: nothing
here mutates the store, queue, cache, or event log.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Optional

from taskqueue.core.job import JobState
from taskqueue.core.queue import PriorityQueue
from taskqueue.storage.cache import Cache, status_key
from taskqueue.storage.events import EventLog
from taskqueue.storage.store import Store


class Inspector:
    def __init__(self, store: Store, queue: PriorityQueue, cache: Cache, events: EventLog):
        self._store = store
        self._queue = queue
        self._cache = cache
        self._events = events

    def queue_snapshot(self) -> list[dict]:
        """Every queued entry in dispatch order, as plain dicts.

        ``ready_batch`` returns a fresh snapshot list, so iterating it here
        is safe regardless of concurrent dispatch activity.
        """
        return [
            {
                "id": job.id,
                "name": job.name,
                "priority": job.priority,
                "state": job.state.value,
                "not_before": job.not_before,
            }
            for job in self._queue.ready_batch()
        ]

    def cached_status(self, job_id: str) -> Optional[dict[str, Any]]:
        """The cached status summary for *job_id*, or None if absent/expired."""
        return self._cache.get(status_key(job_id))

    def recent_events(self, n: int = 50) -> list[dict]:
        """The last *n* events from the event log, oldest first."""
        tail: deque[dict] = deque(self._events.iter_events(), maxlen=n)
        return list(tail)

    def summary(self) -> dict:
        """Aggregate counts across the store, queue, and cache."""
        return {
            "jobs": {state.value: self._store.count(state) for state in JobState},
            "queue_depth": len(self._queue),
            "cache_entries": len(self._cache),
        }
