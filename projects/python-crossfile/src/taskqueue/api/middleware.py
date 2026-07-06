"""Composable request middlewares.

A handler here is any ``(ctx, body) -> (status, body_dict)`` callable; a
middleware takes a handler and returns a wrapped handler with the same shape.
The app builds its request pipeline once with :func:`compose` and calls the
resulting handler for every request.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from taskqueue.api.ratelimit import RateLimiter

log = logging.getLogger(__name__)

Handler = Callable[["RequestContext", dict[str, Any]], tuple[int, dict]]
Middleware = Callable[[Handler], Handler]


@dataclass
class RequestContext:
    """Per-request facts the middlewares need.

    ``started_at`` is a ``time.monotonic()`` reading taken when the request
    entered the pipeline, so durations are immune to wall-clock jumps.
    """

    method: str
    path: str
    caller: str
    started_at: float


def logging_middleware(handler: Handler) -> Handler:
    """Log one line per request: method, path, status, duration, caller."""

    def wrapped(ctx: RequestContext, body: dict[str, Any]) -> tuple[int, dict]:
        status, response = handler(ctx, body)
        duration_ms = (time.monotonic() - ctx.started_at) * 1000.0
        log.info(
            "%s %s -> %d (%.1f ms) caller=%s",
            ctx.method,
            ctx.path,
            status,
            duration_ms,
            ctx.caller,
        )
        return status, response

    return wrapped


def rate_limit_middleware(limiter: RateLimiter) -> Middleware:
    """Reject requests with 429 once *limiter* stops admitting the caller."""

    def middleware(handler: Handler) -> Handler:
        def wrapped(ctx: RequestContext, body: dict[str, Any]) -> tuple[int, dict]:
            if not limiter.allow(ctx.caller):
                return 429, {"error": "rate limited"}
            return handler(ctx, body)

        return wrapped

    return middleware


def compose(middlewares: Sequence[Middleware], handler: Handler) -> Handler:
    """Wrap *handler* in *middlewares*; the first middleware is outermost."""
    wrapped = handler
    for middleware in reversed(middlewares):
        wrapped = middleware(wrapped)
    return wrapped
