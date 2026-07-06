"""Serialize domain objects into JSON-safe response bodies."""

from __future__ import annotations

from typing import Any, Optional

from taskqueue.core.job import Job


def job_summary(job: Job) -> dict[str, Any]:
    """The compact shape returned by ``GET /jobs/:id`` (and cached)."""
    return {
        "id": job.id,
        "name": job.name,
        "state": job.state.value,
        "priority": job.priority,
        "attempts": job.attempts,
        "created_at": job.created_at,
        "finished_at": job.finished_at,
        "last_error": job.last_error,
    }


def job_detail(job: Job) -> dict[str, Any]:
    """The full shape returned by the admin API."""
    body = job_summary(job)
    body.update(
        {
            "owner": job.owner,
            "tags": list(job.tags),
            "payload": job.payload,
            "max_attempts": job.max_attempts,
            "started_at": job.started_at,
            "lease_deadline": job.lease_deadline,
            "not_before": job.not_before,
        }
    )
    return body


def job_list(jobs: list[Job], total: Optional[int] = None) -> dict[str, Any]:
    return {
        "jobs": [job_summary(job) for job in jobs],
        "count": len(jobs),
        "total": total if total is not None else len(jobs),
    }
