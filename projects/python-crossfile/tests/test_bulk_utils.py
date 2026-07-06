import pytest

from taskqueue.api.pagination import paginate
from taskqueue.api.queryfilters import apply_filters, parse_filters
from taskqueue.core import naming, payloads, tags
from taskqueue.core.errors import ValidationError
from taskqueue.core.job import Job, JobState
from taskqueue.storage.events import EventLog
from taskqueue.workers.quarantine import Quarantine


# ------------------------------------------------------------------ core.tags

def test_normalize_strips_lowers_and_dedupes():
    assert tags.normalize(("Web", "web", " db ", "", "  ")) == ("web", "db")


def test_matches_is_case_insensitive_and_empty_required_matches_all():
    assert tags.matches(["Web", "DB"], ["web"]) is True
    assert tags.matches(["web"], ["db"]) is False
    assert tags.matches([], []) is True


# ------------------------------------------------------------- api.pagination

def test_paginate_clamps_limit_and_offset():
    page = paginate(list(range(10)), limit=999, offset=-5, max_limit=4)
    assert page.limit == 4 and page.offset == 0
    assert page.items == [0, 1, 2, 3]
    assert paginate([1, 2, 3], limit=0, offset=0).limit == 1


def test_paginate_exact_windows_and_has_more():
    items = list(range(6))
    first = paginate(items, limit=3, offset=0)
    assert first.items == [0, 1, 2] and first.has_more() is True
    last = paginate(items, limit=3, offset=3)
    assert last.items == [3, 4, 5] and last.has_more() is False
    past = paginate(items, limit=3, offset=6)
    assert past.items == [] and past.has_more() is False and past.total == 6


# --------------------------------------------------------------- core.naming

def test_naming_split_namespace_action():
    assert naming.split("reports.daily_rollup") == ("reports", "daily_rollup")
    assert naming.namespace("batch.export.retry") == "batch"
    assert naming.action("reports") is None
    assert naming.action("reports.daily_rollup") == "daily_rollup"


def test_naming_validity_and_patterns():
    assert naming.is_valid("reports.daily_rollup") is True
    assert naming.is_valid("Bad.Name") is False
    assert naming.matches_pattern("batch.x", "batch.x") is True
    assert naming.matches_pattern("batch.x.y", "batch.*") is True
    assert naming.matches_pattern("batch", "batch.*") is False
    assert naming.matches_pattern("batchx.y", "batch.*") is False


# ------------------------------------------------------------- core.payloads

def test_redact_masks_sensitive_keys_without_mutating_input():
    payload = {"api_key": "s3cr3t", "nested": {"password": "pw", "n": 1}, "ok": [1]}
    redacted = payloads.redact(payload)
    assert redacted == {"api_key": "***", "nested": {"password": "***", "n": 1}, "ok": [1]}
    assert payload["api_key"] == "s3cr3t"
    assert payload["nested"]["password"] == "pw"
    assert redacted["nested"] is not payload["nested"]
    assert redacted["ok"] is not payload["ok"]


# ------------------------------------------------------------ api.queryfilters

def test_parse_filters_normalizes_valid_input():
    parsed = parse_filters(
        {"state": "queued", "owner": " ops ", "tag": " Web ", "since": "1.5", "until": 9}
    )
    assert parsed == {
        "state": JobState.QUEUED,
        "owner": "ops",
        "tag": "web",
        "since": 1.5,
        "until": 9.0,
    }
    assert parse_filters({"limit": 10}) == {}


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({"state": "sleeping"}, "state"),
        ({"owner": "   "}, "owner"),
        ({"owner": 7}, "owner"),
        ({"tag": "  "}, "tag"),
        ({"tag": 3}, "tag"),
        ({"since": "soon"}, "since"),
        ({"until": None}, "until"),
        ({"since": 10.0, "until": 5.0}, "since"),
    ],
)
def test_parse_filters_rejects_bad_fields(params, field):
    with pytest.raises(ValidationError) as excinfo:
        parse_filters(params)
    assert excinfo.value.field == field


def test_apply_filters_is_conjunctive():
    early = Job(name="batch.a", owner="ops", tags=("web",))
    early.created_at = 100.0
    late = Job(name="batch.b", owner="ops", tags=("web",))
    late.created_at = 200.0
    other = Job(name="batch.c", owner="qa", tags=("db",))
    other.created_at = 150.0
    jobs = [early, late, other]
    filters = parse_filters({"owner": "ops", "tag": "WEB", "since": 100, "until": 150})
    assert apply_filters(jobs, filters) == [early]
    assert apply_filters(jobs, {}) == jobs


# --------------------------------------------------------- workers.quarantine

def test_quarantine_counts_failures_up_to_threshold(tmp_path):
    quarantine = Quarantine(EventLog(tmp_path / "events.jsonl"), threshold=2)
    job = Job(name="batch.flaky")
    assert quarantine.is_poisoned(job.id) is False
    quarantine.note_failure(job)
    assert quarantine.is_poisoned(job.id) is False
    quarantine.note_failure(job)
    assert quarantine.is_poisoned(job.id) is True
    assert quarantine.poisoned() == [job.id]
    assert quarantine.failure_count(job.id) == 2


def test_quarantine_record_appends_exactly_once(tmp_path):
    events = EventLog(tmp_path / "events.jsonl")
    quarantine = Quarantine(events, threshold=1)
    job = Job(name="batch.poison")
    quarantine.note_failure(job)
    quarantine.record(job)
    quarantine.record(job)
    written = list(events.iter_events(job.id))
    assert len(written) == 1
    assert written[0]["kind"] == "quarantined"
    assert written[0]["failures"] == 1
