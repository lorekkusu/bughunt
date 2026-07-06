"""The job model and its state machine.

A job's lifecycle:

    QUEUED -> RUNNING -> DONE
                      -> FAILED -> QUEUED (retry)
    QUEUED <-> PAUSED (operator hold)
    QUEUED / RUNNING  -> CANCELLED

Every state change must go through :meth:`Job.transition`, which consults the
``_TRANSITIONS`` table. Consumers that branch on ``JobState`` (dispatch,
serializers, …) are expected to handle every member of the enum.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Optional

from taskqueue.core import timing
from taskqueue.core.errors import InvalidTransition
from taskqueue.core.ids import new_job_id
from taskqueue.core.priority import DEFAULT_PRIORITY


class JobState(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


def is_active(state: JobState) -> bool:
    """True for states that still hold or may hold a worker's attention."""
    return state in (JobState.QUEUED, JobState.RUNNING, JobState.PAUSED)


def is_terminal(state: JobState) -> bool:
    """True for states a job can never leave (FAILED may be re-queued)."""
    return state in (JobState.DONE, JobState.CANCELLED)


# Allowed state transitions. A missing pair means the transition is forbidden.
_TRANSITIONS: dict[JobState, frozenset[JobState]] = {
    JobState.QUEUED: frozenset({JobState.RUNNING, JobState.CANCELLED}),
    JobState.RUNNING: frozenset({JobState.DONE, JobState.FAILED, JobState.CANCELLED}),
    JobState.DONE: frozenset(),
    JobState.FAILED: frozenset({JobState.QUEUED}),
    JobState.CANCELLED: frozenset(),
}


def can_transition(src: JobState, dst: JobState) -> bool:
    """True if the state machine allows moving from *src* to *dst*."""
    return dst in _TRANSITIONS[src]


@dataclass
class Job:
    """A unit of work owned by the queue.

    Timestamps (``created_at``, ``started_at``, ``finished_at``,
    ``lease_deadline``, ``not_before``) are wall-clock epoch seconds as
    returned by :func:`taskqueue.core.timing.now`.
    """

    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: str = DEFAULT_PRIORITY
    owner: str = "anonymous"
    tags: tuple[str, ...] = ()
    max_attempts: int = 5

    id: str = field(default_factory=new_job_id)
    state: JobState = JobState.QUEUED
    attempts: int = 0
    created_at: float = field(default_factory=timing.now)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    lease_deadline: Optional[float] = None
    not_before: Optional[float] = None
    last_error: Optional[str] = None

    def transition(self, dst: JobState) -> None:
        """Move to *dst*, or raise :class:`InvalidTransition`."""
        if not can_transition(self.state, dst):
            raise InvalidTransition(self.state.value, dst.value)
        self.state = dst

    def is_ready(self, now: Optional[float] = None) -> bool:
        """True if the job is queued and its backoff delay (if any) has passed."""
        if self.state is not JobState.QUEUED:
            return False
        if self.not_before is None:
            return True
        return (now if now is not None else timing.now()) >= self.not_before

    def retries_left(self) -> int:
        return max(0, self.max_attempts - self.attempts)
