"""Metrics plugin: execution counters and duration observations.

Records to the process-wide :data:`taskqueue.core.metrics.registry`. Unlike
policy plugins (which raise from hooks to veto work — see the hook contract
in :mod:`taskqueue.clients.plugins.base`), metrics must never abort or fail a
job, so every hook swallows its own exceptions.
"""

from __future__ import annotations

import logging
from typing import Any

from taskqueue.core import timing
from taskqueue.core.job import Job
from taskqueue.core.metrics import registry
from taskqueue.clients.plugins import register
from taskqueue.clients.plugins.base import Plugin

log = logging.getLogger(__name__)


@register
class MetricsPlugin(Plugin):
    name = "metrics"

    def before_execute(self, job: Job) -> None:
        try:
            registry.incr("jobs.started")
        except Exception:
            log.debug("metrics before_execute hook failed", exc_info=True)

    def after_execute(self, job: Job, result: Any) -> None:
        try:
            registry.incr("jobs.done")
            if job.started_at is not None:
                registry.observe("jobs.duration_s", timing.now() - job.started_at)
        except Exception:
            log.debug("metrics after_execute hook failed", exc_info=True)

    def on_failure(self, job: Job, exc: BaseException) -> None:
        try:
            registry.incr("jobs.failed")
        except Exception:
            log.debug("metrics on_failure hook failed", exc_info=True)
