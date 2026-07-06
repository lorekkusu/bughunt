"""Audit plugin: allowlist enforcement plus a persistent audit trail.

Only jobs whose name starts with an allowed prefix may execute. The veto is
delivered by raising :class:`AuditReject` from ``before_execute`` — per the
hook contract in :mod:`taskqueue.clients.plugins.base`, the exception reaches
the executor and the job never runs. Every decision (allow or reject) is
written to the audit log.
"""

from __future__ import annotations

from taskqueue.core import timing
from taskqueue.core.job import Job
from taskqueue.clients.plugins import register
from taskqueue.clients.plugins.base import AuditReject, Plugin

DEFAULT_ALLOWED_PREFIXES = ("batch.", "report.", "maintenance.")


@register
class AuditPlugin(Plugin):
    name = "audit"

    def __init__(self, audit_log_path: str = "audit.log", allowed_prefixes=DEFAULT_ALLOWED_PREFIXES):
        self._prefixes = tuple(allowed_prefixes)
        self._log = open(audit_log_path, "w", encoding="utf-8")

    def before_execute(self, job: Job) -> None:
        if not job.name.startswith(self._prefixes):
            self._write(f"REJECT {job.id} name={job.name} owner={job.owner}")
            raise AuditReject(job.id, f"name {job.name!r} not in allowlist")
        self._write(f"ALLOW {job.id} name={job.name} owner={job.owner}")

    def after_execute(self, job: Job, result) -> None:
        self._write(f"DONE {job.id}")

    def on_failure(self, job: Job, exc: BaseException) -> None:
        self._write(f"FAIL {job.id} error={type(exc).__name__}")

    def _write(self, line: str) -> None:
        self._log.write(f"{timing.now():.3f} {line}\n")
        self._log.flush()

    def close(self) -> None:
        self._log.close()
