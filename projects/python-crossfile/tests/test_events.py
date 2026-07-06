from taskqueue.storage.events import EventLog


def test_append_and_iter(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    log.append_event("job-aaaaaaaaaaaa", "submitted", owner="tests")
    log.append_event("job-bbbbbbbbbbbb", "submitted")
    log.append_event("job-aaaaaaaaaaaa", "done")

    everything = list(log.iter_events())
    assert [ev["kind"] for ev in everything] == ["submitted", "submitted", "done"]
    assert everything[0]["owner"] == "tests"

    mine = list(log.iter_events("job-aaaaaaaaaaaa"))
    assert [ev["kind"] for ev in mine] == ["submitted", "done"]


def test_timestamps_are_monotone_nondecreasing(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    for kind in ("a", "b", "c"):
        log.append_event("job-cccccccccccc", kind)
    stamps = [ev["ts"] for ev in log.iter_events()]
    assert stamps == sorted(stamps)


def test_events_since_uses_recorded_stamps(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    log.append_event("job-dddddddddddd", "first")
    second = log.append_event("job-dddddddddddd", "second")
    since = log.events_since(second["ts"])
    assert [ev["kind"] for ev in since] == ["second"]


def test_missing_file_is_empty(tmp_path):
    log = EventLog(tmp_path / "absent.jsonl")
    assert list(log.iter_events()) == []
    assert log.count() == 0
