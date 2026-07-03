# python-scheduling · cursor-agent/composer-2.5-fast · effort=`default`

| | |
|---|---|
| Runs | 1 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `c21c4a34c3b9` |
| Created | 2026-07-04 05:00:45 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 75% | 75% | 75% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 3.0 | 3 | 3 |
| Speed (s) | 36.2 | 36.2 | 36.2 |
| Output tokens | 6,228 | 6228 | 6228 |
| Est. cost (USD, API-equiv) | 0.1128 | 0.1128 | 0.1128 |

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
| H3 | high | free_slots uses `t <= day_end`, emitting a slot starting at/after the day end (off-by-one) | ❌ 0/1 |
| M1 | medium | parse_hhmm does not validate ranges (accepts hour>23 / minute>59) | ✅ 1/1 |
| M2 | medium | next_available treats a time touching a booking's end as busy (`<=`) → skips a valid slot | ❌ 0/1 |
| M3 | medium | monthly() adds timedelta(days=30) per step → drifts off the intended day of month | ✅ 1/1 |
| L1 | low | first_booking returns the first-inserted booking, not the earliest by start time | ❌ 0/1 |
| L2 | low | Interval.contains uses `<= when <=` (inclusive end); a time at the interval end is wrongly reported inside | ✅ 1/1 |
| L3 | low | busiest_hour calls max() on an empty schedule → ValueError | ✅ 1/1 |

## Bonus findings (real, not planted)

- first_booking crashes on empty schedule — seen in 1/1 runs
- free_slots does not exclude booked times — seen in 1/1 runs
- next_available ignores slot duration overlap — seen in 1/1 runs
