---
# Machine-readable manifest consumed by the harness judge.
project: python-crossfile
review_mode: diff            # subject reviews `git diff main...HEAD`, not the whole tree
pr:
  branch: refactor-time-retry-pause
  title: "refactor: unify time on epoch millis, extract RetryPolicy, add pause/resume"
# distance = how much context is needed to see the defect:
#   D0 in-hunk · D1 whole-modified-file · D2 one-hop caller/callee in another file ·
#   D3 multi-hop / global invariant / runtime-registered contract
planted_bugs:
  - {id: C1, severity: critical, distance: D2, title: "lease_deadline now returns epoch millis; executor compares it against time.time() seconds, so leases never expire", file: "src/taskqueue/core/timing.py", symbol: "lease_deadline", evidence_file: "src/taskqueue/workers/executor.py", evidence_symbol: "_lease_expired"}
  - {id: C2, severity: critical, distance: D2, title: "ready_batch now sorts and returns the queue's internal list; dispatch pops from it, silently draining the queue", file: "src/taskqueue/core/queue.py", symbol: "ready_batch", evidence_file: "src/taskqueue/workers/dispatch.py", evidence_symbol: "run_once"}
  - {id: C3, severity: critical, distance: D3, title: "Hook dispatch now swallows all hook exceptions; the audit plugin raises AuditReject to veto execution, so the veto is silently ignored (audit bypass)", file: "src/taskqueue/clients/plugins/base.py", symbol: "_run_hooks", evidence_file: "src/taskqueue/clients/plugins/audit.py", evidence_symbol: "AuditPlugin.before_execute"}
  - {id: H1, severity: high, distance: D0, title: "pause handler: `state == RUNNING or QUEUED` is always truthy, so any job (including DONE) can be paused and later re-queued", file: "src/taskqueue/api/handlers.py", symbol: "pause_job"}
  - {id: H2, severity: high, distance: D2, title: "cache status key renamed job:{id} -> jobs/{id}; executor still invalidates the old hardcoded key, so completed jobs serve stale status until TTL", file: "src/taskqueue/storage/cache.py", symbol: "status_key", evidence_file: "src/taskqueue/workers/executor.py", evidence_symbol: "_finish"}
  - {id: H3, severity: high, distance: D3, title: "New PAUSED state falls into dispatch's defensive else branch, which marks unknown-state jobs FAILED", file: "src/taskqueue/core/job.py", symbol: "JobState", evidence_file: "src/taskqueue/workers/dispatch.py", evidence_symbol: "_route"}
  - {id: M1, severity: medium, distance: D1, title: "PAUSED added to JobState and is_active, but the _TRANSITIONS table in the same file has no PAUSED entries — resume raises KeyError", file: "src/taskqueue/core/job.py", symbol: "_TRANSITIONS", evidence_symbol: "can_transition"}
  - {id: M2, severity: medium, distance: D1, title: "get_job changed to return None instead of raising, but update_state in the same file still dereferences the result — AttributeError instead of clean JobNotFound", file: "src/taskqueue/storage/store.py", symbol: "Store.get_job", evidence_symbol: "Store.update_state"}
  - {id: M3, severity: medium, distance: D3, title: "Event log ts now written in millis; the SDK timeline reader feeds it to datetime.fromtimestamp and second-based duration math (far-future dates, 1000x durations)", file: "src/taskqueue/storage/events.py", symbol: "append_event", evidence_file: "src/taskqueue/clients/sdk.py", evidence_symbol: "job_timeline"}
  - {id: L1, severity: low, distance: D0, title: "parse_duration minutes branch multiplies by 6000 instead of 60000", file: "src/taskqueue/core/timing.py", symbol: "parse_duration"}
  - {id: L2, severity: low, distance: D0, title: "RetryPolicy caps backoff with max() instead of min(), so every retry waits at least the cap", file: "src/taskqueue/core/retry.py", symbol: "RetryPolicy.next_delay_ms"}
  - {id: L3, severity: low, distance: D1, title: "Retry extraction left the old job.attempts += 1 in the executor while RetryPolicy.record_failure also increments — attempts counted twice, retries exhausted twice as fast", file: "src/taskqueue/workers/executor.py", symbol: "_handle_failure", evidence_symbol: "_handle_failure"}
