"""Webhook plugin: buffers outbound notifications for a delivery daemon.

Job outcomes are queued in memory as plain dicts; a separate delivery daemon
periodically calls :meth:`WebhookPlugin.drain` and ships them out. The buffer
is a bounded deque — when it fills, the *oldest* notifications are dropped.
That is a deliberate policy: a stalled delivery daemon must not grow memory
without bound, and recent outcomes are worth more than stale ones.

Like the metrics plugin, hooks here must never abort a job, so each hook
swallows its own exceptions.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from typing import Any

from taskqueue.core import timing
from taskqueue.core.job import Job
from taskqueue.clients.plugins import register
from taskqueue.clients.plugins.base import Plugin

log = logging.getLogger(__name__)


@register
class WebhookPlugin(Plugin):
    name = "webhook"

    def __init__(self, max_pending: int = 1000):
        self._pending: deque[dict] = deque(maxlen=max_pending)
        # drain() must read and clear as one step, and hooks append
        # concurrently from worker threads — the invariant spans two
        # operations, so both sides take the lock.
        self._lock = threading.Lock()

    def _enqueue(self, job_id: str, event: str) -> None:
        record = {"job_id": job_id, "event": event, "ts": timing.now()}
        with self._lock:
            self._pending.append(record)

    def after_execute(self, job: Job, result: Any) -> None:
        try:
            self._enqueue(job.id, "done")
        except Exception:
            log.debug("webhook after_execute hook failed", exc_info=True)

    def on_failure(self, job: Job, exc: BaseException) -> None:
        try:
            self._enqueue(job.id, "failed")
        except Exception:
            log.debug("webhook on_failure hook failed", exc_info=True)

    def drain(self) -> list[dict]:
        """Return all pending notifications and clear the buffer atomically."""
        with self._lock:
            drained = list(self._pending)
            self._pending.clear()
        return drained
