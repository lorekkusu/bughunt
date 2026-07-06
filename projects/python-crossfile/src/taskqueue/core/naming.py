"""Job-name structure helpers.

Job names are dotted paths of the form ``namespace.action[.qualifier...]``,
e.g. ``reports.daily_rollup`` or ``batch.export.retry``. This module offers
purely structural helpers — splitting, component access, validity, and
prefix-pattern matching — for routing tables, metrics labels, and tooling
that group jobs by namespace. Validation of *API input* remains the job of
:mod:`taskqueue.api.validation`; this module only mirrors its contract.
"""

from __future__ import annotations

import re
from typing import Optional

#: The job-name grammar: lowercase dotted segments, first segment starting
#: with a letter. Duplicated from ``taskqueue.api.validation._NAME_RE`` —
#: validation.py is the authority for what the API accepts; keep the two
#: patterns in lockstep if the grammar ever changes.
NAME_PATTERN = r"[a-z][a-z0-9_]*(\.[a-z0-9_]+)*"

_NAME_RE = re.compile(NAME_PATTERN)

#: Suffix that marks a prefix pattern in :func:`matches_pattern`.
WILDCARD_SUFFIX = ".*"


def split(name: str) -> tuple[str, ...]:
    """Split *name* into its dotted segments.

    Purely structural: no validity check is applied, so ``"a..b"`` yields
    ``("a", "", "b")``. The empty string yields the empty tuple rather than
    ``("",)``, so "no name" and "one empty segment" stay distinguishable.
    """
    if not name:
        return ()
    return tuple(name.split("."))


def namespace(name: str) -> str:
    """The first segment of *name* (its namespace).

    The empty string is returned for an empty name — callers grouping by
    namespace then bucket nameless input together instead of crashing.
    """
    segments = split(name)
    if not segments:
        return ""
    return segments[0]


def action(name: str) -> Optional[str]:
    """The second segment of *name*, or ``None`` when there is none.

    ``"reports.daily_rollup"`` -> ``"daily_rollup"``; a bare namespace like
    ``"reports"`` has no action.
    """
    segments = split(name)
    if len(segments) < 2:
        return None
    return segments[1]


def is_valid(name: str) -> bool:
    """True when *name* satisfies the job-name grammar.

    Uses the same pattern the API's submission validation enforces (see
    :data:`NAME_PATTERN`), so a name that passes here is accepted by
    ``validate_submission`` and vice versa.
    """
    return _NAME_RE.fullmatch(name) is not None


def matches_pattern(name: str, pattern: str) -> bool:
    """True when *name* matches *pattern*.

    Two forms are supported, and only two:

    - An exact pattern matches exactly itself: ``"batch.x"`` matches only
      ``"batch.x"``.
    - A pattern ending in ``".*"`` matches every name that extends the
      prefix by at least one segment: ``"batch.*"`` matches ``"batch.x"``
      and ``"batch.x.y"`` but not ``"batch"`` itself, not ``"batch."``, and
      not ``"batchx.y"`` (the boundary is the literal dot, not a string
      prefix).

    A wildcard anywhere but the tail (``"batch.*.x"``) is not a wildcard —
    such a pattern only matches itself, literally. The degenerate pattern
    ``".*"`` (an empty prefix) matches nothing.
    """
    if pattern.endswith(WILDCARD_SUFFIX):
        prefix = pattern[: -len(WILDCARD_SUFFIX)]
        if not prefix:
            return False
        return name.startswith(prefix + ".") and len(name) > len(prefix) + 1
    return name == pattern