# Pre-existing bugs on main, NOT introduced by the diff. Scored on a separate
# axis (out-of-diff discovery), never counted in recall or FP.
#   on_path  = lives in a file a reviewer must read to catch a D2/D3 bug above
#   off_path = lives in a file no diff-related reasoning ever touches
base_bugs:
  - {id: B1, severity: medium, location: on_path, title: "Dispatch loop catches Exception and logs at DEBUG, silently swallowing routing failures", file: "src/taskqueue/workers/dispatch.py", symbol: "run_once"}
  - {id: B2, severity: high, location: on_path, title: "SDK submit() retries on timeout without an idempotency key — duplicate job submission", file: "src/taskqueue/clients/sdk.py", symbol: "Client.submit"}
  - {id: B3, severity: medium, location: on_path, title: "Audit plugin opens its log with mode 'w' on init, truncating the audit history on every restart", file: "src/taskqueue/clients/plugins/audit.py", symbol: "AuditPlugin.__init__"}
  - {id: B4, severity: high, location: off_path, title: "Backup restore deserializes with pickle.loads (RCE tripwire — catchable only by scanning far outside the diff)", file: "src/taskqueue/storage/backup.py", symbol: "restore"}
  - {id: B5, severity: low, location: off_path, title: "metrics.avg divides by len(samples) with no empty guard — ZeroDivisionError", file: "src/taskqueue/core/metrics.py", symbol: "avg"}
  - {id: B6, severity: medium, location: off_path, title: "Rate limiter does an unlocked check-then-increment on a shared counter — lost updates under threads", file: "src/taskqueue/api/ratelimit.py", symbol: "RateLimiter.allow"}
# Suspicious-but-correct changes INSIDE the diff. Flagging any as a defect is a FP.
noise:
  - {id: N1, title: "heartbeat.py millis migration is complete and consistent (constant, writer, and staleness check all updated) — looks like the units bugs elsewhere, correct here", file: "src/taskqueue/workers/heartbeat.py", symbol: "is_stale"}
  - {id: N2, title: "RetryPolicy jitter uses random.uniform — non-crypto random is correct for backoff jitter", file: "src/taskqueue/core/retry.py", symbol: "RetryPolicy.next_delay_ms"}
  - {id: N3, title: "cache dict mutated without a lock — every op is a single CPython-atomic dict operation with no cross-key invariant", file: "src/taskqueue/storage/cache.py", symbol: "Cache.set"}
  - {id: N4, title: "run_job's broad `except Exception` logs and RE-RAISES — swallow-looking but correct (distinct from C3's _run_hooks, which really swallows)", file: "src/taskqueue/clients/plugins/base.py", symbol: "PluginHost.run_job"}
  - {id: N5, title: "Event timestamps use wall-clock time.time() — correct for persisted epoch timestamps (monotonic would be the bug)", file: "src/taskqueue/storage/events.py", symbol: "append_event"}
---

# 🔑 ANSWER KEY — python-crossfile — DO NOT SHOW TO THE TOOL UNDER TEST

**Target:** `projects/python-crossfile/` (domain: task-queue service, ~5–6k lines,
5 packages) + `patches/python-crossfile/` (the PR under review).

This is the first **diff-mode** project. The subject does not review the whole
tree; it reviews one PR — branch `refactor-time-retry-pause` against `main` — on a
repo too large to read end-to-end. The design question it answers: **how does
recall decay with context distance?** Every planted bug is tagged D0–D3 by how far
from the hunk the evidence sits. D0 is the sanity anchor (any competent tool ≈
100%); the D2/D3 columns are the signal — they measure exactly what a codegraph /
indexing layer claims to buy you.

## The PR narrative (what the diff pretends to be)

> **refactor: unify time on epoch millis, extract RetryPolicy, add pause/resume**
> 1. All time handling moves to integer epoch **milliseconds** (was mixed
>    float-seconds): `core/timing.py`, `storage/events.py`, `workers/heartbeat.py`.
> 2. Retry/backoff logic extracted from `workers/executor.py` into a new
>    `core/retry.py` `RetryPolicy`.
> 3. Storage ergonomics: `Store.get_job` returns `Optional[Job]` instead of
>    raising; cache keys move to a `jobs/` namespace.
> 4. New feature: `JobState.PAUSED` + pause/resume endpoints in `api/handlers.py`.
> 5. Perf: `core/queue.py` `ready_batch` avoids a copy. Robustness: plugin hook
>    dispatch isolated in `clients/plugins/base.py`.

