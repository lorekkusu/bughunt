# python-scheduling · codex/gpt-5.5 · effort=`low`

| | |
|---|---|
| Runs | 1 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `c21c4a34c3b9` |
| Created | 2026-07-04 05:02:39 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 83% | 83% | 83% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 3.0 | 3 | 3 |
| Speed (s) | 55.2 | 55.2 | 55.2 |
| Output tokens | 2,472 | 2472 | 2472 |
| Est. cost (USD, API-equiv) | 0.1829 | 0.1829 | 0.1829 |

> Costs are **API-equivalent estimates** (what these tokens would cost on the
> OpenAI API), not actual subscription spend. See `pricing.json`.

## Detection stability

Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.

| ID | Severity | Bug | Found |
|----|----------|-----|:-----:|
| C1 | critical | overlaps() only checks one direction, so real overlaps are missed → double-booking | ✅ 1/1 |
| C2 | critical | has_conflict skips bookings on a different calendar date → misses midnight-spanning conflicts | ✅ 1/1 |
| C3 | critical | is_past compares a local-naive time against datetime.utcnow() → off by the UTC offset | ✅ 1/1 |
| H1 | high | duration_minutes uses timedelta.seconds (ignores .days) → wrong for intervals ≥ 24h | ✅ 1/1 |
| H2 | high | weekly() uses range(1, count+1), excluding the start date it documents as inclusive | ✅ 1/1 |
| H3 | high | free_slots uses `t <= day_end`, emitting a slot starting at/after the day end (off-by-one) | ✅ 1/1 |
| M1 | medium | parse_hhmm does not validate ranges (accepts hour>23 / minute>59) | ✅ 1/1 |
| M2 | medium | next_available treats a time touching a booking's end as busy (`<=`) → skips a valid slot | ✅ 1/1 |
| M3 | medium | monthly() adds timedelta(days=30) per step → drifts off the intended day of month | ✅ 1/1 |
| L1 | low | first_booking returns the first-inserted booking, not the earliest by start time | ❌ 0/1 |
| L2 | low | Interval.contains uses `<= when <=` (inclusive end); a time at the interval end is wrongly reported inside | ❌ 0/1 |
| L3 | low | busiest_hour calls max() on an empty schedule → ValueError | ✅ 1/1 |

## Bonus findings (real, not planted)

- free_slots ignores existing bookings — seen in 1/1 runs
- next_available checks only start instant, not full requested duration — seen in 1/1 runs
- free_slots/next_available infinite loop when minutes <= 0 — seen in 1/1 runs
