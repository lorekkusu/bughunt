"""Advisory file locks for storage tooling.

Snapshot and restore scripts that share a data directory coordinate through
a ``.lock`` sentinel file. Acquisition relies on ``os.open`` with
``O_CREAT | O_EXCL``, which the OS guarantees to be atomic — exactly one
process can create the sentinel, so no separate existence check is needed
(or wanted: a pre-check would only reintroduce a race).

These locks are advisory: they only exclude other cooperating ``FileLock``
users, not arbitrary processes.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from types import TracebackType
from typing import Optional


class LockTimeout(Exception):
    """Raised when a lock cannot be acquired before the timeout elapses."""


class FileLock:
    """Context manager holding an exclusive advisory lock on *path*.

    *path* names the resource being guarded; the sentinel created on disk is
    ``<path>.lock``. Acquisition polls every *poll_s* seconds and raises
    :class:`LockTimeout` if the sentinel is still held after *timeout_s*.
    """

    def __init__(self, path: str | Path, timeout_s: float = 10.0, poll_s: float = 0.05):
        self._lock_path = Path(str(path) + ".lock")
        self._timeout_s = timeout_s
        self._poll_s = poll_s
        self._fd: Optional[int] = None

    def held(self) -> bool:
        """True while this instance currently holds the lock."""
        return self._fd is not None

    def acquire(self) -> None:
        deadline = time.monotonic() + self._timeout_s
        while True:
            try:
                self._fd = os.open(self._lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise LockTimeout(
                        f"could not acquire {self._lock_path} within {self._timeout_s}s"
                    ) from None
                time.sleep(self._poll_s)

    def release(self) -> None:
        if self._fd is None:
            return
        os.close(self._fd)
        self._fd = None
        try:
            os.unlink(self._lock_path)
        except FileNotFoundError:
            pass

    def __enter__(self) -> FileLock:
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.release()
