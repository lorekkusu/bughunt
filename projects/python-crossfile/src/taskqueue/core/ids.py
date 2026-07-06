"""Job id generation and validation."""

import re
import uuid

_ID_RE = re.compile(r"^job-[0-9a-f]{12}$")


def new_job_id() -> str:
    """Return a fresh, globally unique job id (``job-`` + 12 hex chars)."""
    return "job-" + uuid.uuid4().hex[:12]


def is_valid_id(job_id: str) -> bool:
    """True if *job_id* looks like an id produced by :func:`new_job_id`."""
    return isinstance(job_id, str) and bool(_ID_RE.match(job_id))
