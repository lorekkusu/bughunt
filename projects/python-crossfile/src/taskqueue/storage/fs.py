"""Filesystem helpers shared by the storage tooling.

Small wrappers around ``pathlib``/``os`` that encode the patterns the
snapshot and maintenance scripts need: idempotent directory creation, atomic
whole-file writes, file-age checks, and tolerant removal.
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """Create *path* (and parents) if needed and return it as a ``Path``."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def atomic_write_text(path: str | Path, text: str) -> None:
    """Write *text* to *path* atomically.

    The content is written to a temporary file in the same directory,
    flushed and fsynced, then moved over *path* with ``os.replace`` — so
    readers see either the old content or the new, never a partial write.
    """
    target = Path(path)
    fh = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=target.parent,
        prefix=target.name + ".",
        suffix=".tmp",
        delete=False,
    )
    try:
        with fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(fh.name, target)
    except BaseException:
        try:
            os.unlink(fh.name)
        except OSError:
            pass
        raise


def file_age_s(path: str | Path) -> float:
    """Seconds since *path* was last modified, floored at ``0.0``.

    The floor guards against clock skew making a freshly written file
    appear to be modified in the future.
    """
    mtime = Path(path).stat().st_mtime
    return max(0.0, time.time() - mtime)


def safe_remove(path: str | Path) -> bool:
    """Remove *path* if it exists; return whether a file was removed."""
    try:
        Path(path).unlink()
    except FileNotFoundError:
        return False
    return True
