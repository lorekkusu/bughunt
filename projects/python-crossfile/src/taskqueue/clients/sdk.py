"""The client SDK.

Submission and status go through a transport (see
:mod:`taskqueue.clients.http`); timeline inspection reads the service's event
log directly, which is the supported pattern for embedded deployments where
client and service share a filesystem.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from taskqueue.clients.http import Transport, TransportTimeout
from taskqueue.storage.events import EventLog

log = logging.getLogger(__name__)

SUBMIT_RETRIES = 3


@dataclass
class TimelineEntry:
    kind: str
    at: datetime
    since_previous_s: Optional[float]


class Client:
    def __init__(self, transport: Transport, events_path: Optional[str] = None):
        self._transport = transport
        self._events = EventLog(events_path) if events_path else None

    # ---------------------------------------------------------------- submit

    def submit(
        self,
        name: str,
        payload: Optional[dict[str, Any]] = None,
        priority: str = "normal",
    ) -> str:
        """Submit a job and return its id. Retries on transport timeouts."""
        body = {"name": name, "payload": payload or {}, "priority": priority}
        last_exc: Optional[Exception] = None
        for attempt in range(SUBMIT_RETRIES):
            try:
                response = self._transport.post("/jobs", body)
                return response["id"]
            except TransportTimeout as exc:
                last_exc = exc
                log.warning("submit timed out (attempt %d/%d)", attempt + 1, SUBMIT_RETRIES)
        raise last_exc  # type: ignore[misc]

    # ---------------------------------------------------------------- status

    def status(self, job_id: str) -> dict[str, Any]:
        return self._transport.get(f"/jobs/{job_id}")

    def wait_for(self, job_id: str, timeout_s: float = 60.0, poll_s: float = 0.5) -> dict[str, Any]:
        """Poll until the job reaches a terminal state or *timeout_s* elapses."""
        deadline = time.monotonic() + timeout_s
        while True:
            body = self.status(job_id)
            if body["state"] in ("done", "failed", "cancelled"):
                return body
            if time.monotonic() >= deadline:
                raise TimeoutError(f"job {job_id} still {body['state']} after {timeout_s}s")
            time.sleep(poll_s)

    # -------------------------------------------------------------- timeline

    def job_timeline(self, job_id: str) -> list[TimelineEntry]:
        """The job's lifecycle events, oldest first, with inter-event gaps.

        Event ``ts`` fields are epoch timestamps written by the service's
        event log; gaps are reported in seconds.
        """
        if self._events is None:
            raise RuntimeError("timeline requires an events_path")
        entries: list[TimelineEntry] = []
        previous_ts: Optional[float] = None
        for event in self._events.iter_events(job_id):
            gap = None if previous_ts is None else round(event["ts"] - previous_ts, 3)
            entries.append(
                TimelineEntry(
                    kind=event["kind"],
                    at=datetime.fromtimestamp(event["ts"]),
                    since_previous_s=gap,
                )
            )
            previous_ts = event["ts"]
        return entries

    def total_runtime_s(self, job_id: str) -> float:
        """Wall-clock seconds from first to last recorded event."""
        events = list(self._events.iter_events(job_id)) if self._events else []
        if len(events) < 2:
            return 0.0
        return events[-1]["ts"] - events[0]["ts"]
