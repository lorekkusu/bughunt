# taskqueue

An embeddable task-queue service: jobs are submitted through a small HTTP-style
API layer, held in a priority queue, routed by a dispatcher, and executed by
leased workers with retry/backoff. State is kept in an in-memory store with a
read-through status cache, and every lifecycle change is appended to a JSONL
event log. A plugin system (audit, metrics, webhooks) hooks into execution.

```
src/taskqueue/
  api/       # request handlers, validation, auth, rate limiting, admin
  core/      # job model & state machine, priority queue, timing, metrics
  storage/   # job store, status cache, event log, snapshots
  workers/   # executor (leases, retries), dispatcher, heartbeat, pool
  clients/   # SDK, CLI, inspector, plugins (audit / metrics / webhook)
```

## Getting started

```bash
uv sync
uv run pytest
```
