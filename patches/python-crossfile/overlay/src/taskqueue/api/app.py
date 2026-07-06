"""Application wiring: one :class:`App` owns every shared component.

``App.handle`` is the whole request path: identify the caller (anonymous when
no token table is configured), run the middleware chain (logging, rate limit),
route via :mod:`taskqueue.api.routes`, dispatch to the handler objects, and
translate escaped domain exceptions with :mod:`taskqueue.api.errors`.
"""

from __future__ import annotations

import time
from typing import Any, Mapping, Optional

from taskqueue.api import errors as api_errors
from taskqueue.api import middleware, routes
from taskqueue.api.admin import AdminHandlers
from taskqueue.api.auth import TokenAuth
from taskqueue.api.handlers import Handlers
from taskqueue.api.middleware import RequestContext
from taskqueue.api.ratelimit import RateLimiter
from taskqueue.clients.plugins import load_plugins
from taskqueue.clients.plugins.base import PluginHost
from taskqueue.core.config import Config
from taskqueue.core.metrics import Registry
from taskqueue.core.queue import PriorityQueue
from taskqueue.storage.cache import Cache
from taskqueue.storage.events import EventLog
from taskqueue.storage.store import Store
from taskqueue.workers.dispatch import Dispatcher
from taskqueue.workers.executor import Executor
from taskqueue.workers.heartbeat import HeartbeatMonitor
from taskqueue.workers.pool import WorkerPool


class App:
    def __init__(
        self,
        config: Optional[Config] = None,
        tokens: Optional[Mapping[str, str]] = None,
    ):
        self._config = config or Config()
        self._store = Store()
        self._queue = PriorityQueue(self._config.queue_max_size)
        self._cache = Cache()
        self._events = EventLog(self._config.events_path)
        plugin_instances = load_plugins(
            self._config.plugin_modules(),
            audit_log_path=self._config.audit_log_path,
        )
        self._plugins = PluginHost(plugin_instances)
        self._executor = Executor(
            self._store, self._cache, self._events, self._plugins, self._config
        )
        self._dispatcher = Dispatcher(self._queue, self._executor)
        self._heartbeats = HeartbeatMonitor()
        self._registry = Registry()
        self._handlers = Handlers(self._store, self._queue, self._cache, self._events)
        self._admin = AdminHandlers(
            self._store, self._queue, self._cache, self._heartbeats, self._registry
        )
        self._limiter = RateLimiter(self._config.rate_limit_per_minute)
        self._auth = TokenAuth(tokens or {})
        self._pool: Optional[WorkerPool] = None
        self._pipeline = middleware.compose(
            [
                middleware.logging_middleware,
                middleware.rate_limit_middleware(self._limiter),
            ],
            self._dispatch_request,
        )

    # The stateful components are exposed read-only for embedding callers
    # (CLI, tests, snapshot tooling); request traffic must go through handle().

    @property
    def store(self) -> Store:
        return self._store

    @property
    def queue(self) -> PriorityQueue:
        return self._queue

    @property
    def events(self) -> EventLog:
        return self._events

    @property
    def executor(self) -> Executor:
        return self._executor

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dispatcher

    # ---------------------------------------------------------------- requests

    def handle(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> tuple[int, dict]:
        """Serve one request; always returns ``(status_code, body)``."""
        caller = self._auth.identify(headers or {}) or "anonymous"
        ctx = RequestContext(
            method=method.upper(),
            path=path,
            caller=caller,
            started_at=time.monotonic(),
        )
        return self._pipeline(ctx, body or {})

    def _dispatch_request(
        self, ctx: RequestContext, body: dict[str, Any]
    ) -> tuple[int, dict]:
        matched = routes.match(ctx.method, ctx.path)
        if matched is None:
            return 404, api_errors.error_body(f"no route for {ctx.method} {ctx.path}")
        handler_name, params = matched
        try:
            return self._invoke(handler_name, params, body)
        except Exception as exc:
            return api_errors.to_response(exc)

    def _invoke(
        self, handler_name: str, params: dict[str, str], body: dict[str, Any]
    ) -> tuple[int, dict]:
        if handler_name == "submit_job":
            return self._handlers.submit_job(body)
        if handler_name == "get_status":
            return self._handlers.get_status(params["job_id"])
        if handler_name == "cancel_job":
            return self._handlers.cancel_job(params["job_id"])
        if handler_name == "pause_job":
            return self._handlers.pause_job(params["job_id"])
        if handler_name == "resume_job":
            return self._handlers.resume_job(params["job_id"])
        if handler_name == "list_jobs":
            try:
                limit = int(body.get("limit", 50))
                offset = int(body.get("offset", 0))
            except (TypeError, ValueError):
                return 400, api_errors.error_body("'limit' and 'offset' must be integers")
            return self._handlers.list_jobs(body.get("state"), limit, offset)
        if handler_name == "stats":
            return self._admin.stats()
        if handler_name == "workers":
            return self._admin.workers()
        if handler_name == "purge_cache":
            return self._admin.purge_cache()
        raise RuntimeError(f"route table names unknown handler: {handler_name}")

    # ----------------------------------------------------------------- workers

    def start_workers(self) -> None:
        """Create (lazily) and start the background worker pool. Idempotent."""
        if self._pool is None:
            self._pool = WorkerPool(
                self._dispatcher, self._heartbeats, self._config.workers
            )
            self._pool.start()

    def stop_workers(self) -> None:
        """Stop the worker pool if it was started."""
        if self._pool is not None:
            self._pool.stop()
            self._pool = None
