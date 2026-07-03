"""Loyalty point multipliers by spend."""

# (spend threshold in cents, points multiplier)
_THRESHOLDS = [(100, 1), (500, 2), (1000, 3)]


def multiplier(spend_cents: int) -> int:
    mult = 1
    for threshold, m in _THRESHOLDS:
        if spend_cents > threshold:
            mult = m
    return mult
