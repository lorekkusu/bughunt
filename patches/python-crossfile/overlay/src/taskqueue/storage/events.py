"""Append-only JSONL event log.

Every job lifecycle change is appended as one JSON object per line:

    {"ts": <epoch milliseconds>, "job_id": "...", "kind": "...", ...extra fields}

``ts`` is wall-clock epoch time in integer milliseconds — events are persisted
and read back across process restarts, so a monotonic clock would be
meaningless here. The file is the *only* coupling between writers (executor,
handlers) and readers (SDK timeline, inspector): whatever schema is written
here is what they parse.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Optional

from taskqueue.core import timing


class EventLog:
    def __init__(self, path: str | Path):
        self._path = Path(path)

    def append_event(self, job_id: str, kind: str, **extra: Any) -> dict:
        """Append one event and return the record that was written."""
        record = {"ts": timing.now_ms(), "job_id": job_id, "kind": kind}
        record.update(extra)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, separators=(",", ":")) + "\n")
        return record

    def iter_events(self, job_id: Optional[str] = None) -> Iterator[dict]:
        """Yield events oldest-first, optionally filtered to one job."""
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if job_id is None or record.get("job_id") == job_id:
                    yield record

    def events_since(self, cutoff_ts: float) -> list[dict]:
        """Events with ``ts`` at or after the epoch-ms *cutoff_ts*."""
        return [ev for ev in self.iter_events() if ev["ts"] >= cutoff_ts]

    def count(self) -> int:
        return sum(1 for _ in self.iter_events())
