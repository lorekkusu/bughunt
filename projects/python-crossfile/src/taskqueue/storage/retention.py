"""Retention policy for the on-disk event log.

The event log grows without bound; maintenance tooling applies a
:class:`RetentionPolicy` to drop records older than a maximum age. Event
``ts`` fields are wall-clock epoch seconds (the schema documented in
:mod:`taskqueue.storage.events`), so "expired" is a simple timestamp
comparison against ``now - events_max_age_s``.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from taskqueue.storage.events import EventLog
from taskqueue.storage.fs import atomic_write_text
from taskqueue.storage.jsonl import read_records

#: Default maximum event age: seven days, in seconds.
DEFAULT_EVENTS_MAX_AGE_S = 7 * 24 * 3600.0


@dataclass(frozen=True)
class RetentionPolicy:
    """How long records are kept and how large archives may grow.

    ``events_max_age_s`` bounds the age of event-log records; ``apply``
    enforces it. ``archive_max_records`` is the record ceiling honored by
    the backup/archive tooling when it snapshots the log — it is carried on
    the policy so operators configure retention in one place.
    """

    events_max_age_s: float = DEFAULT_EVENTS_MAX_AGE_S
    archive_max_records: int = 100_000

    def __post_init__(self) -> None:
        if self.events_max_age_s < 0:
            raise ValueError(
                f"events_max_age_s must be >= 0, got {self.events_max_age_s!r}"
            )
        if self.archive_max_records < 0:
            raise ValueError(
                f"archive_max_records must be >= 0, got {self.archive_max_records!r}"
            )

    def cutoff_ts(self, now_s: float) -> float:
        """The epoch-seconds boundary: records with ``ts`` below it expire."""
        return now_s - self.events_max_age_s

    def expired_events(self, events: EventLog, now_s: float) -> int:
        """Count records in *events* older than the cutoff at *now_s*.

        A pure read — nothing is deleted. Records at exactly the cutoff are
        *not* expired, matching :meth:`apply`'s keep-side of the boundary.
        """
        cutoff = self.cutoff_ts(now_s)
        return sum(1 for record in events.iter_events() if _is_expired(record, cutoff))


def _is_expired(record: dict, cutoff: float) -> bool:
    """True if *record*'s ``ts`` is strictly before *cutoff*.

    Records with a missing or non-numeric ``ts`` are conservatively treated
    as fresh: retention must never destroy a record it cannot date.
    """
    ts = record.get("ts")
    if isinstance(ts, bool) or not isinstance(ts, (int, float)):
        return False
    return ts < cutoff


def apply(
    events_path: str | Path,
    policy: RetentionPolicy,
    now_s: Optional[float] = None,
) -> int:
    """Rewrite the JSONL at *events_path* keeping only fresh records.

    Returns how many records were dropped. The rewrite goes through a
    temp-file-plus-``os.replace`` cycle (via
    :func:`taskqueue.storage.fs.atomic_write_text`), so concurrent readers
    see either the old file or the new one, never a torn write. A missing
    file drops nothing and is not created; a file with nothing to drop is
    left untouched to avoid needless churn (and mtime changes).
    """
    path = Path(events_path)
    if not path.exists():
        return 0
    current = now_s if now_s is not None else time.time()
    cutoff = policy.cutoff_ts(current)

    records = read_records(path)
    kept = [record for record in records if not _is_expired(record, cutoff)]
    dropped = len(records) - len(kept)
    if dropped == 0:
        return 0

    text = "".join(json.dumps(record, separators=(",", ":")) + "\n" for record in kept)
    atomic_write_text(path, text)
    return dropped
