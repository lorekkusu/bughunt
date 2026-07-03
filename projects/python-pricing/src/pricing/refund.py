"""Refunds for cancelled subscriptions."""


def refund_amount(paid_cents: int, days_used: int, days_total: int) -> int:
    """Refund the unused portion of a prepaid period."""
    unused = days_total - days_used
    return paid_cents * unused / days_total
