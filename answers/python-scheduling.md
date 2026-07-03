---
# Machine-readable manifest consumed by the harness judge.
project: python-scheduling
planted_bugs:
  - {id: C1, severity: critical, title: "overlaps() only checks one direction, so real overlaps are missed → double-booking", file: "src/booking/interval.py", symbol: "Interval.overlaps"}
  - {id: C2, severity: critical, title: "has_conflict skips bookings on a different calendar date → misses midnight-spanning conflicts", file: "src/booking/calendar.py", symbol: "Schedule.has_conflict"}
  - {id: C3, severity: critical, title: "is_past compares a local-naive time against datetime.utcnow() → off by the UTC offset", file: "src/booking/reminders.py", symbol: "is_past"}
  - {id: H1, severity: high,     title: "duration_minutes uses timedelta.seconds (ignores .days) → wrong for intervals ≥ 24h", file: "src/booking/interval.py", symbol: "Interval.duration_minutes"}
  - {id: H2, severity: high,     title: "weekly() uses range(1, count+1), excluding the start date it documents as inclusive", file: "src/booking/recurrence.py", symbol: "weekly"}
  - {id: H3, severity: high,     title: "free_slots uses `t <= day_end`, emitting a slot starting at/after the day end (off-by-one)", file: "src/booking/calendar.py", symbol: "Schedule.free_slots"}
  - {id: M1, severity: medium,   title: "parse_hhmm does not validate ranges (accepts hour>23 / minute>59)", file: "src/booking/parse.py", symbol: "parse_hhmm"}
  - {id: M2, severity: medium,   title: "next_available treats a time touching a booking's end as busy (`<=`) → skips a valid slot", file: "src/booking/calendar.py", symbol: "Schedule.next_available"}
  - {id: M3, severity: medium,   title: "monthly() adds timedelta(days=30) per step → drifts off the intended day of month", file: "src/booking/recurrence.py", symbol: "monthly"}
  - {id: L1, severity: low,      title: "first_booking returns the first-inserted booking, not the earliest by start time", file: "src/booking/calendar.py", symbol: "Schedule.first_booking"}
  - {id: L2, severity: low,      title: "Interval.contains uses `<= when <=` (inclusive end); a time at the interval end is wrongly reported inside", file: "src/booking/interval.py", symbol: "Interval.contains"}
  - {id: L3, severity: low,      title: "busiest_hour calls max() on an empty schedule → ValueError", file: "src/booking/calendar.py", symbol: "Schedule.busiest_hour"}
noise:
  - {id: N1, title: "safe.overlaps: correct half-open overlap in both directions", file: "src/booking/safe.py", symbol: "overlaps"}
  - {id: N2, title: "safe.duration_total_minutes: correct total_seconds-based duration", file: "src/booking/safe.py", symbol: "duration_total_minutes"}
  - {id: N3, title: "safe.now_utc: correct tz-aware UTC now", file: "src/booking/safe.py", symbol: "now_utc"}
  - {id: N4, title: "safe.parse_iso: correct fromisoformat parsing", file: "src/booking/safe.py", symbol: "parse_iso"}
  - {id: N5, title: "safe.sorted_events: correct sort with a tie-break key", file: "src/booking/safe.py", symbol: "sorted_events"}
  - {id: N6, title: "Schedule.sorted_bookings: sorts by start; Python's stable sort keeps ties in insertion order → correct", file: "src/booking/calendar.py", symbol: "Schedule.sorted_bookings"}
---

# 🔑 ANSWER KEY — python-scheduling — DO NOT SHOW TO THE TOOL UNDER TEST

**Target project:** `projects/python-scheduling/` (theme: date/time & calendar
correctness — a different subtle-correctness domain from python-pricing).

12 planted bugs (3 critical / 3 high / 3 medium / 3 low), all **subtle date/time
correctness** defects — naive-vs-UTC comparison, half-open interval boundaries,
`timedelta.seconds` vs `.total_seconds()`, off-by-one on slots/recurrence,
30-day "months". No famous vulnerabilities. Plus 5 noise items that are correct.

## CRITICAL
- **C1 `interval.overlaps`** — `self.start <= other.start < self.end` only detects
  when `other` *starts inside* self; it misses the symmetric case where `other`
  starts before self but overlaps into it → conflicting bookings pass as free.
  Correct: `self.start < other.end and other.start < self.end` (see `safe.overlaps`).
- **C2 `calendar.Schedule.has_conflict`** — `continue`s past any existing booking
  whose `.start.date()` differs from the candidate's, so a booking that spans
  midnight (or a long booking starting the previous day) is never checked → double-book.
- **C3 `reminders.is_past`** — compares a local-naive `when` against
  `datetime.utcnow()` (naive UTC). The two are on different clocks, so results are
  wrong by the local UTC offset. Use a consistent, tz-aware "now".

## HIGH
- **H1 `interval.duration_minutes`** — `(end - start).seconds` returns only the
  seconds-within-a-day part (0–86399) and ignores `.days`, so any interval ≥ 24h (or
  crossing into `.days`) is wrong. Use `.total_seconds()` (see `safe.duration_total_minutes`).
- **H2 `recurrence.weekly`** — the docstring says occurrences start *inclusive* of
  `start`, but `range(1, count+1)` skips `start` and shifts every date one week late.
- **H3 `calendar.Schedule.free_slots`** — `while t <= day_end` emits a slot that
  starts exactly at (or past) `day_end`, an invalid trailing slot. Should be `t < day_end`.

## MEDIUM
- **M1 `parse.parse_hhmm`** — no range validation; `"25:70"` parses to `(25, 70)`.
  Should reject hour > 23 / minute > 59.
- **M2 `calendar.Schedule.next_available`** — the busy test `b.start <= t <= b.end`
  treats a time exactly at a booking's `end` as still busy, so it skips a slot that
  could legitimately start when the prior booking ends. Should be half-open (`< b.end`).
- **M3 `recurrence.monthly`** — `timedelta(days=30 * i)` approximates a month as 30
  days, so occurrences drift off the intended day-of-month across real months.

## LOW
- **L1 `calendar.Schedule.first_booking`** — returns `self._bookings[0]`, i.e. the
  first-*inserted* booking, not the earliest by start time. Should be `min` by `.start`.
- **L2 `interval.Interval.contains`** — `self.start <= when <= self.end` includes the
  end boundary, so a time exactly at the interval's end is reported as inside; for a
  half-open interval it should be `when < self.end`.
- **L3 `calendar.Schedule.busiest_hour`** — `max(counts, ...)` raises `ValueError`
  on an empty schedule; guard the empty case.

## NOISE (correct — flagging these is a false positive)
| # | Location | Why it's correct |
|---|----------|------------------|
| N1 | `safe.overlaps` | proper half-open overlap, both directions |
| N2 | `safe.duration_total_minutes` | uses `.total_seconds()` |
| N3 | `safe.now_utc` | tz-aware `datetime.now(timezone.utc)` |
| N4 | `safe.parse_iso` | `datetime.fromisoformat` |
| N5 | `safe.sorted_events` | sort with a `(start, id)` tie-break |
| N6 | `Schedule.sorted_bookings` | `sorted` is stable → ties keep insertion order; no tie-break needed |
