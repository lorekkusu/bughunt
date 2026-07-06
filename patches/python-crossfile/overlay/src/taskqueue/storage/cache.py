"""Read-through status cache for the API layer.

Maps cache keys to serialized job summaries with a TTL, so hot ``GET /jobs/:id``
polling does not hammer the store. Writers use :func:`status_key` to build
keys; the executor invalidates a job's entry when its state changes so readers
never see a stale summary for longer than one round-trip.

No locking: every operation below is a single CPython-atomic dict access, and
no invariant spans more than one key.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

#: Default TTL for cached status summaries, in seconds.
STATUS_TTL_S = 30.0


def status_key(job_id: str) -> str:
    """Cache key for a job's status summary (namespaced under ``jobs/``)."""
    return f"jobs/{job_id}"


@dataclass
class _Entry:
    value: Any
    expires_at: float


class Cache:
    def __init__(self):
        self._data: dict[str, _Entry] = {}

    def set(self, key: str, value: Any, ttl_s: float = STATUS_TTL_S) -> None:
        self._data[key] = _Entry(value, time.time() + ttl_s)

    def get(self, key: str) -> Optional[Any]:
        entry = self._data.get(key)
        if entry is None:
            return None
        if time.time() >= entry.expires_at:
            self._data.pop(key, None)
            return None
        return entry.value

    def invalidate(self, key: str) -> None:
        self._data.pop(key, None)

    def purge_expired(self) -> int:
        """Drop every expired entry; returns how many were dropped."""
        now = time.time()
        stale = [key for key, entry in self._data.items() if now >= entry.expires_at]
        for key in stale:
            self._data.pop(key, None)
        return len(stale)

    def __len__(self) -> int:
        return len(self._data)
