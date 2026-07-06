"""Validation for job-submission payloads.

:func:`validate_submission` is the single gate the API's submit handler runs
before constructing a :class:`~taskqueue.core.job.Job`. It returns a
human-readable error message for the first problem found, or ``None`` when the
payload is acceptable — the handler turns a message into a 400 response.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from taskqueue.core.priority import PRIORITIES

#: Job names are dotted lowercase segments, e.g. ``reports.daily_rollup``.
_NAME_RE = re.compile(r"[a-z][a-z0-9_]*(\.[a-z0-9_]+)*")

#: Inclusive bounds for the ``max_attempts`` field.
MIN_ATTEMPTS = 1
MAX_ATTEMPTS = 20


def _is_non_empty_str(value: Any) -> bool:
    """True if *value* is a ``str`` with at least one non-whitespace char."""
    return isinstance(value, str) and bool(value.strip())


def _is_str_list(value: Any) -> bool:
    """True if *value* is a list/tuple whose items are all strings."""
    if not isinstance(value, (list, tuple)):
        return False
    return all(isinstance(item, str) for item in value)


def _is_bounded_int(value: Any, low: int, high: int) -> bool:
    """True if *value* is a real int (not a bool) within ``[low, high]``."""
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def validate_submission(payload: Any) -> Optional[str]:
    """Check a submission body; return an error message or ``None`` if valid."""
    if not isinstance(payload, dict):
        return "request body must be a JSON object"

    name = payload.get("name")
    if not _is_non_empty_str(name):
        return "'name' is required and must be a non-empty string"
    if _NAME_RE.fullmatch(name) is None:
        return "'name' must be dotted lowercase segments, e.g. 'reports.daily_rollup'"

    if "priority" in payload and payload["priority"] not in PRIORITIES:
        allowed = ", ".join(PRIORITIES)
        return f"'priority' must be one of: {allowed}"

    if "payload" in payload and not isinstance(payload["payload"], dict):
        return "'payload' must be an object"

    if "tags" in payload and not _is_str_list(payload["tags"]):
        return "'tags' must be a list of strings"

    if "max_attempts" in payload and not _is_bounded_int(
        payload["max_attempts"], MIN_ATTEMPTS, MAX_ATTEMPTS
    ):
        return f"'max_attempts' must be an integer between {MIN_ATTEMPTS} and {MAX_ATTEMPTS}"

    if "owner" in payload and not _is_non_empty_str(payload["owner"]):
        return "'owner' must be a non-empty string"

    return None
