# pricing

An order-pricing engine for a store: volume tiers, percentage discounts and
coupons, sales tax, subscription proration and refunds, and loyalty multipliers.
All monetary amounts are integer minor units (cents).

```
src/pricing/
  money.py      # rounding helpers
  catalog.py    # volume price tiers
  discount.py   # discounts, coupons, allocation
  tax.py        # sales tax
  invoice.py    # assemble line items into a total
  proration.py  # subscription proration
  refund.py     # refunds
  loyalty.py    # loyalty multipliers
  safe.py       # misc helpers
```

## Getting started

```bash
uv sync
uv run pytest
```
