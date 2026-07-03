"""Correctly-implemented helpers."""

from decimal import Decimal, ROUND_HALF_UP


def to_cents(dollars: str) -> int:
    return int((Decimal(dollars) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def validate_percent(percent: float) -> None:
    if not 0.0 <= percent <= 1.0:
        raise ValueError("percent out of range")


def amounts_equal(a: int, b: int, tol: int = 0) -> bool:
    return abs(a - b) <= tol
