# python-crossfile · claude/claude-opus-4-8 · effort=`low`

| | |
|---|---|
| Runs | 1 |
| Mode | automated · prompt `diff-v1` |
| Judge | `opus` (claude) |
| Code hash | `a5d4dd12d58a` |
| Created | 2026-07-06 19:09:09 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 75% | 75% | 75% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 0.0 | 0 | 0 |
| Speed (s) | 102.4 | 102.4 | 102.4 |
| Output tokens | 5,929 | 5929 | 5929 |
| Est. cost (USD, API-equiv) | 0.5180 | 0.5180 | 0.5180 |

> Costs are **API-equivalent estimates** (what these tokens would cost on the
> OpenAI API), not actual subscription spend. See `pricing.json`.

## Detection stability

Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.

| ID | Severity | Distance | Bug | Found |
|----|----------|:--------:|-----|:-----:|
| C1 | critical | D2 | lease_deadline now returns epoch millis; executor compares it against time.time() seconds, so leases never expire | ✅ 1/1 |
| C2 | critical | D2 | ready_batch now sorts and returns the queue's internal list; dispatch pops from it, silently draining the queue | ✅ 1/1 |
| C3 | critical | D3 | Hook dispatch now swallows all hook exceptions; the audit plugin raises AuditReject to veto execution, so the veto is silently ignored (audit bypass) | ❌ 0/1 |
| H1 | high | D0 | pause handler: `state == RUNNING or QUEUED` is always truthy, so any job (including DONE) can be paused and later re-queued | ✅ 1/1 |
| H2 | high | D2 | cache status key renamed job:{id} -> jobs/{id}; executor still invalidates the old hardcoded key, so completed jobs serve stale status until TTL | ✅ 1/1 |
| H3 | high | D3 | New PAUSED state falls into dispatch's defensive else branch, which marks unknown-state jobs FAILED | ✅ 1/1 |
| M1 | medium | D1 | PAUSED added to JobState and is_active, but the _TRANSITIONS table in the same file has no PAUSED entries — resume raises KeyError | ✅ 1/1 |
| M2 | medium | D1 | get_job changed to return None instead of raising, but update_state in the same file still dereferences the result — AttributeError instead of clean JobNotFound | ❌ 0/1 |
| M3 | medium | D3 | Event log ts now written in millis; the SDK timeline reader feeds it to datetime.fromtimestamp and second-based duration math (far-future dates, 1000x durations) | ❌ 0/1 |
| L1 | low | D0 | parse_duration minutes branch multiplies by 6000 instead of 60000 | ✅ 1/1 |
| L2 | low | D0 | RetryPolicy caps backoff with max() instead of min(), so every retry waits at least the cap | ✅ 1/1 |
| L3 | low | D1 | Retry extraction left the old job.attempts += 1 in the executor while RetryPolicy.record_failure also increments — attempts counted twice, retries exhausted twice as fast | ✅ 1/1 |

## Recall by context distance

D0 = visible in the hunk · D1 = whole modified file · D2 = one-hop
caller/callee in another file · D3 = multi-hop / global invariant.

| Distance | Bugs | Mean recall | Min | Max |
|----------|:----:|:-----------:|:---:|:---:|
| D0 | 3 | 100% | 100% | 100% |
| D1 | 3 | 67% | 67% | 67% |
| D2 | 3 | 100% | 100% | 100% |
| D3 | 3 | 33% | 33% | 33% |

## Out-of-diff discovery (pre-existing bugs — separate axis)

Real bugs on `main`, untouched by the PR. Reporting them is neither
rewarded in recall nor punished as FP. on_path = lives in a file a
reviewer must read to catch a D2/D3 bug; off_path = cold code (finding
these implies a repo-wide sweep).

| ID | Location | Bug | Reported |
|----|----------|-----|:--------:|
| B4 | off_path | Backup restore deserializes with pickle.loads (RCE tripwire — catchable only by scanning far outside the diff) | ❌ 0/1 |
| B5 | off_path | metrics.avg divides by len(samples) with no empty guard — ZeroDivisionError | ❌ 0/1 |
| B6 | off_path | Rate limiter does an unlocked check-then-increment on a shared counter — lost updates under threads | ❌ 0/1 |
| B1 | on_path | Dispatch loop catches Exception and logs at DEBUG, silently swallowing routing failures | ❌ 0/1 |
| B2 | on_path | SDK submit() retries on timeout without an idempotency key — duplicate job submission | ❌ 0/1 |
| B3 | on_path | Audit plugin opens its log with mode 'w' on init, truncating the audit history on every restart | ❌ 0/1 |
