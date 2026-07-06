"""Event-log compaction.

The event log grows without bound: every lifecycle change appends a line.
For most tooling only the most recent event(s) per job matter, so this module
rewrites the JSONL file keeping the last *N* events for each ``job_id`` while
preserving the overall file order. The rewrite goes through
:func:`taskqueue.storage.fs.atomic_write_text`, so readers never observe a
half-written log.
"""

from __future__ import annotations

import json
from pathlib import Path

from taskqueue.storage.fs import atomic_write_text
from taskqueue.storage.jsonl import count_records, read_records


def _kept_records(records: list[dict], keep_last: int) -> list[dict]:
    """Return the records that survive compaction, in original order.

    A record survives when it is among the last *keep_last* records sharing
    its ``job_id``. Records missing a ``job_id`` field group together under
    the ``None`` key, so malformed lines are compacted rather than dropped.
    """
    totals: dict[object, int] = {}
    for record in records:
        key = record.get("job_id")
        totals[key] = totals.get(key, 0) + 1

    kept: list[dict] = []
    seen: dict[object, int] = {}
    for record in records:
        key = record.get("job_id")
        position = seen.get(key, 0)  # zero-based occurrence index for this key
        seen[key] = position + 1
        if position >= totals[key] - keep_last:
            kept.append(record)
    return kept


def compact(events_path: str | Path, keep_last: int = 1) -> tuple[int, int]:
    """Compact the JSONL log at *events_path* in place.

    Keeps only the last *keep_last* events per ``job_id`` (order preserved
    overall) and returns ``(records_before, records_after)``. A missing or
    empty file is a no-op returning ``(0, 0)``. When compaction would remove
    nothing, the file is left untouched to avoid pointless churn. *keep_last*
    must be at least 1 — dropping every event for a job would erase its
    history entirely, which is never what compaction means.
    """
    if keep_last < 1:
        raise ValueError(f"keep_last must be >= 1, got {keep_last}")

    records = read_records(events_path)
    before = len(records)
    if before == 0:
        return 0, 0

    kept = _kept_records(records, keep_last)
    after = len(kept)
    if after == before:
        return before, after

    lines = [json.dumps(record, separators=(",", ":")) for record in kept]
    atomic_write_text(events_path, "\n".join(lines) + "\n")
    return before, after


def estimate_savings(path: str | Path, keep_last: int = 1) -> int:
    """How many records :func:`compact` would remove, without writing.

    Zero for a missing or empty file. Useful for logging a dry-run figure
    before scheduling a real compaction pass.
    """
    if keep_last < 1:
        raise ValueError(f"keep_last must be >= 1, got {keep_last}")
    records = read_records(path)
    if not records:
        return 0
    return len(records) - len(_kept_records(records, keep_last))


def should_compact(path: str | Path, max_records: int) -> bool:
    """True when the log at *path* has grown past *max_records* records.

    This is the cheap predicate maintenance loops poll: it only counts
    records, it does not compute per-job savings. A missing file counts as
    zero records and therefore never triggers compaction.
    """
    return count_records(path) > max_records
