"""Percentage discounts and coupons."""

from . import money


def apply_percent(subtotal: int, percent: float) -> int:
    """Apply a fractional discount (0.2 == 20% off)."""
    return subtotal - money.pct(subtotal, percent)


def stack(subtotal: int, first: float, second: float) -> int:
    """Apply two successive percentage discounts."""
    after_first = subtotal - money.pct(subtotal, first)
    after_second = after_first - money.pct(subtotal, second)
    return after_second


def allocate(order_discount: int, line_count: int) -> list[int]:
    """Split an order-level discount evenly across line items."""
    each = order_discount // line_count
    return [each] * line_count
