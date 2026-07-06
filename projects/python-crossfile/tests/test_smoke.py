"""End-to-end smoke: submit through the API, execute via dispatch, read back."""

from taskqueue.api.app import App
from taskqueue.clients.http import InMemoryTransport
from taskqueue.clients.sdk import Client
from taskqueue.core import timing
from taskqueue.core.config import Config
from taskqueue.core.job import JobState

import pytest


@pytest.fixture
def app(tmp_path):
    config = Config(
        events_path=str(tmp_path / "events.jsonl"),
        audit_log_path=str(tmp_path / "audit.log"),
        plugins="taskqueue.clients.plugins.audit,taskqueue.clients.plugins.metrics_hook",
    )
    application = App(config)
    application.executor.register_handler("batch", lambda job: {"echo": job.payload})
    return application


def _tick(app, times=2):
    # One tick executes ready jobs; a second prunes terminal jobs from the queue.
    for _ in range(times):
        app.dispatcher.run_once()


def test_submit_execute_status(app):
    status, body = app.handle("POST", "/jobs", {"name": "batch.echo", "payload": {"n": 1}})
    assert status == 201
    job_id = body["id"]

    _tick(app)

    status, body = app.handle("GET", f"/jobs/{job_id}")
    assert status == 200
    assert body["state"] == "done"
    assert len(app.queue) == 0


def test_unknown_job_is_404(app):
    status, body = app.handle("GET", "/jobs/job-000000000000")
    assert status == 404
    assert "error" in body


def test_invalid_submission_is_400(app):
    status, _ = app.handle("POST", "/jobs", {"name": ""})
    assert status == 400
    status, _ = app.handle("POST", "/jobs", {"name": "batch.echo", "priority": "urgent"})
    assert status == 400


def test_cancel_flow(app):
    _, body = app.handle("POST", "/jobs", {"name": "batch.later"})
    job_id = body["id"]
    status, body = app.handle("POST", f"/jobs/{job_id}/cancel")
    assert status == 200
    assert body["state"] == "cancelled"
    status, _ = app.handle("POST", f"/jobs/{job_id}/cancel")
    assert status == 409


def test_failure_schedules_retry(app):
    def boom(job):
        raise RuntimeError("handler exploded")

    app.executor.register_handler("report", boom)
    _, body = app.handle("POST", "/jobs", {"name": "report.weekly"})
    job = app.store.get_job(body["id"])

    app.dispatcher.run_once()

    assert job.state is JobState.QUEUED
    assert job.not_before is not None and job.not_before > timing.now()
    assert job.last_error is not None


def test_admin_stats(app):
    app.handle("POST", "/jobs", {"name": "batch.echo"})
    status, body = app.handle("GET", "/admin/stats")
    assert status == 200
    assert body["queue"]["depth"] == 1
    assert body["jobs"]["by_state"]["queued"] == 1


def test_rate_limit(tmp_path):
    config = Config(
        events_path=str(tmp_path / "events.jsonl"),
        audit_log_path=str(tmp_path / "audit.log"),
        rate_limit_per_minute=2,
    )
    application = App(config)
    assert application.handle("GET", "/jobs")[0] == 200
    assert application.handle("GET", "/jobs")[0] == 200
    assert application.handle("GET", "/jobs")[0] == 429


def test_sdk_roundtrip(app):
    client = Client(InMemoryTransport(app))
    job_id = client.submit("batch.echo", {"n": 2})

    _tick(app)

    assert client.status(job_id)["state"] == "done"
