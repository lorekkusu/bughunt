"""Liveness and readiness probes.

Two flavors of health, matching the usual orchestrator contract: *liveness*
answers "is the process up and serving?" and always succeeds if the handler
runs at all, while *readiness* answers "should this instance receive
traffic?" and fails when the queue is saturated or workers have stopped
heartbeating. Both are pure reads — probing never mutates any state.
"""

from __future__ import annotations

from typing import Any

from taskqueue.core.queue import PriorityQueue
from taskqueue.workers.heartbeat import HeartbeatMonitor

#: Default queue depth at which the instance stops reporting ready. Chosen
#: well under the queue's own capacity so load sheds before submissions 429.
DEFAULT_MAX_QUEUE_DEPTH = 5000


class HealthCheck:
    """Health probe handlers over the shared queue and heartbeat monitor.

    Handlers follow the API convention of returning ``(status_code, body)``
    so the app layer can route to them like any other handler.
    """

    def __init__(
        self,
        queue: PriorityQueue,
        heartbeats: HeartbeatMonitor,
        max_queue_depth: int = DEFAULT_MAX_QUEUE_DEPTH,
    ):
        if max_queue_depth < 1:
            raise ValueError(f"max_queue_depth must be >= 1, got {max_queue_depth}")
        self._queue = queue
        self._heartbeats = heartbeats
        self._max_queue_depth = max_queue_depth

    # -------------------------------------------------------------- liveness

    def liveness(self) -> tuple[int, dict[str, Any]]:
        """Always-ok probe: reaching this handler proves the process serves.

        Deliberately touches no shared component, so a wedged queue or a
        stuck heartbeat lock cannot make the orchestrator kill an instance
        that is otherwise still draining work.
        """
        return 200, {"status": "ok"}

    # ------------------------------------------------------------- readiness

    def readiness(self) -> tuple[int, dict[str, Any]]:
        """Ready when the queue has headroom and every worker is heartbeating.

        Returns ``200`` with ``{"status": "ok"}`` when the queue depth is
        strictly under the configured threshold *and* no known worker is
        stale. Otherwise returns ``503`` with a ``"reasons"`` list naming
        each failing check, so dashboards show *why* an instance dropped out
        of rotation rather than a bare status code.
        """
        reasons: list[str] = []

        depth = len(self._queue)
        if depth >= self._max_queue_depth:
            reasons.append(
                f"queue depth {depth} at or above limit {self._max_queue_depth}"
            )

        stale = sorted(self._heartbeats.stale_workers())
        if stale:
            reasons.append("stale workers: " + ", ".join(stale))

        if reasons:
            return 503, {"status": "unavailable", "reasons": reasons}
        return 200, {"status": "ok"}

    # ------------------------------------------------------------- accessors

    def detail(self) -> tuple[int, dict[str, Any]]:
        """Readiness plus the raw numbers behind it, for dashboards.

        Same status code as :meth:`readiness`, with the measured queue depth,
        the configured threshold, and the stale-worker list included so a
        dashboard can plot the margin instead of just the verdict.
        """
        code, body = self.readiness()
        body = dict(body)
        body["queue_depth"] = len(self._queue)
        body["max_queue_depth"] = self._max_queue_depth
        body["stale_workers"] = sorted(self._heartbeats.stale_workers())
        return code, body

    def max_queue_depth(self) -> int:
        """The configured readiness threshold (useful for dashboards)."""
        return self._max_queue_depth
