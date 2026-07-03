# bughunt — results

An informal, honest benchmark of AI code-review tools. Each project hides a known
set of planted bugs; every tool gets the **same standard prompt** and is scored by
an **LLM-as-judge** against the answer key. Recall = planted bugs found. Costs are
**API-equivalent estimates** (what the tokens would cost on the API), not actual
subscription spend. Default 3 runs per config. See `harness/` for how to reproduce.

> Caveats: small, fully-readable projects; a single LLM judge; one language so far.
> Treat as a directional signal, not gospel.

---

## Project 1 — `python-basic` (textbook web-backend bugs)

12 planted bugs (SQLi, command injection, pickle RCE, path traversal, IDOR, weak
hash, TOCTOU, float money, off-by-one, mutable default, broad-except, `is` vs `==`).

| # | Config | Recall | FP | $/run |
|:--:|--------|:------:|:--:|:-----:|
| 🥇 | composer-2.5 | 100% | 0 | $0.065 |
| 🥈 | composer-2.5-fast | 100% | 0 | $0.216 |
| 🥉 | claude sonnet-5 `max` | 100% | 0 | $1.23 |
| | codex gpt-5.5 `medium` | 94% | 0.7 | $0.27 |
| | cursor bugbot (manual) | 89% | 0 | — |
| | claude opus-4-8 (best) | 89% | 0 | $0.51 |
| | codex/claude (low tiers) | 81–86% | — | — |

**Findings:** near-saturated at the top — every strong config lands 86–100%. The
only discriminators were the two **non-flashy correctness** bugs (float-for-money,
swallowed-exception): codex `low` missed float money 0/3; composer got both 3/3.
Effort mostly plateaus (codex 86→94% and back). To *reach* 100% the others need
their priciest setting (sonnet `max`, $1.23) — composer just gets it for $0.065.

---

## Project 2 — `python-pricing` (subtle money-math correctness)

12 planted bugs, all **subtle correctness** (no famous vulns): unclamped discount →
negative price, per-line coupon over-charge, tax on the wrong base, float-money
refund, hardcoded `/30` proration, tier boundary off-by-one, truncation vs rounding,
wrong discount base, dropped remainder, `>` vs `>=`, float equality, empty-input crash.

| # | Config | Recall | FP | $/run |
|:--:|--------|:------:|:--:|:-----:|
| 🥇 | composer-2.5 | 100% | 0 | $0.027 |
| 🥈 | composer-2.5-fast | 100% | 0 | $0.14 |
| 🥉 | claude sonnet-5 `high` | 78% | 0 | $0.39 |
| | claude sonnet-5 `low` | 72% | 0 | $0.20 |
| | claude sonnet-5 `xhigh` | 69% | 0 | $0.47 |
| | codex gpt-5.5 `xhigh` | 69% | 0.7 | $0.61 |
| | codex gpt-5.5 `low`/`med`/`high` | 61% | — | $0.19–0.32 |

**Findings — this one actually discriminates:**

1. **Wide separation.** composer 100%; everyone else ≤ 78%. A 22-point gap, unlike
   basic's cluster.
2. **Effort doesn't help — and can hurt.** codex is flat at 61% from `low` to
   `high`, only 69% at `xhigh`. sonnet is 78% at `high` but *drops* to 69% at
   `xhigh`. Reasoning depth doesn't buy subtle-correctness catches.
3. **Cost inversion.** The cheapest tool (composer, $0.027) is the best; the most
   expensive run (codex `xhigh`, $0.61) gets 69%. Care is intrinsic, not a knob.
4. **Consistently missed by everyone but composer:** float equality on money,
   tax-on-pre-discount base (cross-function), unclamped discount → negative price.

---

## What it all says

- **composer-2.5 is the standout** — cheapest *and* most thorough, winning both
  projects at a fraction of the cost. On this evidence it's the value pick for
  routine bug-finding, and unusually strong for its price.
- **The discriminating axis is subtle correctness**, not exotic topics. Famous
  vulnerabilities (basic) are near-saturated; famous patterns don't separate tools
  at all (an earlier concurrency project scored everyone ~100% and was scrapped);
  it's the quiet "should-be-right-but-easy-to-get-wrong" money-math bugs that
  reveal a real gap.
- **Effort ≠ care.** Paying for higher reasoning effort does little for subtle
  correctness — thoroughness looks like a model property, not a setting.

Method, provenance, and how to add tools/projects: `harness/docs/` and
`harness/REFERENCES.md`.
