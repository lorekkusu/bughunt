"""Static OpenAPI-flavored description of the API.

Builds a small OpenAPI 3.0 document straight from the declarative route
table in :mod:`taskqueue.api.routes`, so the spec can never drift from what
the router actually matches. Summaries live in the hand-kept
:data:`DESCRIPTIONS` map; :func:`spec` fails loudly when a route has no
entry there, turning "someone added a route and forgot the docs" into an
error at spec-generation time instead of a silently undocumented endpoint.
"""

from __future__ import annotations

import json
from typing import Any

from taskqueue.api import routes

#: Handler name -> one-line summary. Every handler name appearing in
#: ``routes.ROUTES`` must have an entry here; :func:`spec` enforces this.
DESCRIPTIONS: dict[str, str] = {
    "submit_job": "Submit a new job to the queue.",
    "list_jobs": "List jobs, optionally filtered by state, with pagination.",
    "get_status": "Fetch the current status of a single job.",
    "cancel_job": "Cancel a queued or running job.",
    "stats": "Operational snapshot: job counts, queue depth, cache and metrics.",
    "workers": "Known workers split into alive and stale sets.",
    "purge_cache": "Drop expired status-cache entries.",
}


def _path_parameters(pattern: str) -> list[dict[str, Any]]:
    """OpenAPI parameter objects for each ``{param}`` segment in *pattern*.

    Mirrors the router's segment convention: a segment counts as a
    placeholder only when it is wrapped in braces with a non-empty name.
    All path parameters are strings — the router captures raw segments.
    """
    parameters: list[dict[str, Any]] = []
    trimmed = pattern.strip("/")
    if not trimmed:
        return parameters
    for segment in trimmed.split("/"):
        if segment.startswith("{") and segment.endswith("}") and len(segment) > 2:
            parameters.append(
                {
                    "name": segment[1:-1],
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            )
    return parameters


def spec() -> dict[str, Any]:
    """Build the OpenAPI document from the live route table.

    Raises ``KeyError`` with an actionable message when a route's handler
    has no entry in :data:`DESCRIPTIONS`. This is a deliberate wiring check:
    the failure surfaces in the test suite or at startup, exactly when a new
    route was added without documentation.
    """
    paths: dict[str, dict[str, Any]] = {}
    for method, pattern, handler_name in routes.ROUTES:
        try:
            summary = DESCRIPTIONS[handler_name]
        except KeyError:
            raise KeyError(
                f"no description for handler {handler_name!r} "
                f"({method} {pattern}); add an entry to "
                f"taskqueue.api.openapi.DESCRIPTIONS"
            ) from None

        operation: dict[str, Any] = {
            "operationId": handler_name,
            "summary": summary,
            "responses": {"default": {"description": summary}},
        }
        parameters = _path_parameters(pattern)
        if parameters:
            operation["parameters"] = parameters

        paths.setdefault(pattern, {})[method.lower()] = operation

    return {
        "openapi": "3.0.0",
        "info": {"title": "taskqueue API", "version": "1.0.0"},
        "paths": paths,
    }


def to_json() -> str:
    """The spec rendered as deterministic JSON (sorted keys, indent 2).

    Sorted keys keep the output stable across Python versions and route
    reorderings, so the rendered document can be committed or diffed.
    """
    return json.dumps(spec(), sort_keys=True, indent=2)
