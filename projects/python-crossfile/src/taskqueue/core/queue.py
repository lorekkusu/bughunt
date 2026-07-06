"""The in-memory priority queue.

Holds every non-pruned job the dispatcher may still need to look at. Ordering
is priority rank, then submission time (see :mod:`taskqueue.core.priority`).
Mutating operations take the queue lock; ``ready_batch`` hands callers an
independent snapshot they are free to consume.
"""

from __future__ import annotations

import threading
from typing import Optional

from taskqueue.core import priority
from taskqueue.core.errors import QueueFull
from taskqueue.core.job import Job

DEFAULT_MAX_SIZE = 10_000


class PriorityQueue:
    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        self._entries: list[Job] = []
        self._lock = threading.Lock()
        self._max_size = max_size

    def enqueue(self, job: Job) -> None:
        with self._lock:
            if len(self._entries) >= self._max_size:
                raise QueueFull(f"queue is at capacity ({self._max_size})")
            self._entries.append(job)

    def remove(self, job: Job) -> bool:
        """Drop *job* from the queue. Returns False if it was not present."""
        with self._lock:
            try:
                self._entries.remove(job)
            except ValueError:
                return False
            return True

    def find(self, job_id: str) -> Optional[Job]:
        with self._lock:
            for job in self._entries:
                if job.id == job_id:
                    return job
        return None

    def ready_batch(self) -> list[Job]:
        """Every entry, in dispatch order, as a fresh list.

        Returns a sorted copy: callers may pop from or otherwise consume the
        returned list without affecting the queue itself.
        """
        with self._lock:
            return sorted(self._entries, key=priority.sort_key)

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    def depth_by_priority(self) -> dict[str, int]:
        """Queue depth per priority level (for metrics/admin)."""
        with self._lock:
            depths = {name: 0 for name in priority.PRIORITIES}
            for job in self._entries:
                depths[job.priority] += 1
            return depths
