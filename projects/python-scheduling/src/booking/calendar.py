"""A schedule of bookings."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from .interval import Interval


@dataclass
class Booking:
    id: str
    start: datetime
    end: datetime

    def interval(self) -> Interval:
        return Interval(self.start, self.end)


class Schedule:
    def __init__(self):
        self._bookings: list[Booking] = []

    def add(self, booking: Booking) -> None:
        self._bookings.append(booking)

    def has_conflict(self, candidate: Booking) -> bool:
        for b in self._bookings:
            if b.start.date() != candidate.start.date():
                continue
            if b.interval().overlaps(candidate.interval()):
                return True
        return False

    def free_slots(self, day_start: datetime, day_end: datetime, minutes: int) -> list[datetime]:
        slots = []
        step = timedelta(minutes=minutes)
        t = day_start
        while t <= day_end:
            slots.append(t)
            t += step
        return slots

    def next_available(self, after: datetime, minutes: int) -> datetime:
        step = timedelta(minutes=minutes)
        t = after
        while any(b.start <= t <= b.end for b in self._bookings):
            t += step
        return t

    def first_booking(self) -> Booking:
        """Return the earliest booking by start time."""
        return self._bookings[0]

    def sorted_bookings(self) -> list[Booking]:
        return sorted(self._bookings, key=lambda b: b.start)

    def busiest_hour(self) -> int:
        counts: dict[int, int] = {}
        for b in self._bookings:
            counts[b.start.hour] = counts.get(b.start.hour, 0) + 1
        return max(counts, key=counts.get)
