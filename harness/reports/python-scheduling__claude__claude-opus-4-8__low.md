# python-scheduling · claude/claude-opus-4-8 · effort=`low`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `60fd3a139ff5` |
| Created | 2026-07-04 09:28:45 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 92% | 92% | 92% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 0.0 | 0 | 0 |
| Speed (s) | 44.8 | 41.6 | 47.4 |
| Output tokens | 3,149 | 3136 | 3164 |
| Est. cost (USD, API-equiv) | 0.2274 | 0.2179 | 0.2412 |

> Costs are **API-equivalent estimates** (what these tokens would cost on the
> OpenAI API), not actual subscription spend. See `pricing.json`.

## Detection stability

Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.

| ID | Severity | Bug | Found |
|----|----------|-----|:-----:|
| C1 | critical | overlaps() only checks one direction, so real overlaps are missed → double-booking | ✅ 3/3 |
| C2 | critical | has_conflict skips bookings on a different calendar date → misses midnight-spanning conflicts | ✅ 3/3 |
| C3 | critical | is_past compares a local-naive time against datetime.utcnow() → off by the UTC offset | ✅ 3/3 |
| H1 | high | duration_minutes uses timedelta.seconds (ignores .days) → wrong for intervals ≥ 24h | ✅ 3/3 |
| H2 | high | weekly() uses range(1, count+1), excluding the start date it documents as inclusive | ✅ 3/3 |
| H3 | high | free_slots uses `t <= day_end`, emitting a slot starting at/after the day end (off-by-one) | ❌ 0/3 |
| M1 | medium | parse_hhmm does not validate ranges (accepts hour>23 / minute>59) | ✅ 3/3 |
| M2 | medium | next_available treats a time touching a booking's end as busy (`<=`) → skips a valid slot | ✅ 3/3 |
| M3 | medium | monthly() adds timedelta(days=30) per step → drifts off the intended day of month | ✅ 3/3 |
| L1 | low | first_booking returns the first-inserted booking, not the earliest by start time | ✅ 3/3 |
| L2 | low | Interval.contains uses `<= when <=` (inclusive end); a time at the interval end is wrongly reported inside | ✅ 3/3 |
| L3 | low | busiest_hour calls max() on an empty schedule → ValueError | ✅ 3/3 |
