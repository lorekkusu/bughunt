# bughunt — benchmark summary

Recall = planted bugs found. **✅** found every run · **⚠️** some runs · **❌** never. Costs are **API-equivalent estimates**, not actual spend.

⟨manual⟩ = human-triggered tool scored via `bench judge` (no cost/speed/token). `prompt` = which review prompt ran (`standard-v1` for automated tools; `native` means the tool used its own prompt — not directly comparable).

## python-basic

### 🏆 Leaderboard (by recall, then cost)

| # | Config | Recall | FP | $/run | Speed |
|--:|--------|:------:|:--:|:-----:|:-----:|
| 🥇 | cursor-agent/composer-2.5-fast/default | 100% | 0.0 | $0.2305 | 62s |
| 🥈 | codex/gpt-5.5/high | 94% | 0.0 | $0.2699 | 114s |
| 🥉 | codex/gpt-5.5/xhigh | 92% | 1.3 | $0.6657 | 278s |
| 4 | codex/gpt-5.5/low | 89% | 0.3 | $0.1936 | 77s |
| 5 | codex/gpt-5.5/medium | 89% | 0.7 | $0.2340 | 92s |
| 6 | cursor/bugbot/default ⟨manual⟩ | 89% | 0.0 | — | — |
| 7 | claude/claude-opus-4-8/xhigh | 86% | 0.0 | $0.4693 | 115s |
| 8 | claude/claude-opus-4-8/max | 86% | 0.0 | $0.6657 | 202s |
| 9 | claude/claude-opus-4-8/medium | 86% | 0.0 | $0.2487 | 44s |
| 10 | claude/claude-opus-4-8/high | 83% | 0.0 | $0.3074 | 58s |
| 11 | coderabbit/cli/default | 83% | 0.0 | — | 213s |
| 12 | claude/claude-opus-4-8/low | 78% | 0.7 | $0.2108 | 36s |

### Metrics (all configs)

| Config | Runs | Recall (mean·min–max) | FP | Bonus | Speed | Out-tok | Est. $ |
|--------|:----:|-----------------------|:--:|:-----:|:-----:|:-------:|:------:|
| claude/claude-opus-4-8/`low` | 3 | 78% · 75%–83% | 0.7 | 5.0 | 35.8s | 2,286 | $0.2108 |
| claude/claude-opus-4-8/`medium` | 3 | 86% · 75%–92% | 0.0 | 4.3 | 44.2s | 2,991 | $0.2487 |
| claude/claude-opus-4-8/`high` | 3 | 83% · 83%–83% | 0.0 | 4.0 | 58.5s | 3,860 | $0.3074 |
| claude/claude-opus-4-8/`xhigh` | 3 | 86% · 83%–92% | 0.0 | 3.3 | 114.9s | 7,810 | $0.4693 |
| claude/claude-opus-4-8/`max` | 3 | 86% · 83%–92% | 0.0 | 4.3 | 202.3s | 14,245 | $0.6657 |
| coderabbit/cli/`default` ⟨native⟩ | 3 | 83% · 83%–83% | 0.0 | 6.7 | 212.8s | — | — |
| codex/gpt-5.5/`low` | 3 | 89% · 83%–92% | 0.3 | 4.3 | 77.2s | 2,792 | $0.1936 |
| codex/gpt-5.5/`medium` | 3 | 89% · 83%–92% | 0.7 | 3.7 | 91.8s | 3,602 | $0.2340 |
| codex/gpt-5.5/`high` | 3 | 94% · 92%–100% | 0.0 | 5.7 | 113.7s | 4,815 | $0.2699 |
| codex/gpt-5.5/`xhigh` | 3 | 92% · 92%–92% | 1.3 | 4.0 | 277.7s | 13,603 | $0.6657 |
| cursor/bugbot/`default` ⟨manual·standard-v1⟩ | 3 | 89% · 83%–92% | 0.0 | 4.3 | —s | — | — |
| cursor-agent/composer-2.5-fast/`default` | 3 | 100% · 100%–100% | 0.0 | 8.0 | 62.1s | 8,960 | $0.2305 |

