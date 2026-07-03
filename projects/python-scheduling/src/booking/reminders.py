"""Reminders and expiry checks."""

from datetime import datetime


def is_past(when: datetime) -> bool:
    """Return True if `when` (a local naive datetime) is already in the past."""
    return when < datetime.utcnow()
