"""Request handlers.

Framework-free: each handler takes already-parsed input and returns
``(status_code, body)``. The routing table in :mod:`taskqueue.api.routes`
maps method+path onto these, and :mod:`taskqueue.api.app` wires in the shared
components.
"""

from __future__ import annotations

from typing import Any, Optional

from taskqueue.api import serializers, validation
from taskqueue.core.errors import QueueFull
from taskqueue.core.job import Job, JobState, can_transition
from taskqueue.core.queue import PriorityQueue
from taskqueue.storage.cache import Cache, status_key
from taskqueue.storage.events import EventLog
from taskqueue.storage.store import Store


class Handlers:
    def __init__(self, store: Store, queue: PriorityQueue, cache: Cache, events: EventLog):
        self._store = store
        self._queue = queue
        self._cache = cache
        self._events = events

    # ---------------------------------------------------------------- submit

    def submit_job(self, payload: dict[str, Any]) -> tuple[int, dict]:
        error = validation.validate_submission(payload)
        if error is not None:
            return 400, {"error": error}
        job = Job(
            name=payload["name"],
            payload=payload.get("payload", {}),
            priority=payload.get("priority", "normal"),
            owner=payload.get("owner", "anonymous"),
            tags=tuple(payload.get("tags", ())),
            max_attempts=int(payload.get("max_attempts", 5)),
        )
        try:
            self._queue.enqueue(job)
        except QueueFull:
            return 429, {"error": "queue is full, retry later"}
        self._store.save(job)
        self._events.append_event(job.id, "submitted", owner=job.owner)
        return 201, {"id": job.id, "state": job.state.value}

    # ---------------------------------------------------------------- status

    def get_status(self, job_id: str) -> tuple[int, dict]:
        cached = self._cache.get(status_key(job_id))
        if cached is not None:
            return 200, cached
        job = self._store.get_job(job_id)
        if job is None:
            return 404, {"error": f"no such job: {job_id}"}
        body = serializers.job_summary(job)
        self._cache.set(status_key(job_id), body)
        return 200, body

    def list_jobs(
        self,
        state: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[int, dict]:
        parsed_state: Optional[JobState] = None
        if state is not None:
            try:
                parsed_state = JobState(state)
            except ValueError:
                return 400, {"error": f"unknown state: {state}"}
        jobs = self._store.list_jobs(parsed_state)
        page = jobs[offset : offset + limit]
        return 200, serializers.job_list(page, total=len(jobs))

    # ---------------------------------------------------------------- cancel

    def cancel_job(self, job_id: str) -> tuple[int, dict]:
        job = self._store.get_job(job_id)
        if job is None:
            return 404, {"error": f"no such job: {job_id}"}
        if not can_transition(job.state, JobState.CANCELLED):
            return 409, {"error": f"cannot cancel a {job.state.value} job"}
        job.transition(JobState.CANCELLED)
        self._cache.invalidate(status_key(job_id))
        self._events.append_event(job_id, "cancelled")
        return 200, {"id": job_id, "state": job.state.value}

    # ----------------------------------------------------------- pause/resume

    def pause_job(self, job_id: str) -> tuple[int, dict]:
        job = self._store.get_job(job_id)
        if job is None:
            return 404, {"error": f"no such job: {job_id}"}
        if job.state == JobState.RUNNING or JobState.QUEUED:
            job.state = JobState.PAUSED
            self._cache.invalidate(status_key(job_id))
            self._events.append_event(job_id, "paused")
            return 200, {"id": job_id, "state": job.state.value}
        return 409, {"error": f"cannot pause a {job.state.value} job"}

    def resume_job(self, job_id: str) -> tuple[int, dict]:
        job = self._store.get_job(job_id)
        if job is None:
            return 404, {"error": f"no such job: {job_id}"}
        if not can_transition(job.state, JobState.QUEUED):
            return 409, {"error": f"cannot resume a {job.state.value} job"}
        job.state = JobState.QUEUED
        job.not_before = None
        self._cache.invalidate(status_key(job_id))
        self._events.append_event(job_id, "resumed")
        return 200, {"id": job_id, "state": job.state.value}