| Bug | claude-opus-4-8/`low` | claude-opus-4-8/`medium` | claude-opus-4-8/`high` | claude-opus-4-8/`xhigh` | claude-opus-4-8/`max` | cli/`default` ⟨native⟩ | gpt-5.5/`low` | gpt-5.5/`medium` | gpt-5.5/`high` | gpt-5.5/`xhigh` | bugbot/`default` ⟨manual·standard-v1⟩ | composer-2.5-fast/`default` |
|-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 crit SQL injection | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| C2 crit OS command injection | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| C3 crit Insecure deserialization (pickle) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H1 high Path traversal | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H2 high Weak password hashing (unsalted MD5) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H3 high Broken access control (IDOR) | ⚠️ 1/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| M1 medi Race condition / TOCTOU on transfer | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 1/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| M2 medi Floating-point money arithmetic | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ⚠️ 1/3 | ⚠️ 2/3 | ⚠️ 2/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 |
| M3 medi Off-by-one in pagination | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L1 low Mutable default argument | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L2 low Overly-broad except swallowing errors | ❌ 0/3 | ⚠️ 2/3 | ❌ 0/3 | ⚠️ 1/3 | ❌ 0/3 | ⚠️ 2/3 | ❌ 0/3 | ❌ 0/3 | ⚠️ 1/3 | ❌ 0/3 | ⚠️ 2/3 | ✅ 3/3 |
| L3 low Identity vs equality (is) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |

## python-pricing

### 🏆 Leaderboard (by recall, then cost)

| # | Config | Recall | FP | $/run | Speed |
|--:|--------|:------:|:--:|:-----:|:-----:|
| 🥇 | cursor-agent/composer-2.5-fast/default | 94% | 0.0 | $0.1343 | 36s |
| 🥈 | claude/claude-opus-4-8/low | 92% | 0.0 | $0.2296 | 46s |
| 🥉 | claude/claude-opus-4-8/max | 92% | 0.0 | $0.9285 | 276s |
| 4 | cursor/bugbot/default ⟨manual⟩ | 92% | 0.0 | — | — |
| 5 | codex/gpt-5.5/medium | 89% | 0.3 | $0.2735 | 118s |
| 6 | claude/claude-opus-4-8/medium | 89% | 0.0 | $0.2784 | 55s |
| 7 | claude/claude-opus-4-8/high | 89% | 0.0 | $0.3060 | 66s |
| 8 | claude/claude-opus-4-8/xhigh | 86% | 0.0 | $0.4811 | 154s |
| 9 | codex/gpt-5.5/low | 83% | 0.0 | $0.2698 | 87s |
| 10 | codex/gpt-5.5/high | 83% | 0.0 | $0.3374 | 137s |
| 11 | codex/gpt-5.5/xhigh | 83% | 0.0 | $0.5591 | 232s |
| 12 | coderabbit/cli/default | 75% | 0.3 | — | 180s |

### Metrics (all configs)

| Config | Runs | Recall (mean·min–max) | FP | Bonus | Speed | Out-tok | Est. $ |
|--------|:----:|-----------------------|:--:|:-----:|:-----:|:-------:|:------:|
| claude/claude-opus-4-8/`low` | 3 | 92% · 92%–92% | 0.0 | 1.3 | 45.9s | 3,125 | $0.2296 |
| claude/claude-opus-4-8/`medium` | 3 | 89% · 83%–92% | 0.0 | 1.3 | 54.6s | 3,897 | $0.2784 |
| claude/claude-opus-4-8/`high` | 3 | 89% · 83%–92% | 0.0 | 1.3 | 66.0s | 4,986 | $0.3060 |
| claude/claude-opus-4-8/`xhigh` | 3 | 86% · 83%–92% | 0.0 | 1.0 | 153.5s | 11,802 | $0.4811 |
| claude/claude-opus-4-8/`max` | 3 | 92% · 92%–92% | 0.0 | 2.0 | 276.1s | 20,423 | $0.9285 |
| coderabbit/cli/`default` ⟨native⟩ | 3 | 75% · 67%–83% | 0.3 | 0.3 | 179.6s | — | — |
| codex/gpt-5.5/`low` | 3 | 83% · 75%–92% | 0.0 | 1.0 | 86.8s | 3,256 | $0.2698 |
| codex/gpt-5.5/`medium` | 3 | 89% · 83%–92% | 0.3 | 0.7 | 117.9s | 4,583 | $0.2735 |
| codex/gpt-5.5/`high` | 3 | 83% · 83%–83% | 0.0 | 0.0 | 136.7s | 5,823 | $0.3374 |
| codex/gpt-5.5/`xhigh` | 3 | 83% · 83%–83% | 0.0 | 0.7 | 231.5s | 10,929 | $0.5591 |
| cursor/bugbot/`default` ⟨manual·standard-v1⟩ | 3 | 92% · 92%–92% | 0.0 | 1.3 | —s | — | — |
| cursor-agent/composer-2.5-fast/`default` | 3 | 94% · 92%–100% | 0.0 | 2.7 | 36.2s | 5,938 | $0.1343 |

