"""Follow the event log the way ``tail -f`` follows a file.

:class:`EventTailer` polls an :class:`~taskqueue.storage.events.EventLog`
and yields each new record exactly once. Progress is tracked by the *count*
of records already consumed, not by byte offsets: every scan re-iterates the
log from the top and skips the first N records. That rescan is O(n) per poll
— an honest tradeoff, chosen because it is trivially correct (no seek/inode
bookkeeping to get wrong) and cheap at benchmark-sized log lengths.
"""

from __future__ import annotations

import threading
import time
from typing import Iterator

from taskqueue.storage.events import EventLog

#: Default interval between scans of the log, in seconds.
DEFAULT_POLL_S = 0.5


class EventTailer:
    """Poll-based follower for an append-only event log.

    Instances hold no open file handles between scans, so a tailer can be
    created before the log file exists — an absent file simply reads as
    empty until the first event is appended.
    """

    def __init__(self, events: EventLog, poll_s: float = DEFAULT_POLL_S):
        if poll_s <= 0:
            raise ValueError(f"poll_s must be positive, got {poll_s!r}")
        self._events = events
        self._poll_s = poll_s

    def _count(self) -> int:
        """Number of records currently in the log."""
        return sum(1 for _ in self._events.iter_events())

    def _scan_from(self, consumed: int) -> tuple[list[dict], int]:
        """Records beyond the first *consumed*, plus the new consumed count.

        Re-iterates the whole log and skips the prefix. Because the log is
        append-only, the first *consumed* records are exactly the ones a
        previous scan already returned.
        """
        fresh: list[dict] = []
        for index, record in enumerate(self._events.iter_events()):
            if index >= consumed:
                fresh.append(record)
        return fresh, consumed + len(fresh)

    def follow(self, stop: threading.Event, from_start: bool = False) -> Iterator[dict]:
        """Yield new events as they appear, until *stop* is set.

        With ``from_start=False`` (the default) only events appended after
        the call begins are yielded; ``from_start=True`` replays the whole
        log first. Between scans the generator blocks in ``stop.wait`` for
        the poll interval, so setting *stop* wakes it promptly; *stop* is
        also checked before each yield so a consumer that sets the flag
        mid-batch is not fed the remainder.
        """
        consumed = 0 if from_start else self._count()
        while not stop.is_set():
            fresh, consumed = self._scan_from(consumed)
            for record in fresh:
                if stop.is_set():
                    return
                yield record
            stop.wait(self._poll_s)

    def collect_for(self, duration_s: float) -> list[dict]:
        """Gather every event appended during the next *duration_s* seconds.

        A convenience wrapper for tests and diagnostics: scans on the same
        poll interval as :meth:`follow`, using a ``time.monotonic`` deadline
        so wall-clock adjustments cannot stretch the window, and never
        sleeping past the remaining budget. Events already in the log when
        the call starts are excluded. A non-positive *duration_s* still
        performs one scan (which observes nothing new) and returns.
        """
        collected: list[dict] = []
        consumed = self._count()
        deadline = time.monotonic() + max(0.0, duration_s)
        while True:
            fresh, consumed = self._scan_from(consumed)
            collected.extend(fresh)
            remaining = deadline - time.monotonic()
            if remaining <= 0.0:
                return collected
            time.sleep(min(self._poll_s, remaining))
