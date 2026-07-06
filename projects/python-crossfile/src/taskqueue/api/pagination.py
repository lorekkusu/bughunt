"""Offset/limit pagination over in-memory sequences.

:func:`paginate` clamps whatever the caller sends into safe bounds and slices
a window out of the full sequence; :func:`page_body` renders the standard
JSON shape. The slice ``items[offset : offset + limit]`` returns *limit*
items starting at index *offset* (fewer near the end, empty past the end) —
Python slicing never raises for out-of-range bounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

#: Hard ceiling on page size unless the caller overrides it.
DEFAULT_MAX_LIMIT = 200


@dataclass(frozen=True)
class Page:
    """One window of results plus the paging facts needed to fetch the next."""

    items: list[Any]
    limit: int
    offset: int
    total: int

    def has_more(self) -> bool:
        """True if items exist beyond this page."""
        return self.offset + len(self.items) < self.total


def paginate(
    items: Sequence[Any],
    limit: int,
    offset: int,
    max_limit: int = DEFAULT_MAX_LIMIT,
) -> Page:
    """Slice one page out of *items* with clamped ``limit``/``offset``.

    ``limit`` is clamped into ``[1, max_limit]`` and ``offset`` to ``>= 0``,
    so hostile or sloppy query parameters cannot request a negative or
    unbounded window.
    """
    ceiling = max(1, max_limit)
    clamped_limit = max(1, min(limit, ceiling))
    clamped_offset = max(0, offset)
    window = list(items[clamped_offset : clamped_offset + clamped_limit])
    return Page(
        items=window,
        limit=clamped_limit,
        offset=clamped_offset,
        total=len(items),
    )


def page_body(page: Page) -> dict[str, Any]:
    """Render *page* as the standard list-response body."""
    return {
        "items": list(page.items),
        "count": len(page.items),
        "limit": page.limit,
        "offset": page.offset,
        "total": page.total,
        "has_more": page.has_more(),
    }
