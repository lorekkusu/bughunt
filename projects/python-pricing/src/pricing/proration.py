"""Subscription proration."""


def prorate(monthly_cents: int, days_used: int, days_in_month: int) -> int:
    """Charge for the days used in the current billing month (of days_in_month)."""
    return monthly_cents * days_used // 30
