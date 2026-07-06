"""The SDK's transport layer.

The client SDK (:mod:`taskqueue.clients.sdk`) talks to the service through a
:class:`Transport`: ``post``/``get`` take a path and return the decoded
response body, raising :class:`TransportError` for error statuses and
:class:`TransportTimeout` when the service cannot be reached in time.

:class:`InMemoryTransport` is the embedded-deployment implementation — it
binds directly to an in-process handler object, so tests and single-process
deployments exercise the same SDK code paths as a networked client would.
"""

from __future__ import annotations

from typing import Any, Protocol


class TransportTimeout(Exception):
    """Raised when a request does not complete within the transport timeout."""


class TransportError(Exception):
    """Raised when the service answers with an error status (>= 400)."""

    def __init__(self, status: int, body: dict[str, Any]):
        super().__init__(f"request failed with status {status}: {body!r}")
        self.status = status
        self.body = body


class _App(Protocol):
    def handle(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict]: ...


class Transport:
    """Abstract transport. Subclasses implement :meth:`post` and :meth:`get`."""

    def post(self, path: str, body: dict) -> dict:
        raise NotImplementedError

    def get(self, path: str) -> dict:
        raise NotImplementedError


class InMemoryTransport(Transport):
    """A transport bound directly to an in-process application object.

    *app* is anything exposing ``handle(method, path, body=None,
    headers=None) -> (status, dict)``. *timeout_s* is stored only for
    interface parity with networked transports — in-process calls cannot
    time out, so it is never consulted.
    """

    def __init__(self, app: _App, timeout_s: float = 30.0):
        self._app = app
        self.timeout_s = timeout_s

    def _dispatch(self, method: str, path: str, body: dict | None = None) -> dict:
        status, response = self._app.handle(method, path, body=body, headers=None)
        if status >= 400:
            raise TransportError(status, response)
        return response

    def post(self, path: str, body: dict) -> dict:
        return self._dispatch("POST", path, body)

    def get(self, path: str) -> dict:
        return self._dispatch("GET", path)
