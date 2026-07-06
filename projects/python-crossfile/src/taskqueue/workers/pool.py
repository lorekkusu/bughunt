"""The worker pool: N daemon threads driving the dispatcher.

Each worker thread runs the same tick — heartbeat, one dispatch pass, then a
short interruptible sleep when the queue was idle — until the pool's stop
event is set. A crashed tick is logged and the worker keeps going; the thread
itself never dies to an exception.
"""

from __future__ import annotations

import logging
import threading
import time

from taskqueue.workers.dispatch import Dispatcher
from taskqueue.workers.heartbeat import HeartbeatMonitor

log = logging.getLogger(__name__)


class WorkerPool:
    def __init__(
        self,
        dispatcher: Dispatcher,
        heartbeats: HeartbeatMonitor,
        count: int = 4,
        poll_interval_s: float = 0.5,
    ):
        self._dispatcher = dispatcher
        self._heartbeats = heartbeats
        self._count = count
        self._poll_interval_s = poll_interval_s
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        """Spawn the worker threads. A pool may only be started once."""
        if self._threads:
            raise RuntimeError("worker pool already started")
        for index in range(self._count):
            name = f"worker-{index}"
            thread = threading.Thread(
                target=self._worker_loop, args=(name,), name=name, daemon=True
            )
            self._threads.append(thread)
            thread.start()
        log.info("started %d worker threads", self._count)

    def _worker_loop(self, worker_name: str) -> None:
        while not self._stop_event.is_set():
            try:
                self._heartbeats.record(worker_name)
                routed = self._dispatcher.run_once()
                if routed == 0:
                    self._stop_event.wait(self._poll_interval_s)
            except Exception:
                # A failed tick must not kill the worker thread.
                log.exception("worker %s tick failed; continuing", worker_name)
        log.debug("worker %s exiting", worker_name)

    def stop(self, timeout_s: float = 5.0) -> None:
        """Signal every worker to exit and join them within *timeout_s* total."""
        self._stop_event.set()
        deadline = time.monotonic() + timeout_s
        for thread in self._threads:
            remaining = max(0.0, deadline - time.monotonic())
            thread.join(remaining)
            if thread.is_alive():
                log.warning("worker %s did not stop within the join budget", thread.name)

    def alive_count(self) -> int:
        """How many worker threads are currently running."""
        return sum(1 for thread in self._threads if thread.is_alive())
