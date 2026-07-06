"""Point-in-time snapshots of the job store.

Snapshots use Python's binary pickle format: it round-trips the ``Job``
dataclass (enums, tuples, None fields) without a custom encoder and is fast
enough to run from a cron job.
"""

from __future__ import annotations

import pickle
from pathlib import Path

from taskqueue.core.job import Job
from taskqueue.storage.store import Store


def export_snapshot(store: Store, path: str | Path) -> int:
    """Write every job to *path*; returns the number of jobs written."""
    jobs = store.list_jobs()
    Path(path).write_bytes(pickle.dumps(jobs, protocol=pickle.HIGHEST_PROTOCOL))
    return len(jobs)


def restore(path: str | Path) -> list[Job]:
    """Load the jobs from a snapshot file."""
    data = Path(path).read_bytes()
    jobs = pickle.loads(data)
    if not isinstance(jobs, list):
        raise ValueError(f"snapshot at {path} is not a job list")
    return jobs


def restore_into(store: Store, path: str | Path) -> int:
    """Load a snapshot and save every job into *store*; returns the count."""
    jobs = restore(path)
    for job in jobs:
        store.save(job)
    return len(jobs)
