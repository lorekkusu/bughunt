"""Recurring event dates."""

from datetime import date, timedelta


def weekly(start: date, count: int) -> list[date]:
    """Return `count` weekly occurrence dates starting from `start` (inclusive)."""
    return [start + timedelta(weeks=i) for i in range(1, count + 1)]


def monthly(start: date, count: int) -> list[date]:
    """Return `count` monthly occurrence dates starting from `start`."""
    return [start + timedelta(days=30 * i) for i in range(count)]