| Bug | claude-opus-4-8/`low` | claude-opus-4-8/`medium` | claude-opus-4-8/`high` | claude-opus-4-8/`xhigh` | claude-opus-4-8/`max` | cli/`default` ⟨native⟩ | gpt-5.5/`low` | gpt-5.5/`medium` | gpt-5.5/`high` | gpt-5.5/`xhigh` | bugbot/`default` ⟨manual·standard-v1⟩ | composer-2.5-fast/`default` |
|-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 crit Discount percent not clamped: percent > 1 yields a negative price | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ⚠️ 1/3 |
| C2 crit Per-order coupon subtracted on every line item (multi-line over-discount) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| C3 crit Tax computed on the pre-discount subtotal (wrong tax base) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H1 high Refund returns float money from division instead of rounded integer cents | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H2 high Proration hardcodes /30 and ignores the days_in_month argument | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H3 high Tier boundary off-by-one: quantity at a tier's max falls into the next tier | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 1/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| M1 medi pct truncates the fractional cent instead of rounding half-up | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| M2 medi stack applies the second discount to the original subtotal, not the already-discounted amount | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| M3 medi allocate drops the remainder when splitting an order discount (integer division) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L1 low Loyalty threshold uses > instead of >= (spend exactly at a threshold misqualified) | ✅ 3/3 | ⚠️ 2/3 | ⚠️ 2/3 | ⚠️ 1/3 | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L2 low to_dollars uses integer // 100 and truncates the cents part | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L3 low average_line divides by len with no guard for empty input (ZeroDivisionError) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ⚠️ 1/3 | ⚠️ 2/3 | ❌ 0/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 |

## python-scheduling

### 🏆 Leaderboard (by recall, then cost)

| # | Config | Recall | FP | $/run | Speed |
|--:|--------|:------:|:--:|:-----:|:-----:|
| 🥇 | claude/claude-opus-4-8/high | 100% | 0.0 | $0.2569 | 59s |
| 🥈 | claude/claude-opus-4-8/xhigh | 100% | 0.0 | $0.4444 | 126s |
| 🥉 | codex/gpt-5.5/low | 97% | 0.3 | $0.1715 | 72s |
| 4 | claude/claude-opus-4-8/max | 97% | 0.0 | $0.6618 | 197s |
| 5 | claude/claude-opus-4-8/medium | 94% | 0.0 | $0.2460 | 56s |
| 6 | cursor/bugbot/default ⟨manual⟩ | 94% | 0.0 | — | — |
| 7 | cursor-agent/composer-2.5-fast/default | 92% | 0.0 | $0.2117 | 59s |
| 8 | claude/claude-opus-4-8/low | 92% | 0.0 | $0.2274 | 45s |
| 9 | codex/gpt-5.5/medium | 89% | 0.0 | $0.2199 | 97s |
| 10 | codex/gpt-5.5/xhigh | 89% | 0.0 | $0.4486 | 467s |
| 11 | codex/gpt-5.5/high | 86% | 0.0 | $0.2716 | 126s |
| 12 | coderabbit/cli/default | 67% | 0.0 | — | 124s |

