"""Tag utilities.

Tags are short, case-insensitive labels attached to jobs. All comparisons in
taskqueue happen on the *normalized* form (stripped, lowercased), so callers
should run user-supplied tags through :func:`normalize` before storing or
matching them.
"""

from __future__ import annotations

from typing import Iterable, Sequence


def normalize(tags: Iterable[str]) -> tuple[str, ...]:
    """Return *tags* stripped, lowercased, without empties or duplicates.

    Order of first occurrence is preserved, so ``("Web", "web", " db ")``
    normalizes to ``("web", "db")``.
    """
    seen: set[str] = set()
    result: list[str] = []
    for tag in tags:
        cleaned = tag.strip().lower()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return tuple(result)


def matches(job_tags: Sequence[str], required: Sequence[str]) -> bool:
    """True if every tag in *required* is present on the job.

    Both sides are normalized before comparison, so matching is
    case- and whitespace-insensitive. An empty *required* sequence
    matches every job.
    """
    have = set(normalize(job_tags))
    return all(tag in have for tag in normalize(required))


def parse_tag_expr(expr: str) -> list[str]:
    """Parse a comma-separated tag expression into normalized tags.

    Blank segments are dropped, so ``"web, ,DB,"`` parses to
    ``["web", "db"]``. An empty or whitespace-only *expr* yields ``[]``.
    """
    return list(normalize(expr.split(",")))
