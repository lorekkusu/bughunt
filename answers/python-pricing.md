---
# Machine-readable manifest consumed by the harness judge.
project: python-pricing
planted_bugs:
  - {id: C1, severity: critical, title: "Discount percent not clamped: percent > 1 yields a negative price", file: "src/pricing/discount.py", symbol: "apply_percent"}
  - {id: C2, severity: critical, title: "Per-order coupon subtracted on every line item (multi-line over-discount)", file: "src/pricing/invoice.py", symbol: "build"}
  - {id: C3, severity: critical, title: "Tax computed on the pre-discount subtotal (wrong tax base)", file: "src/pricing/invoice.py", symbol: "build"}
  - {id: H1, severity: high,     title: "Refund returns float money from division instead of rounded integer cents", file: "src/pricing/refund.py", symbol: "refund_amount"}
  - {id: H2, severity: high,     title: "Proration hardcodes /30 and ignores the days_in_month argument", file: "src/pricing/proration.py", symbol: "prorate"}
  - {id: H3, severity: high,     title: "Tier boundary off-by-one: quantity at a tier's max falls into the next tier", file: "src/pricing/catalog.py", symbol: "unit_price"}
  - {id: M1, severity: medium,   title: "pct truncates the fractional cent instead of rounding half-up", file: "src/pricing/money.py", symbol: "pct"}
  - {id: M2, severity: medium,   title: "stack applies the second discount to the original subtotal, not the already-discounted amount", file: "src/pricing/discount.py", symbol: "stack"}
  - {id: M3, severity: medium,   title: "allocate drops the remainder when splitting an order discount (integer division)", file: "src/pricing/discount.py", symbol: "allocate"}
  - {id: L1, severity: low,      title: "Loyalty threshold uses > instead of >= (spend exactly at a threshold misqualified)", file: "src/pricing/loyalty.py", symbol: "multiplier"}
  - {id: L2, severity: low,      title: "to_dollars uses integer // 100 and truncates the cents part", file: "src/pricing/invoice.py", symbol: "to_dollars"}
  - {id: L3, severity: low,      title: "average_line divides by len with no guard for empty input (ZeroDivisionError)", file: "src/pricing/invoice.py", symbol: "average_line"}
noise:
  - {id: N1, title: "round_half_up: correct Decimal rounding", file: "src/pricing/money.py", symbol: "round_half_up"}
  - {id: N2, title: "validate_percent: correct range validation", file: "src/pricing/safe.py", symbol: "validate_percent"}
  - {id: N3, title: "to_cents: correct Decimal conversion", file: "src/pricing/safe.py", symbol: "to_cents"}
  - {id: N4, title: "amounts_equal: correct integer comparison", file: "src/pricing/safe.py", symbol: "amounts_equal"}
  - {id: N5, title: "bulk_price: correct inclusive tier boundary", file: "src/pricing/catalog.py", symbol: "bulk_price"}
---

# 🔑 ANSWER KEY — python-pricing — DO NOT SHOW TO THE TOOL UNDER TEST

**Target project:** `projects/python-pricing/` (theme: pricing / subtle correctness).

12 planted bugs (3 critical / 3 high / 3 medium / 3 low) — all **subtle
correctness** defects in money math, no famous vulnerabilities or famous
invariants. Several require cross-function reasoning (C2/C3 span the invoice loop
+ tax/discount ordering). Plus 5 noise items that are actually correct. The intent
is to create attention-dilution: hasty/weaker reviewers deprioritize the subtle
ones. See `harness/docs/authoring-advanced.md`.

## CRITICAL
- **C1 `discount.apply_percent`** — `percent` is never clamped to [0,1]; a
  `percent > 1` produces a *negative* total (store pays the customer). Correct code
  validates the range (contrast: `safe.validate_percent`).
- **C2 `invoice.build`** — `coupon_cents` is a flat *per-order* coupon, but it is
  subtracted **inside the per-line loop**, so an order with N lines gets the coupon
  applied N times. Apply it once to the order subtotal.
- **C3 `invoice.build`** — tax is computed on `subtotal` *before* the discount is
  applied, then the discount is applied to the taxed amount. The tax base is wrong
  (and the discount wrongly reduces tax). Discount first, then tax the net.

## HIGH
- **H1 `refund.refund_amount`** — `paid_cents * unused / days_total` uses `/`
  (true division) → returns a **float**, not rounded integer cents; money precision
  and type are both wrong. Use integer/`round_half_up`.
- **H2 `proration.prorate`** — divides by a hardcoded `30` while ignoring the
  `days_in_month` argument it is given; months have 28–31 days, so proration is
  systematically off. Should divide by `days_in_month`.
- **H3 `catalog.unit_price`** — `if quantity < max_qty` excludes the tier's own
  `max_qty`, so a quantity exactly at a boundary (e.g. 10) is charged the *next*
  tier's price. Should be `<=` (contrast: `catalog.bulk_price`).

## MEDIUM
- **M1 `money.pct`** — `int(cents * rate)` truncates toward zero instead of
  rounding half-up (contrast `round_half_up`), so every percentage taken through
  `pct` (e.g. `discount.apply_percent` / `discount.stack`) is off by up to a cent.
  Use `round_half_up`.
- **M2 `discount.stack`** — the second discount is computed on the original
  `subtotal` (`int(subtotal * second)`) rather than on `after_first`, over-discounting.
- **M3 `discount.allocate`** — `order_discount // line_count` drops the remainder,
  so the allocated amounts sum to *less* than `order_discount`.

## LOW
- **L1 `loyalty.multiplier`** — `spend_cents > threshold` should be `>=`; spending
  exactly a threshold amount fails to qualify for that tier.
- **L2 `invoice.to_dollars`** — `total_cents // 100` truncates to whole dollars
  (`1250 -> 12`, dropping the cents), contradicting the docstring's own `12.5`
  example. Use `total_cents / 100` (or `Decimal`).
- **L3 `invoice.average_line`** — `total // len(lines)` raises `ZeroDivisionError`
  on an empty order; guard the empty case.

## NOISE (correct — flagging these is a false positive)
| # | Location | Why it's correct |
|---|----------|------------------|
| N1 | `money.round_half_up` | proper `Decimal` half-up rounding |
| N2 | `safe.validate_percent` | correctly rejects out-of-range percents |
| N3 | `safe.to_cents` | correct `Decimal` dollars→cents |
| N4 | `safe.amounts_equal` | correct integer comparison with tolerance |
| N5 | `catalog.bulk_price` | correct inclusive (`<=`) tier boundary |
