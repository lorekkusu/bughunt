"""Graceful drain: wait for in-flight work to settle before shutdown.

A drain is complete when the store shows no RUNNING jobs and the queue's
ready batch contains no QUEUED job that is ready to dispatch right now.
Stopping intake is the **caller's** responsibility: pause the API submit path
before calling :meth:`DrainCoordinator.drain`, otherwise fresh submissions
can extend the drain indefinitely.
"""

from __future__ import annotations

import logging
import time

from taskqueue.core import timing
from taskqueue.core.job import JobState
from taskqueue.core.queue import PriorityQueue
from taskqueue.storage.store import Store
from taskqueue.workers.pool import WorkerPool
from taskqueue.workers.signals import ShutdownFlag

log = logging.getLogger(__name__)

#: Default total drain budget, in seconds.
DEFAULT_TIMEOUT_S = 30.0

#: Default interval between pending-work checks, in seconds.
DEFAULT_POLL_S = 0.1


class DrainCoordinator:
    """Watches the store and queue until outstanding work has settled.

    The coordinator never mutates anything itself: it only observes the
    store's RUNNING count and the queue's ready batch, leaving the worker
    pool to finish (or reap) whatever is in flight. Jobs parked behind a
    retry backoff (``not_before`` in the future) are deliberately *not*
    treated as pending — they cannot be dispatched right now, and waiting
    out arbitrary backoff windows is not what a shutdown drain is for.
    """

    def __init__(self, queue: PriorityQueue, store: Store, pool: WorkerPool):
        self._queue = queue
        self._store = store
        self._pool = pool

    def pending_count(self) -> int:
        """Jobs still holding the drain open: RUNNING plus queued-and-ready.

        RUNNING jobs are counted from the store (the source of truth for job
        state); ready QUEUED jobs are counted from the queue's snapshot.
        ``Job.is_ready`` is False for RUNNING jobs, so nothing is counted
        twice even though the queue also holds running entries.
        """
        running = self._store.count(JobState.RUNNING)
        now = timing.now()
        ready = sum(1 for job in self._queue.ready_batch() if job.is_ready(now))
        return running + ready

    def drain(self, timeout_s: float = DEFAULT_TIMEOUT_S, poll_s: float = DEFAULT_POLL_S) -> bool:
        """Block until :meth:`pending_count` reaches zero or the budget lapses.

        Returns True if the system drained within *timeout_s*, False on
        timeout. The deadline is computed with ``time.monotonic`` so wall
        clock adjustments cannot stretch or shrink the budget, and the sleep
        between checks is capped at the remaining budget so the method never
        waits negative time nor meaningfully overshoots the deadline.
        """
        if poll_s <= 0:
            raise ValueError(f"poll_s must be positive, got {poll_s!r}")
        deadline = time.monotonic() + max(0.0, timeout_s)
        while True:
            if self.pending_count() == 0:
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0.0:
                return False
            time.sleep(min(poll_s, remaining))

    def shutdown(self, flag: ShutdownFlag, timeout_s: float = DEFAULT_TIMEOUT_S) -> bool:
        """Drain, stop the worker pool, then latch the shutdown flag.

        The ordering is deliberate: the drain runs first while the pool is
        still alive to finish in-flight jobs, the pool is stopped next so no
        new work starts, and the flag is latched last so supervisor-style
        loops observing it only exit once the workers are down. A timed-out
        drain is logged but does not abort the shutdown — the pool is
        stopped and the flag latched regardless.

        Returns whatever :meth:`drain` returned, so callers can distinguish
        a clean shutdown from one that abandoned pending work.
        """
        drained = self.drain(timeout_s=timeout_s)
        if not drained:
            log.warning(
                "drain timed out after %.1fs with %d job(s) still pending; stopping anyway",
                timeout_s,
                self.pending_count(),
            )
        self._pool.stop()
        flag.request()
        return drained
