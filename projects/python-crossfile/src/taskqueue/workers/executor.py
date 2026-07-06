"""The executor: claims a job under a lease, runs its handler, records the
outcome, and schedules retries with exponential backoff.

Leases: a claimed job carries a ``lease_deadline`` (epoch seconds, set from
``timing.lease_deadline``). If the worker dies mid-run, the dispatcher's reap
pass notices the expired lease and re-queues the job.
"""

from __future__ import annotations

import logging
import random
from typing import Any, Callable, Optional

from taskqueue.core import timing
from taskqueue.core.config import Config
from taskqueue.core.job import Job, JobState
from taskqueue.storage.cache import Cache
from taskqueue.storage.events import EventLog
from taskqueue.storage.store import Store
from taskqueue.clients.plugins.base import PluginError, PluginHost

log = logging.getLogger(__name__)

Handler = Callable[[Job], Any]


class Executor:
    def __init__(
        self,
        store: Store,
        cache: Cache,
        events: EventLog,
        plugins: PluginHost,
        config: Config,
        handlers: Optional[dict[str, Handler]] = None,
    ):
        self._store = store
        self._cache = cache
        self._events = events
        self._plugins = plugins
        self._config = config
        self._handlers: dict[str, Handler] = dict(handlers or {})

    def register_handler(self, name: str, handler: Handler) -> None:
        self._handlers[name] = handler

    # ------------------------------------------------------------------ leases

    def claim(self, job: Job) -> None:
        """Take ownership of a queued job for one execution attempt."""
        job.transition(JobState.RUNNING)
        job.started_at = timing.now()
        job.lease_deadline = timing.lease_deadline(timing.now(), self._config.lease_ttl_s)
        self._events.append_event(job.id, "claimed")

    def _lease_expired(self, job: Job) -> bool:
        """True if the running job's lease has lapsed (worker presumed dead)."""
        if job.lease_deadline is None:
            return False
        return timing.now() > job.lease_deadline

    def reap(self, job: Job) -> bool:
        """Re-queue a running job whose lease expired. Returns True if reaped."""
        if not self._lease_expired(job):
            return False
        log.warning("lease expired for %s; re-queueing", job.id)
        job.state = JobState.QUEUED
        job.lease_deadline = None
        self._events.append_event(job.id, "lease_expired")
        return True

    # --------------------------------------------------------------- execution

    def execute(self, job: Job) -> None:
        """Run one attempt of *job*: claim, handler (with plugin hooks), record."""
        handler = self._handlers.get(job.name.split(".")[0])
        if handler is None:
            handler = self._handlers.get(job.name)
        if handler is None:
            job.last_error = f"no handler for {job.name!r}"
            job.transition(JobState.FAILED)
            self._events.append_event(job.id, "no_handler")
            return

        self.claim(job)
        try:
            self._plugins.run_job(job, handler)
        except PluginError as exc:
            # Policy rejections (audit veto, quota) are not retryable.
            job.last_error = str(exc)
            job.lease_deadline = None
            job.transition(JobState.FAILED)
            job.finished_at = timing.now()
            self._cache.invalidate(f"job:{job.id}")
            self._events.append_event(job.id, "rejected", error=job.last_error)
        except Exception as exc:
            self._handle_failure(job, exc)
        else:
            self._finish(job)

    def _finish(self, job: Job) -> None:
        job.transition(JobState.DONE)
        job.finished_at = timing.now()
        job.lease_deadline = None
        self._cache.invalidate(f"job:{job.id}")
        self._events.append_event(job.id, "done", duration=job.finished_at - job.started_at)

    def _handle_failure(self, job: Job, exc: BaseException) -> None:
        job.attempts += 1
        job.last_error = f"{type(exc).__name__}: {exc}"
        job.lease_deadline = None
        self._events.append_event(job.id, "attempt_failed", error=job.last_error)

        if job.attempts >= job.max_attempts:
            job.transition(JobState.FAILED)
            job.finished_at = timing.now()
            self._cache.invalidate(f"job:{job.id}")
            self._events.append_event(job.id, "failed", attempts=job.attempts)
            return

        # Exponential backoff with jitter, capped at retry_cap_s.
        delay = min(self._config.retry_base_s * (2 ** job.attempts), self._config.retry_cap_s)
        delay *= random.uniform(0.5, 1.5)
        job.transition(JobState.FAILED)
        job.transition(JobState.QUEUED)
        job.not_before = timing.now() + delay
        self._events.append_event(job.id, "retry_scheduled", delay=round(delay, 3))
