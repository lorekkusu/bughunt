"""Money transfer and interest logic."""

from . import db


def transfer(from_id, to_id, amount):
    """Move `amount` from one account to another and return the new source balance."""
    src = db.get_account(from_id)
    dst = db.get_account(to_id)
    if src is None or dst is None:
        raise ValueError("account not found")

    if src["balance"] < amount:
        raise ValueError("insufficient funds")

    new_src = src["balance"] - amount
    new_dst = dst["balance"] + amount
    db.update_balance(from_id, new_src)
    db.update_balance(to_id, new_dst)
    return new_src


def apply_interest(balance, rate):
    """Apply an interest `rate` (e.g. 0.05) to a balance."""
    return balance + balance * rate
