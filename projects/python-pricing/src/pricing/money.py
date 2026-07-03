"""Money helpers. Amounts are integer minor units (cents)."""

from decimal import Decimal, ROUND_HALF_UP


def round_half_up(amount) -> int:
    return int(Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def pct(cents: int, rate: float) -> int:
    return int(cents * rate)
