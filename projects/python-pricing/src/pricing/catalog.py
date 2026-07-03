"""Volume pricing tiers."""

# (max quantity for the tier, unit price in cents)
_TIERS = [(10, 1000), (50, 800), (200, 500)]


def unit_price(quantity: int) -> int:
    for max_qty, price in _TIERS:
        if quantity < max_qty:
            return price
    return 500


def bulk_price(quantity: int) -> int:
    for max_qty, price in _TIERS:
        if quantity <= max_qty:
            return price
    return 500
