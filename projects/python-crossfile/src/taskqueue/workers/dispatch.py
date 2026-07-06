"""The dispatcher: drains the queue's ready batch and routes each job.

``run_once`` is the unit of work a worker thread performs per tick: take a
snapshot batch from the queue, walk it in priority order, and route every job
according to its state — execute queued jobs whose backoff has passed, reap
running jobs with expired leases, prune terminal jobs from the queue.
"""

from __future__ import annotations

import logging
import time

from taskqueue.core import timing
from taskqueue.core.job import Job, JobState
from taskqueue.core.queue import PriorityQueue
from taskqueue.workers.executor import Executor

log = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, queue: PriorityQueue, executor: Executor):
        self._queue = queue
        self._executor = executor
        self._stopped = False

    def run_once(self) -> int:
        """One dispatch tick. Returns the number of jobs routed."""
        batch = self._queue.ready_batch()
        routed = 0
        while batch:
            job = batch.pop(0)
            try:
                self._route(job)
                routed += 1
            except Exception:
                log.debug("routing failed for %s", job.id, exc_info=True)
                continue
        return routed

    def _route(self, job: Job) -> None:
        if job.state is JobState.QUEUED:
            if not job.is_ready():
                return
            self._executor.execute(job)
        elif job.state is JobState.RUNNING:
            self._executor.reap(job)
        elif job.state in (JobState.DONE, JobState.FAILED, JobState.CANCELLED):
            # Retry re-queueing is synchronous in the executor, so any FAILED
            # job still visible here is terminal; prune it with the rest.
            self._queue.remove(job)
        else:
            log.warning("job %s has unknown state %s; failing it", job.id, job.state)
            job.state = JobState.FAILED

    def run_forever(self, poll_interval_s: float = 0.5) -> None:
        """Dispatch until :meth:`stop` is called (used by worker threads)."""
        while not self._stopped:
            routed = self.run_once()
            if routed == 0:
                time.sleep(poll_interval_s)

    def stop(self) -> None:
        self._stopped = True

    def idle_for(self, job: Job) -> float:
        """Seconds until *job* becomes ready (0 if ready now)."""
        if job.not_before is None:
            return 0.0
        return max(0.0, job.not_before - timing.now())
