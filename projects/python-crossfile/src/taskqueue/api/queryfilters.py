"""Declarative filters for job listings.

:func:`parse_filters` turns raw query parameters into a normalized filter
dict, raising :class:`~taskqueue.core.errors.ValidationError` (naming the
offending field) for anything malformed; :func:`apply_filters` then applies
every present filter conjunctively to a job sequence. Splitting parse from
apply keeps the 400-response mapping in the handler layer trivial.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from taskqueue.core.errors import ValidationError
from taskqueue.core.job import Job, JobState
from taskqueue.core.tags import normalize

#: Query keys this module understands. Anything else in ``params`` (paging
#: parameters, for instance) is ignored rather than rejected.
KNOWN_KEYS = frozenset({"state", "owner", "tag", "since", "until"})


def _parse_epoch(field: str, value: Any) -> float:
    """Coerce *value* to a finite float of epoch seconds, or raise."""
    if isinstance(value, bool):
        raise ValidationError(field, "must be a number (epoch seconds)")
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValidationError(field, "must be a number (epoch seconds)") from None
    if not math.isfinite(parsed):
        raise ValidationError(field, "must be a finite number")
    return parsed


def parse_filters(params: dict) -> dict:
    """Validate and normalize listing filters out of *params*.

    Recognized keys are all optional: ``state`` (a JobState value),
    ``owner`` (non-empty string, surrounding whitespace stripped), ``tag``
    (a single tag, normalized like every tag in taskqueue), and ``since``/
    ``until`` (epoch seconds, with ``since <= until`` enforced when both are
    given). Returns a dict containing only the filters that were present;
    raises :class:`ValidationError` naming the first offending field.
    """
    filters: dict[str, Any] = {}

    if "state" in params:
        try:
            filters["state"] = JobState(params["state"])
        except (TypeError, ValueError):
            allowed = ", ".join(state.value for state in JobState)
            raise ValidationError("state", f"must be one of: {allowed}") from None

    if "owner" in params:
        owner = params["owner"]
        if not isinstance(owner, str) or not owner.strip():
            raise ValidationError("owner", "must be a non-empty string")
        filters["owner"] = owner.strip()

    if "tag" in params:
        tag = params["tag"]
        if not isinstance(tag, str):
            raise ValidationError("tag", "must be a string")
        normalized = normalize([tag])
        if not normalized:
            raise ValidationError("tag", "must be a non-empty tag")
        filters["tag"] = normalized[0]

    if "since" in params:
        filters["since"] = _parse_epoch("since", params["since"])

    if "until" in params:
        filters["until"] = _parse_epoch("until", params["until"])

    if "since" in filters and "until" in filters and filters["since"] > filters["until"]:
        raise ValidationError("since", "must be <= 'until'")

    return filters


def apply_filters(jobs: Iterable[Job], filters: dict) -> list[Job]:
    """Return the jobs matching *every* filter present in *filters*.

    Semantics, per key: ``state`` matches by identity on ``job.state``;
    ``owner`` is exact string equality; ``tag`` requires membership in the
    job's normalized tags; ``since``/``until`` bound ``job.created_at``
    inclusively on both ends (``since <= created_at <= until``). An empty
    *filters* dict matches everything. Input order is preserved.
    """
    state = filters.get("state")
    owner = filters.get("owner")
    tag = filters.get("tag")
    since = filters.get("since")
    until = filters.get("until")

    matched: list[Job] = []
    for job in jobs:
        if state is not None and job.state is not state:
            continue
        if owner is not None and job.owner != owner:
            continue
        if tag is not None and tag not in normalize(job.tags):
            continue
        if since is not None and job.created_at < since:
            continue
        if until is not None and job.created_at > until:
            continue
        matched.append(job)
    return matched
