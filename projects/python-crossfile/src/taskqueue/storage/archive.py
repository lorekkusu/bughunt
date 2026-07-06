"""Archival of terminal jobs.

Long-running deployments accumulate DONE and CANCELLED jobs that will never
change again; this module moves them out of the live store into an append-only
JSONL archive so the store stays small. FAILED jobs are deliberately *not*
archived — they may be re-queued for retry and, once out of retries, operators
want them visible in the store for inspection, not buried in the archive.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from taskqueue.core import timing
from taskqueue.core.errors import JobNotFound
from taskqueue.core.job import Job, JobState
from taskqueue.storage.jsonl import append_record, read_records
from taskqueue.storage.store import Store

#: States whose jobs are eligible for archival. FAILED is excluded on purpose
#: (see the module docstring); it is not terminal in the state machine anyway,
#: since a FAILED job may transition back to QUEUED.
ARCHIVABLE_STATES: tuple[JobState, ...] = (JobState.DONE, JobState.CANCELLED)


def _job_record(job: Job, archived_at: float) -> dict:
    """Serialize *job* into a plain-JSON archive record.

    Fields are listed explicitly (rather than via ``dataclasses.asdict``) so
    the archive schema is deliberate: enums are written by ``.value`` and the
    ``tags`` tuple becomes a JSON list. ``archived_at`` records when the job
    left the live store.
    """
    return {
        "id": job.id,
        "name": job.name,
        "state": job.state.value,
        "priority": job.priority,
        "owner": job.owner,
        "tags": list(job.tags),
        "payload": job.payload,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "lease_deadline": job.lease_deadline,
        "not_before": job.not_before,
        "last_error": job.last_error,
        "archived_at": archived_at,
    }


def archive_terminal(
    store: Store,
    path: str | Path,
    older_than_s: float,
    now: Optional[float] = None,
) -> int:
    """Archive DONE/CANCELLED jobs older than *older_than_s* seconds.

    A job qualifies when its ``finished_at`` timestamp is strictly earlier
    than ``now - older_than_s``. Jobs whose ``finished_at`` is ``None`` (for
    example a job cancelled straight out of QUEUED that never got a finish
    timestamp) are skipped: without a finish time their age is unknowable.

    Each qualifying job is appended to the JSONL archive at *path* first and
    then removed from *store*. Append-then-delete means a crash between the
    two steps can leave a duplicate archive record on the next run — callers
    that care can dedupe with :func:`archived_ids`. Returns the number of
    jobs archived.
    """
    current = now if now is not None else timing.now()
    cutoff = current - older_than_s

    candidates: list[Job] = []
    for state in ARCHIVABLE_STATES:
        candidates.extend(store.list_jobs(state))
    # list_jobs sorts per state; re-sort so the archive is globally ordered.
    candidates.sort(key=lambda job: job.created_at)

    archived = 0
    for job in candidates:
        if job.finished_at is None:
            continue
        if job.finished_at >= cutoff:
            continue
        append_record(path, _job_record(job, archived_at=current))
        try:
            store.delete(job.id)
        except JobNotFound:
            # Deleted concurrently after we snapshotted the listing; the
            # archive record is already written, so still count the job.
            pass
        archived += 1
    return archived


def load_archive(path: str | Path) -> list[dict]:
    """Read every archived record at *path*, oldest first.

    Returns an empty list when the archive file does not exist yet.
    """
    return read_records(path)


def archived_ids(path: str | Path) -> set[str]:
    """The set of job ids present in the archive at *path*.

    Records without an ``id`` field (which :func:`archive_terminal` never
    writes, but a hand-edited file might contain) are ignored rather than
    contributing a bogus ``None`` entry.
    """
    ids: set[str] = set()
    for record in read_records(path):
        job_id = record.get("id")
        if isinstance(job_id, str):
            ids.add(job_id)
    return ids
