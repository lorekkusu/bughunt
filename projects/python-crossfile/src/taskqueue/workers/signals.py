"""Cooperative shutdown signalling.

A :class:`ShutdownFlag` is a one-way latch shared between the process's
signal handlers and its worker/supervisor loops: SIGINT or SIGTERM flips the
flag, and every loop that polls it drains and exits on its own schedule.
"""

from __future__ import annotations

import logging
import signal
import threading
from typing import Optional

log = logging.getLogger(__name__)


class ShutdownFlag:
    """A latch that flips exactly once when shutdown is requested."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def request(self) -> None:
        """Request shutdown. Idempotent."""
        self._event.set()

    def is_set(self) -> bool:
        """True once shutdown has been requested."""
        return self._event.is_set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        """Block until shutdown is requested or *timeout* elapses.

        Returns True if shutdown was requested, False on timeout.
        """
        return self._event.wait(timeout)


def install(flag: ShutdownFlag) -> None:
    """Register SIGINT/SIGTERM handlers that call ``flag.request()``.

    ``signal.signal`` raises ``ValueError`` when called off the main thread,
    so installation is skipped (with a log line) anywhere but the main
    thread — embedded deployments arrange their own shutdown signalling.
    """
    if threading.current_thread() is not threading.main_thread():
        log.warning("install() called off the main thread; skipping signal handlers")
        return

    def _handler(signum: int, frame: object) -> None:
        log.info("received signal %s; requesting shutdown", signal.Signals(signum).name)
        flag.request()

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)
    log.debug("installed SIGINT/SIGTERM shutdown handlers")
