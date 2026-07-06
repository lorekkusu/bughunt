"""Generic JSONL file helpers.

One JSON object per line, UTF-8. These functions back ad-hoc tooling
(inspection scripts, snapshot manifests) rather than the hot path; they favor
simplicity over streaming performance. A missing file is treated as an empty
log, and blank lines are ignored on read.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_records(path: str | Path) -> list[dict]:
    """Read every record in *path*, oldest first.

    Returns an empty list if the file does not exist. Blank lines are
    skipped; malformed JSON raises ``json.JSONDecodeError``.
    """
    file = Path(path)
    if not file.exists():
        return []
    records: list[dict] = []
    with file.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def append_record(path: str | Path, record: dict[str, Any]) -> None:
    """Append one *record* to *path* as a single JSON line.

    Creates the file if it does not exist.
    """
    with Path(path).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, separators=(",", ":")) + "\n")


def tail(path: str | Path, n: int) -> list[dict]:
    """Return the last *n* records in *path*, oldest first.

    If *n* is zero or negative the result is empty; if *n* meets or exceeds
    the record count, every record is returned.
    """
    if n <= 0:
        return []
    records = read_records(path)
    return records[-n:]


def count_records(path: str | Path) -> int:
    """Number of records in *path* (zero if the file does not exist)."""
    return len(read_records(path))
