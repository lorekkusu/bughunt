from taskqueue.core.errors import InvalidTransition, JobNotFound
from taskqueue.core.job import Job, JobState
from taskqueue.storage.store import Store

import pytest


def test_save_and_get_roundtrip():
    store = Store()
    job = Job(name="batch.echo")
    store.save(job)
    assert store.get_job(job.id) is job


def test_missing_job_raises():
    store = Store()
    with pytest.raises(JobNotFound):
        store.get_job("job-000000000000")


def test_update_state():
    store = Store()
    job = Job(name="batch.echo")
    store.save(job)
    updated = store.update_state(job.id, JobState.RUNNING)
    assert updated.state is JobState.RUNNING
    with pytest.raises(InvalidTransition):
        store.update_state(job.id, JobState.QUEUED)


def test_delete():
    store = Store()
    job = Job(name="batch.echo")
    store.save(job)
    store.delete(job.id)
    assert not store.exists(job.id)
    with pytest.raises(JobNotFound):
        store.delete(job.id)


def test_list_jobs_filters_and_sorts():
    store = Store()
    first = Job(name="batch.a")
    second = Job(name="batch.b")
    second.created_at = first.created_at + 1
    second.state = JobState.RUNNING
    store.save(second)
    store.save(first)
    assert [j.name for j in store.list_jobs()] == ["batch.a", "batch.b"]
    assert [j.name for j in store.list_jobs(JobState.RUNNING)] == ["batch.b"]
    assert store.count(JobState.RUNNING) == 1
