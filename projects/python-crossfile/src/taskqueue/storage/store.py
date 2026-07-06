"""The job store — the single source of truth for job state.

In-memory, keyed by job id, guarded by an RLock. Lookups for ids that do not
exist raise :class:`JobNotFound`; callers that treat "missing" as a normal
outcome (the API layer's 404 mapping) catch it explicitly.
"""

from __future__ import annotations

import threading
from typing import Optional

from taskqueue.core.errors import InvalidTransition, JobNotFound
from taskqueue.core.job import Job, JobState, can_transition


class Store:
    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.RLock()

    def save(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.id] = job

    def get_job(self, job_id: str) -> Job:
        """Return the job with *job_id*, or raise :class:`JobNotFound`."""
        with self._lock:
            try:
                return self._jobs[job_id]
            except KeyError:
                raise JobNotFound(job_id) from None

    def exists(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self._jobs

    def update_state(self, job_id: str, new_state: JobState) -> Job:
        """Transition the stored job to *new_state* and return it."""
        with self._lock:
            job = self.get_job(job_id)
            if not can_transition(job.state, new_state):
                raise InvalidTransition(job.state.value, new_state.value)
            job.state = new_state
            return job

    def delete(self, job_id: str) -> None:
        with self._lock:
            if self._jobs.pop(job_id, None) is None:
                raise JobNotFound(job_id)

    def list_jobs(self, state: Optional[JobState] = None) -> list[Job]:
        with self._lock:
            jobs = list(self._jobs.values())
        if state is not None:
            jobs = [job for job in jobs if job.state is state]
        return sorted(jobs, key=lambda job: job.created_at)

    def count(self, state: Optional[JobState] = None) -> int:
        return len(self.list_jobs(state))