15 files changed, +180/−78 (measured). Every planted bug is a plausible slip
inside one of these five storylines; the noise items are the storylines done
*right* in places reviewers will want to flag.

## D0 — visible in the hunk alone (sanity anchors)

- **H1 `api/handlers.pause_job`** — `if job.state == JobState.RUNNING or
  JobState.QUEUED:` — the `or` arm is a bare truthy enum, so the guard always
  passes. Any job, including `DONE`/`FAILED`, can be paused and then resumed into
  the queue → duplicate execution of finished work. Fix: `in (RUNNING, QUEUED)`.
- **L1 `core/timing.parse_duration`** — new helper accepts `"500ms" | "2s" |
  "5m"`; the minutes branch multiplies by `6000` instead of `60_000`, so `"5m"` =
  30 s. Entirely inside the added function.
- **L2 `core/retry.RetryPolicy.next_delay_ms`** — backoff is computed correctly,
  then "capped" with `max(delay, self.max_delay_ms)` instead of `min(...)` — the
  comment on the same line says *cap*. Every retry waits at least the cap.

## D1 — needs the whole modified file

- **M1 `core/job.py`** — the diff adds `PAUSED` to `JobState` and updates
  `is_active()`, but the `_TRANSITIONS` dict ~60 lines below (unchanged) gains no
  `PAUSED` key and `RUNNING`'s allowed-set gains no `PAUSED` member. `can_transition`
  raises `KeyError` the moment a paused job is resumed. The hunk looks complete;
  the file proves it isn't.
- **M2 `storage/store.py`** — `get_job` changes `raise JobNotFound` →
  `return None` ("friendlier API"); the diff dutifully updates the *api/handlers*
  callers, but `update_state()` in the **same file** (outside hunk context) still
  does `job = self.get_job(job_id); job.state = new_state` → `AttributeError`
  where the old code gave a clean, handler-mapped 404.
- **L3 `workers/executor.py`** — the extraction hunk adds
  `self.policy.record_failure(job)` (which increments `job.attempts` inside
  `RetryPolicy`), but the pre-existing `job.attempts += 1` sits ~10 lines above the
  hunk in the same function. Attempts count twice; a job configured for 6 retries
  gets 3. Classic incomplete-extraction residue.

## D2 — one-hop caller/callee in another file

- **C1 `core/timing.lease_deadline`** → **`workers/executor._lease_expired`** —
  the helper now returns epoch **millis** (docstring updated, internally
  consistent). The executor — untouched by the diff — still compares
  `time.time() > job.lease_deadline`. An epoch-ms deadline is ~1000× any epoch-s
  now: **leases never expire**, so jobs owned by crashed workers are stuck forever.
- **C2 `core/queue.ready_batch`** → **`workers/dispatch.run_once`** — was
  `return sorted(self._entries, ...)` (a copy); now sorts in place and returns
  `self._entries` ("perf: avoid alloc"). The dispatcher does
  `batch = q.ready_batch()` then `batch.pop(0)` per routed job — it now pops the
  queue's own backing list: **queued jobs silently vanish** without going through
  `dequeue`, corrupting counts and dropping work.
- **H2 `storage/cache.status_key`** → **`workers/executor._finish`** — writer and
  the updated `api/handlers.get_status` read/write the new `jobs/{id}` key, but the
  executor's completion path (untouched) still invalidates the **hardcoded** old
  string `f"job:{job_id}"`. Invalidation now targets a key nobody writes:
  completed jobs keep serving their cached `RUNNING` status until TTL expiry.

## D3 — multi-hop / global invariant / runtime-registered contract

- **C3 `clients/plugins/base._run_hooks`** → **`clients/plugins/audit.py`** — the
  diff wraps hook dispatch in `try/except Exception: log.exception(...)`
  ("a failing plugin must not kill the worker"). But plugins are registered at
  runtime (no static import edge to grep), and `AuditPlugin.before_execute`'s
  documented contract is to **raise `AuditReject` to veto** non-allowlisted jobs.
  The veto is now swallowed and logged: **audit bypass — rejected jobs execute
  anyway.** Finding this requires enumerating plugin *implementations*, not
  callers.
