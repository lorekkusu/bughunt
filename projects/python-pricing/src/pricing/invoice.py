"""Assemble invoices from line items."""

from . import catalog, discount, tax


def build(lines, coupon_cents=0, discount_pct=0.0, tax_rate=0.0) -> int:
    """Build an order total from line items.

    lines: list of (quantity,) tuples. coupon_cents is a flat per-order coupon.
    Order of operations: sum the line prices, subtract the coupon once from the
    order subtotal, apply the percent discount, then add tax on the discounted
    (net) subtotal.
    """
    subtotal = 0
    for (quantity,) in lines:
        line = catalog.unit_price(quantity) * quantity
        line = line - coupon_cents
        subtotal += line
    taxed = subtotal + tax.tax_for(subtotal, tax_rate)
    return discount.apply_percent(taxed, discount_pct)


def to_dollars(total_cents: int) -> float:
    """Convert integer cents to a dollar amount for display (e.g. 1250 -> 12.5)."""
    return total_cents // 100


def average_line(lines) -> int:
    total = sum(catalog.unit_price(q) * q for (q,) in lines)
    return total // len(lines)
