# python-pricing · claude/claude-opus-4-8 · effort=`max`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `a9f8b2065c7c` |
| Created | 2026-07-04 09:24:20 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 92% | 92% | 92% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 2.0 | 2 | 2 |
| Speed (s) | 276.1 | 262.1 | 286.6 |
| Output tokens | 20,423 | 19728 | 21762 |
| Est. cost (USD, API-equiv) | 0.9285 | 0.8509 | 0.9914 |

> Costs are **API-equivalent estimates** (what these tokens would cost on the
> OpenAI API), not actual subscription spend. See `pricing.json`.

## Detection stability

Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.

| ID | Severity | Bug | Found |
|----|----------|-----|:-----:|
| C1 | critical | Discount percent not clamped: percent > 1 yields a negative price | ❌ 0/3 |
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

- allocate ZeroDivisionError on empty order — seen in 2/3 runs
- refund_amount ZeroDivisionError when days_total==0 — seen in 2/3 runs
- refund_amount ZeroDivisionError when days_total == 0 — seen in 1/3 runs
- allocate ZeroDivisionError when line_count==0 — seen in 1/3 runs
