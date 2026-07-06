"""Declarative routing table for the API.

Each route is ``(method, path_pattern, handler_name)``. Patterns are literal
path segments with ``{param}`` placeholders; :func:`match` compares segment by
segment and captures placeholder values. The app looks the handler name up on
its handler objects; unmatched requests are the app's 404 case.
"""

from __future__ import annotations

from typing import Optional

#: The full route table, checked in order.
ROUTES: tuple[tuple[str, str, str], ...] = (
    ("POST", "/jobs", "submit_job"),
    ("GET", "/jobs", "list_jobs"),
    ("GET", "/jobs/{job_id}", "get_status"),
    ("POST", "/jobs/{job_id}/cancel", "cancel_job"),
    ("POST", "/jobs/{job_id}/pause", "pause_job"),
    ("POST", "/jobs/{job_id}/resume", "resume_job"),
    ("GET", "/admin/stats", "stats"),
    ("GET", "/admin/workers", "workers"),
    ("POST", "/admin/cache/purge", "purge_cache"),
)


def _segments(path: str) -> list[str]:
    """Split a path into segments, tolerating a leading/trailing slash."""
    trimmed = path.strip("/")
    if not trimmed:
        return []
    return trimmed.split("/")


def _match_segments(
    pattern_segments: list[str], path_segments: list[str]
) -> Optional[dict[str, str]]:
    """Match one pattern against a concrete path; return captured params."""
    if len(pattern_segments) != len(path_segments):
        return None
    params: dict[str, str] = {}
    for pattern_segment, path_segment in zip(pattern_segments, path_segments):
        if pattern_segment.startswith("{") and pattern_segment.endswith("}"):
            if not path_segment:
                return None
            params[pattern_segment[1:-1]] = path_segment
        elif pattern_segment != path_segment:
            return None
    return params


def match(method: str, path: str) -> Optional[tuple[str, dict[str, str]]]:
    """Resolve ``(method, path)`` to ``(handler_name, path_params)`` or None."""
    wanted_method = method.upper()
    path_segments = _segments(path)
    for route_method, pattern, handler_name in ROUTES:
        if route_method != wanted_method:
            continue
        params = _match_segments(_segments(pattern), path_segments)
        if params is not None:
            return handler_name, params
    return None
