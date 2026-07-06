"""Plugin base class and the host that runs plugin hooks around execution.

Hook contract
-------------
Hooks run synchronously in the worker, in registration order, and are
isolated from one another: a hook that raises is logged and skipped, the
remaining hooks still run, and the job's own execution is unaffected. A
misbehaving plugin must never take down a worker.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from taskqueue.core.job import Job

log = logging.getLogger(__name__)


class PluginError(Exception):
    """Base class for plugin-raised errors."""


class AuditReject(PluginError):
    """Raised by a policy plugin's ``before_execute`` to veto a job."""

    def __init__(self, job_id: str, reason: str):
        super().__init__(f"job {job_id} rejected: {reason}")
        self.job_id = job_id
        self.reason = reason


class Plugin:
    """Base class for plugins. Subclasses override any subset of the hooks."""

    #: Registry name; subclasses must override.
    name = "plugin"

    def before_execute(self, job: Job) -> None:
        """Runs before the job handler."""

    def after_execute(self, job: Job, result: Any) -> None:
        """Runs after the handler returns."""

    def on_failure(self, job: Job, exc: BaseException) -> None:
        """Runs when the handler raises."""


class PluginHost:
    """Runs the registered plugins' hooks around a job execution."""

    def __init__(self, plugins: list[Plugin]):
        self._plugins = list(plugins)

    def _run_hooks(self, hook: str, job: Job, *args: Any) -> None:
        """Invoke *hook* on every plugin, in order.

        Hook failures are isolated: an exception from one plugin is logged
        and the remaining hooks still run.
        """
        for plugin in self._plugins:
            try:
                getattr(plugin, hook)(job, *args)
            except Exception:
                log.exception(
                    "plugin %s failed in %s for job %s", plugin.name, hook, job.id
                )

    def run_job(self, job: Job, handler: Callable[[Job], Any]) -> Any:
        """Execute *job* via *handler*, bracketed by the plugin hooks."""
        self._run_hooks("before_execute", job)
        try:
            result = handler(job)
        except Exception as exc:
            log.error("job %s (%s) handler raised %s", job.id, job.name, type(exc).__name__)
            self._run_hooks("on_failure", job, exc)
            raise
        self._run_hooks("after_execute", job, result)
        return result

    def plugin_names(self) -> list[str]:
        return [plugin.name for plugin in self._plugins]
