"""Parsing helpers."""


def parse_hhmm(text: str) -> tuple[int, int]:
    """Parse an 'HH:MM' 24-hour time into (hour, minute).

    Rejects out-of-range values (hour must be 0-23, minute 0-59).
    """
    hour, minute = text.split(":")
    return int(hour), int(minute)
