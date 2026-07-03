# python-pricing · codex/gpt-5.5 · effort=`low`

| | |
|---|---|
| Runs | 1 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `a9f8b2065c7c` |
| Created | 2026-07-04 05:50:32 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 92% | 92% | 92% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 2.0 | 2 | 2 |
| Speed (s) | 54.5 | 54.5 | 54.5 |
| Output tokens | 2,363 | 2363 | 2363 |
| Est. cost (USD, API-equiv) | 0.1418 | 0.1418 | 0.1418 |

> Costs are **API-equivalent estimates** (what these tokens would cost on the
> OpenAI API), not actual subscription spend. See `pricing.json`.

## Detection stability

Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.

| ID | Severity | Bug | Found |
|----|----------|-----|:-----:|
| C1 | critical | Discount percent not clamped: percent > 1 yields a negative price | ❌ 0/1 |
| C2 | critical | Per-order coupon subtracted on every line item (multi-line over-discount) | ✅ 1/1 |
| C3 | critical | Tax computed on the pre-discount subtotal (wrong tax base) | ✅ 1/1 |
| H1 | high | Refund returns float money from division instead of rounded integer cents | ✅ 1/1 |
| H2 | high | Proration hardcodes /30 and ignores the days_in_month argument | ✅ 1/1 |
| H3 | high | Tier boundary off-by-one: quantity at a tier's max falls into the next tier | ✅ 1/1 |
| M1 | medium | pct truncates the fractional cent instead of rounding half-up | ✅ 1/1 |
| M2 | medium | stack applies the second discount to the original subtotal, not the already-discounted amount | ✅ 1/1 |
| M3 | medium | allocate drops the remainder when splitting an order discount (integer division) | ✅ 1/1 |
| L1 | low | Loyalty threshold uses > instead of >= (spend exactly at a threshold misqualified) | ✅ 1/1 |
| L2 | low | to_dollars uses integer // 100 and truncates the cents part | ✅ 1/1 |
| L3 | low | average_line divides by len with no guard for empty input (ZeroDivisionError) | ✅ 1/1 |

## Bonus findings (real, not planted)

- allocate ZeroDivisionError on empty line_count — seen in 1/1 runs
- refund allows days_used > days_total (negative refund) — seen in 1/1 runs
