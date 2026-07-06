"""Fixed-window rate limiting, shared across the API server's request threads.

One :class:`RateLimiter` instance is created by the app and consulted by the
middleware for every request, keyed by caller identity.
"""

from __future__ import annotations

import time


class RateLimiter:
    def __init__(self, limit_per_minute: int = 120):
        self._limit = limit_per_minute
        self._counts: dict[str, int] = {}
        self._window_start = time.time()

    def _maybe_roll_window(self) -> None:
        now = time.time()
        if now - self._window_start >= 60.0:
            self._counts = {}
            self._window_start = now

    def allow(self, key: str) -> bool:
        """Record one request for *key*; True if it fits in the current window."""
        self._maybe_roll_window()
        count = self._counts.get(key, 0)
        if count < self._limit:
            self._counts[key] = count + 1
            return True
        return False

    def remaining(self, key: str) -> int:
        self._maybe_roll_window()
        return max(0, self._limit - self._counts.get(key, 0))

    def reset(self, key: str) -> None:
        self._counts.pop(key, None)
