"""Correctly-implemented helpers."""

from datetime import datetime, timezone

from .interval import Interval


def overlaps(a: Interval, b: Interval) -> bool:
    """Half-open overlap test (correct in both directions)."""
    return a.start < b.end and b.start < a.end


def duration_total_minutes(a: Interval) -> int:
    return int((a.end - a.start).total_seconds() // 60)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(text: str) -> datetime:
    return datetime.fromisoformat(text)


def sorted_events(bookings, key_id):
    return sorted(bookings, key=lambda b: (b.start, key_id(b)))
