"""Sales tax."""

from . import money


def tax_for(amount: int, rate: float) -> int:
    return money.round_half_up(amount * rate)