### Metrics (all configs)

| Config | Runs | Recall (mean·min–max) | FP | Bonus | Speed | Out-tok | Est. $ |
|--------|:----:|-----------------------|:--:|:-----:|:-----:|:-------:|:------:|
| claude/claude-opus-4-8/`low` | 3 | 92% · 92%–92% | 0.0 | 0.0 | 44.8s | 3,149 | $0.2274 |
| claude/claude-opus-4-8/`medium` | 3 | 94% · 83%–100% | 0.0 | 0.0 | 55.6s | 4,136 | $0.2460 |
| claude/claude-opus-4-8/`high` | 3 | 100% · 100%–100% | 0.0 | 0.7 | 58.8s | 4,268 | $0.2569 |
| claude/claude-opus-4-8/`xhigh` | 3 | 100% · 100%–100% | 0.0 | 1.0 | 126.5s | 9,850 | $0.4444 |
| claude/claude-opus-4-8/`max` | 3 | 97% · 92%–100% | 0.0 | 0.7 | 196.9s | 14,501 | $0.6618 |
| coderabbit/cli/`default` ⟨native⟩ | 3 | 67% · 67%–67% | 0.0 | 1.0 | 124.4s | — | — |
| codex/gpt-5.5/`low` | 3 | 97% · 92%–100% | 0.3 | 1.7 | 71.7s | 2,608 | $0.1715 |
| codex/gpt-5.5/`medium` | 3 | 89% · 83%–92% | 0.0 | 2.3 | 96.8s | 3,818 | $0.2199 |
| codex/gpt-5.5/`high` | 3 | 86% · 83%–92% | 0.0 | 1.3 | 125.9s | 5,552 | $0.2716 |
| codex/gpt-5.5/`xhigh` | 3 | 89% · 83%–92% | 0.0 | 2.7 | 467.5s | 9,330 | $0.4486 |
| cursor/bugbot/`default` ⟨manual·standard-v1⟩ | 3 | 94% · 92%–100% | 0.0 | 1.7 | —s | — | — |
| cursor-agent/composer-2.5-fast/`default` | 3 | 92% · 83%–100% | 0.0 | 1.7 | 59.2s | 8,568 | $0.2117 |

| Bug | claude-opus-4-8/`low` | claude-opus-4-8/`medium` | claude-opus-4-8/`high` | claude-opus-4-8/`xhigh` | claude-opus-4-8/`max` | cli/`default` ⟨native⟩ | gpt-5.5/`low` | gpt-5.5/`medium` | gpt-5.5/`high` | gpt-5.5/`xhigh` | bugbot/`default` ⟨manual·standard-v1⟩ | composer-2.5-fast/`default` |
|-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 crit overlaps() only checks one direction, so real overlaps are missed → double-booking | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| C2 crit has_conflict skips bookings on a different calendar date → misses midnight-spanning conflicts | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| C3 crit is_past compares a local-naive time against datetime.utcnow() → off by the UTC offset | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 1/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H1 high duration_minutes uses timedelta.seconds (ignores .days) → wrong for intervals ≥ 24h | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H2 high weekly() uses range(1, count+1), excluding the start date it documents as inclusive | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| H3 high free_slots uses `t <= day_end`, emitting a slot starting at/after the day end (off-by-one) | ❌ 0/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 | ⚠️ 1/3 | ⚠️ 2/3 |
| M1 medi parse_hhmm does not validate ranges (accepts hour>23 / minute>59) | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| M2 medi next_available treats a time touching a booking's end as busy (`<=`) → skips a valid slot | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ⚠️ 2/3 | ⚠️ 2/3 | ⚠️ 2/3 | ✅ 3/3 | ⚠️ 1/3 |
| M3 medi monthly() adds timedelta(days=30) per step → drifts off the intended day of month | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L1 low first_booking returns the first-inserted booking, not the earliest by start time | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L2 low Interval.contains uses `<= when <=` (inclusive end); a time at the interval end is wrongly reported inside | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| L3 low busiest_hour calls max() on an empty schedule → ValueError | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 |

