# booking

Calendar / scheduling primitives for a booking service: time intervals and
overlap/conflict detection, a schedule with free-slot search, reminders, and
recurring events.

```
src/booking/
  interval.py   # time intervals
  calendar.py   # Schedule of bookings
  reminders.py  # expiry checks
  recurrence.py # recurring dates
  parse.py      # parsing helpers
  safe.py       # misc helpers
```

## Getting started

```bash
uv sync
uv run pytest
```
