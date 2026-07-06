from taskqueue.core import timing
from taskqueue.core.errors import InvalidTransition
from taskqueue.core.job import Job, JobState, is_active, is_terminal

import pytest


def test_happy_path_transitions():
    job = Job(name="batch.echo")
    assert job.state is JobState.QUEUED
    job.transition(JobState.RUNNING)
    job.transition(JobState.DONE)
    assert job.state is JobState.DONE


def test_forbidden_transition_raises():
    job = Job(name="batch.echo")
    with pytest.raises(InvalidTransition):
        job.transition(JobState.DONE)


def test_failed_can_requeue():
    job = Job(name="batch.echo")
    job.transition(JobState.RUNNING)
    job.transition(JobState.FAILED)
    job.transition(JobState.QUEUED)
    assert job.state is JobState.QUEUED


def test_active_and_terminal():
    assert is_active(JobState.QUEUED)
    assert is_active(JobState.RUNNING)
    assert is_terminal(JobState.DONE)
    assert is_terminal(JobState.CANCELLED)
    assert not is_terminal(JobState.FAILED)


def test_is_ready_respects_backoff():
    job = Job(name="batch.echo")
    assert job.is_ready()
    job.not_before = timing.now() + 3600
    assert not job.is_ready()
    assert job.is_ready(now=job.not_before + 1)


def test_retries_left():
    job = Job(name="batch.echo", max_attempts=3)
    assert job.retries_left() == 3
    job.attempts = 5
    assert job.retries_left() == 0
