"""Map domain exceptions to HTTP responses.

The app's dispatch loop funnels every exception through :func:`to_response`.
Known :mod:`taskqueue.core.errors` types map to specific status codes with
their own messages; anything else becomes a generic 500 whose body never
leaks exception details (they go to the log instead).
"""

from __future__ import annotations

import logging

from taskqueue.core.errors import (
    ConfigError,
    InvalidTransition,
    JobNotFound,
    QueueFull,
    ValidationError,
)

log = logging.getLogger(__name__)

#: Fixed body text for unexpected errors — never derived from the exception.
GENERIC_MESSAGE = "internal server error"


def error_body(message: str) -> dict[str, str]:
    """The uniform error-response shape used across the API."""
    return {"error": message}


def to_response(exc: Exception) -> tuple[int, dict]:
    """Translate *exc* into ``(status_code, body)``."""
    if isinstance(exc, JobNotFound):
        return 404, error_body(str(exc))
    if isinstance(exc, InvalidTransition):
        return 409, error_body(str(exc))
    if isinstance(exc, QueueFull):
        return 429, error_body(str(exc))
    if isinstance(exc, ValidationError):
        return 400, error_body(str(exc))
    if isinstance(exc, ConfigError):
        log.error("configuration error surfaced to a request: %s", exc)
        return 500, error_body("configuration error")
    log.error("unhandled %s during request", type(exc).__name__, exc_info=exc)
    return 500, error_body(GENERIC_MESSAGE)
