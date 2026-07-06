"""Poison-job bookkeeping.

A job that keeps failing across attempts is "poisoned": running it again
would only burn worker time. :class:`Quarantine` counts failures per job id
and, once a job crosses the threshold, lets operators record a single
``quarantined`` event in the event log for the audit trail. All bookkeeping
is guarded by one lock, since every update is a check-then-write.
"""

from __future__ import annotations

import threading

from taskqueue.core.job import Job
from taskqueue.storage.events import EventLog

#: Failures before a job is considered poisoned, unless overridden.
DEFAULT_THRESHOLD = 3


class Quarantine:
    """Thread-safe failure counting with idempotent quarantine events.

    The failure counter and the recorded-set are both read-modify-write
    structures, so every method that touches them holds ``self._lock`` for
    the full check-then-update sequence — releasing between the check and
    the update would let two threads double-count a failure or write the
    ``quarantined`` event twice.
    """

    def __init__(self, events: EventLog, threshold: int = DEFAULT_THRESHOLD):
        if threshold < 1:
            raise ValueError(f"threshold must be at least 1, got {threshold}")
        self._events = events
        self._threshold = threshold
        self._lock = threading.Lock()
        self._failures: dict[str, int] = {}
        self._recorded: set[str] = set()

    def note_failure(self, job: Job) -> None:
        """Count one failed attempt for *job*.

        The read of the current count and the write of the incremented one
        happen under the lock as a single unit, so concurrent callers can
        never lose an increment.
        """
        with self._lock:
            self._failures[job.id] = self._failures.get(job.id, 0) + 1

    def failure_count(self, job_id: str) -> int:
        """How many failures have been noted for *job_id* (0 if none)."""
        with self._lock:
            return self._failures.get(job_id, 0)

    def is_poisoned(self, job_id: str) -> bool:
        """True once *job_id* has failed at least ``threshold`` times."""
        with self._lock:
            return self._failures.get(job_id, 0) >= self._threshold

    def poisoned(self) -> list[str]:
        """Every poisoned job id, sorted for stable presentation."""
        with self._lock:
            return sorted(
                job_id
                for job_id, count in self._failures.items()
                if count >= self._threshold
            )

    def record(self, job: Job) -> None:
        """Append one ``quarantined`` event for *job*, exactly once.

        Repeat calls for the same job id are no-ops. The membership check,
        the event append, and the seen-set insertion all happen under the
        lock: holding it across the (short, local-file) append is the
        deliberately conservative choice, because it is the only way two
        concurrent first calls cannot both pass the check and double-write.
        The id is added to the seen set only after the append succeeds, so
        a failed write (e.g. a full disk) leaves the call retryable rather
        than silently swallowing the event forever.
        """
        with self._lock:
            if job.id in self._recorded:
                return
            self._events.append_event(
                job.id,
                "quarantined",
                failures=self._failures.get(job.id, 0),
                threshold=self._threshold,
            )
            self._recorded.add(job.id)

    def forget(self, job_id: str) -> None:
        """Drop all bookkeeping for *job_id* (e.g. after a manual requeue).

        A forgotten job starts from zero failures, and a later
        :meth:`record` for it will write a fresh event.
        """
        with self._lock:
            self._failures.pop(job_id, None)
            self._recorded.discard(job_id)
