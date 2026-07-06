"""Plugin base class and the host that runs plugin hooks around execution.

Hook contract
-------------
Hooks run synchronously in the worker, in registration order. **A hook may
raise to abort the job**: exceptions from ``before_execute`` propagate to the
executor and prevent the job from running at all — this is how policy plugins
(audit, quotas) veto work they reject. Exceptions from ``after_execute`` and
``on_failure`` propagate too, and fail the job.
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
        """Runs before the job handler. Raise to veto execution."""

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

        Hook exceptions propagate to the caller — see the module docstring:
        raising from ``before_execute`` is the documented veto mechanism.
        """
        for plugin in self._plugins:
            getattr(plugin, hook)(job, *args)

    def run_job(self, job: Job, runner: Callable[[Job], Any]) -> Any:
        """Execute *job* via *runner*, bracketed by the plugin hooks."""
        self._run_hooks("before_execute", job)
        try:
            result = runner(job)
        except Exception as exc:
            log.error("job %s handler raised %s", job.id, type(exc).__name__)
            self._run_hooks("on_failure", job, exc)
            raise
        self._run_hooks("after_execute", job, result)
        return result

    def plugin_names(self) -> list[str]:
        return [plugin.name for plugin in self._plugins]
