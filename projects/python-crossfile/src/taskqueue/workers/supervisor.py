"""Watchdog over the worker pool.

The supervisor *reports*; it does not restart. Restarting workers is an
operator-driven action (recycle the process, or start a fresh pool) — this
loop only surfaces stale workers through logs and its return value, and tidies
heartbeat bookkeeping once the pool has no live threads left. The pool exposes
only an aggregate :meth:`WorkerPool.alive_count`, so per-worker liveness
cannot be checked here; a stale-but-possibly-alive worker is logged, not
forgotten.
"""

from __future__ import annotations

import logging

from taskqueue.workers.heartbeat import HeartbeatMonitor
from taskqueue.workers.pool import WorkerPool
from taskqueue.workers.signals import ShutdownFlag

log = logging.getLogger(__name__)


class Supervisor:
    def __init__(
        self,
        pool: WorkerPool,
        heartbeats: HeartbeatMonitor,
        check_interval_s: float = 10.0,
    ):
        self._pool = pool
        self._heartbeats = heartbeats
        self._check_interval_s = check_interval_s

    def check_once(self) -> list[str]:
        """One watchdog pass. Returns the ids of stale workers.

        Every stale worker is logged. Heartbeat entries are only forgotten
        when the pool reports zero live threads — then no heartbeat can ever
        refresh, so the entries are dead bookkeeping.
        """
        stale = self._heartbeats.stale_workers()
        if not stale:
            return stale
        alive = self._pool.alive_count()
        for worker_id in stale:
            log.warning(
                "worker %s is stale (no heartbeat; pool reports %d live threads)",
                worker_id,
                alive,
            )
            if alive == 0:
                self._heartbeats.forget(worker_id)
        return stale

    def run(self, flag: ShutdownFlag) -> None:
        """Run watchdog passes until *flag* requests shutdown."""
        log.info("supervisor running (interval %.1fs)", self._check_interval_s)
        while not flag.is_set():
            self.check_once()
            flag.wait(self._check_interval_s)
        log.info("supervisor exiting")