- **H3 `core/job.JobState`** → **`workers/dispatch._route`** — the dispatcher's
  exhaustive `if/elif` over states ends in a defensive
  `else: job.state = FAILED  # unknown state` (pre-existing). Nothing in the diff
  touches dispatch, and `_route` doesn't call anything that changed — the only
  link is the enum's global "every consumer must be exhaustive" invariant. Result:
  **pausing a queued job gets it marked FAILED** by the next dispatch tick.
- **M3 `storage/events.append_event`** → **`clients/sdk.job_timeline`** — events
  are persisted JSONL; the writer now stamps `ts` in millis. The SDK's timeline
  reader — two hops away, connected only through the *file format* — does
  `datetime.fromtimestamp(ev["ts"])` (dates in the year ~57000, or `OSError` on
  some platforms) and second-based duration subtraction (1000× inflation).

## BASE BUGS — pre-existing on `main`, untouched by the diff

Separate axis: **out-of-diff discovery**. A subject that reports these is neither
rewarded in recall nor punished in FP — report the two `location` groups
separately.

**On-path** (inside the D2/D3 evidence files a good reviewer must open — do they
notice what's *next to* what they came to read?):
- **B1 `workers/dispatch.run_once`** — `except Exception:` around per-job routing,
  logged at `DEBUG` and the loop continues: routing failures are invisible at
  default log level.
- **B2 `clients/sdk.Client.submit`** — retries the HTTP submit on timeout with no
  idempotency key; a timed-out-but-committed first attempt = duplicate job.
- **B3 `clients/plugins/audit.AuditPlugin.__init__`** — opens the audit log with
  `open(path, "w")`: every process restart truncates the audit trail.

**Off-path** (cold files; finding these means the tool swept the whole repo —
that's *signal about scope discipline*, not a defect of the tool):
- **B4 `storage/backup.restore`** — `pickle.loads` on file bytes. Deliberately a
  *famous* vuln: it's a *tripwire* — any diff-scoped reviewer that reports it
  provably wandered repo-wide.
- **B5 `core/metrics.avg`** — `sum(samples) / len(samples)`, no empty guard.
- **B6 `api/ratelimit.RateLimiter.allow`** — `if self._count[key] < limit:
  self._count[key] += 1` across threads without a lock — check-then-act race,
  lost updates (genuine in CPython: read/compare/write is not atomic).

## NOISE (correct — flagging any of these as a defect is a false positive)

| # | Location | Why it's correct |
|---|----------|------------------|
| N1 | `workers/heartbeat.py` | the millis migration here is *complete*: constant renamed `_S`→`_MS`, writer and `is_stale` comparison both updated — same storyline as C1/M3 but done right |
| N2 | `core/retry.RetryPolicy` | `random.uniform` jitter — backoff jitter needs no crypto RNG |
| N3 | `storage/cache.Cache` | lock-free dict ops — each is a single CPython-atomic dict operation, no invariant spans two keys (see harness language-caveats) |
| N4 | `clients/plugins/base.PluginHost.run_job` | outer `except Exception: log.error(...); raise` — re-raises; only `_run_hooks` (C3) actually swallows |
| N5 | `storage/events.append_event` | wall-clock `time.time()` for *persisted* timestamps is correct; monotonic clocks are not epoch-anchored |

## Scoring notes for the judge

1. **Diff-scoped recall/FP.** Only findings attributable to the PR count toward
   recall and FP. Findings about untouched code are matched against `base_bugs`
   (→ out-of-diff discovery) or recorded as out-of-scope; they are **never** FPs.
2. **Cross-file credit at either end.** For D2/D3 bugs, credit the find if the
   report identifies the *mismatch* while anchored at either side (e.g. C1
   reported as "executor compares seconds against ms" **or** "lease_deadline
   changed units under its callers"). Naming one side without the broken
   interaction (e.g. "timing.py returns ms now" as a mere observation) is not a
   catch.
3. **Attribution guards.** M1 vs H3 are both PAUSED fallout — M1 is the
   transition table *inside* `core/job.py`, H3 is dispatch's else-branch. C3 vs N4
   are both "broad except in base.py" — C3 is `_run_hooks` (swallows), N4 is
   `run_job` (re-raises). C1/M3/N1 are all millis storylines — N1 (heartbeat) is
   the correct one. Match on file+symbol, not theme.
4. **Report slices.** Primary table: recall-by-distance (D0→D3) per config,
   plus FP as usual. Secondary: out-of-diff discovery split on_path / off_path.
   B4 findings additionally imply "repo-wide sweep" behavior — worth a note in
   the report prose.
