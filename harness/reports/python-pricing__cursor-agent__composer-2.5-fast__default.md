# python-pricing · cursor-agent/composer-2.5-fast · effort=`default`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `a9f8b2065c7c` |
| Created | 2026-07-04 08:14:28 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 94% | 92% | 100% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 2.7 | 2 | 3 |
| Speed (s) | 36.2 | 34.3 | 38.8 |
| Output tokens | 5,938 | 5853 | 6070 |
| Est. cost (USD, API-equiv) | 0.1343 | 0.1214 | 0.1505 |

> Costs are **API-equivalent estimates** (what these tokens would cost on the
> OpenAI API), not actual subscription spend. See `pricing.json`.

## Detection stability

Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.

| ID | Severity | Bug | Found |
|----|----------|-----|:-----:|
| C1 | critical | Discount percent not clamped: percent > 1 yields a negative price | ⚠️ 1/3 |
| C2 | critical | Per-order coupon subtracted on every line item (multi-line over-discount) | ✅ 3/3 |
| C3 | critical | Tax computed on the pre-discount subtotal (wrong tax base) | ✅ 3/3 |
| H1 | high | Refund returns float money from division instead of rounded integer cents | ✅ 3/3 |
| H2 | high | Proration hardcodes /30 and ignores the days_in_month argument | ✅ 3/3 |
| H3 | high | Tier boundary off-by-one: quantity at a tier's max falls into the next tier | ✅ 3/3 |
| M1 | medium | pct truncates the fractional cent instead of rounding half-up | ✅ 3/3 |
| M2 | medium | stack applies the second discount to the original subtotal, not the already-discounted amount | ✅ 3/3 |
| M3 | medium | allocate drops the remainder when splitting an order discount (integer division) | ✅ 3/3 |
| L1 | low | Loyalty threshold uses > instead of >= (spend exactly at a threshold misqualified) | ✅ 3/3 |
| L2 | low | to_dollars uses integer // 100 and truncates the cents part | ✅ 3/3 |
| L3 | low | average_line divides by len with no guard for empty input (ZeroDivisionError) | ✅ 3/3 |

## Bonus findings (real, not planted)

- allocate ZeroDivisionError when line_count=0 — seen in 2/3 runs
- average_line integer floor division loses fractional cents — seen in 1/3 runs
- allocate ZeroDivisionError when line_count == 0 — seen in 1/3 runs
- refund missing validation for days_used >= days_total — seen in 1/3 runs
- refund ZeroDivisionError when days_total=0 — seen in 1/3 runs
- refund negative when days_used > days_total — seen in 1/3 runs
- refund_amount ZeroDivisionError when days_total=0 — seen in 1/3 runs
