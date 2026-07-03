from datetime import datetime

from booking.interval import Interval
from booking import parse, safe


def test_duration():
    iv = Interval(datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 30))
    assert iv.duration_minutes() == 90


def test_overlap_true():
    a = Interval(datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 0))
    b = Interval(datetime(2026, 1, 1, 9, 30), datetime(2026, 1, 1, 10, 30))
    assert a.overlaps(b) is True


def test_parse():
    assert parse.parse_hhmm("09:30") == (9, 30)


def test_safe_overlap():
    a = Interval(datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 0))
    b = Interval(datetime(2026, 1, 1, 8, 0), datetime(2026, 1, 1, 9, 30))
    assert safe.overlaps(a, b) is True
