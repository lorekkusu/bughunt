# bughunt — results

An informal, honest benchmark of AI code-review tools. Each project hides a known
set of planted bugs, and every tool is scored by an **LLM-as-judge** (Claude Opus,
headless) against the answer key. Recall = planted bugs found. FP = false positives
per run. Costs are **API-equivalent estimates** (what the measured tokens would cost
on the API), not actual subscription spend. Default **3 runs** per config; a bug
counts by stability (found every run / some / never). See `harness/` for how to
reproduce.

**Subjects:** codex `gpt-5.5` (efforts low→xhigh), claude `opus-4.8` (low→max),
cursor-agent `composer-2.5-fast`, cursor **bugbot** (run manually), and
**CodeRabbit** CLI. The coding models and Bugbot share one **standard prompt**;
CodeRabbit runs its own review engine (marked `native`, and it reports no tokens so
it has speed but no cost). 30 automated model configs × 3 runs, plus Bugbot and
CodeRabbit × 3 projects.

> Caveats: small, fully-readable projects; a single LLM judge; one language (Python)
> so far; `native` tools aren't directly comparable on the prompt axis; costs are
> list-price estimates, not billed spend. Treat as a directional signal, not gospel.

---

## Project 1 — `python-basic` (textbook web-backend bugs)

12 planted bugs: SQLi, command injection, pickle RCE, path traversal, IDOR, unsalted
MD5, TOCTOU transfer, float-for-money, off-by-one pagination, mutable default,
broad-except, `is` vs `==`.

| # | Config | Recall | FP | $/run |
|:--:|--------|:------:|:--:|:-----:|
| 🥇 | composer-2.5-fast | 100% | 0.0 | $0.23 |
| 🥈 | codex gpt-5.5 `high` | 94% | 0.0 | $0.27 |
| 🥉 | codex gpt-5.5 `xhigh` | 92% | 1.3 | $0.67 |
| | codex gpt-5.5 `low` / `medium` | 89% | 0.3–0.7 | $0.19–0.23 |
| | cursor bugbot ⟨manual⟩ | 89% | 0.0 | — |
| | claude opus-4.8 (best: `medium`) | 86% | 0.0 | $0.25 |
| | coderabbit `cli` ⟨native⟩ | 83% | 0.0 | — |
| | claude opus-4.8 `low` | 78% | 0.7 | $0.21 |

**Findings:** near-saturated at the top — the famous vulnerabilities (SQLi, command
injection, pickle, path traversal, MD5, TOCTOU) are caught 3/3 by essentially
everyone. The whole spread comes from two **non-flashy** bugs: **float-for-money**
(opus missed it almost entirely — 0/3 at every effort except one lucky `max` run;
codex needed `high`+ to lock it) and **broad-except** (only composer got it 3/3;
most configs never did). Effort plateaus or inverts — codex peaks at `high` (94%)
and *drops* at `xhigh` (92%, and picks up 1.3 FP). composer reaches 100% for $0.23
while opus can't clear 86% even at `max` ($0.67). **CodeRabbit**, the one
purpose-built reviewer, lands at 83% (2nd from bottom) — though it flags the most
*extra* real issues of anyone (bonus 6.7), so it's thorough but not accurate.

---

## Project 2 — `python-pricing` (subtle money-math correctness)

12 planted bugs, all **subtle correctness**, no famous vulns: unclamped discount →
negative price, per-line coupon over-charge, tax on the wrong base, float-money
refund, `/30`-vs-`days_in_month` proration, tier boundary off-by-one, truncate-vs-
round, wrong discount base, dropped remainder, `>` vs `>=`, cents truncation,
empty-input crash.

| # | Config | Recall | FP | $/run |
|:--:|--------|:------:|:--:|:-----:|
| 🥇 | composer-2.5-fast | 94% | 0.0 | $0.13 |
| 🥈 | claude opus-4.8 `low` | 92% | 0.0 | $0.23 |
| | cursor bugbot ⟨manual⟩ | 92% | 0.0 | — |
| | claude opus-4.8 `max` | 92% | 0.0 | $0.93 |
| | codex gpt-5.5 `medium` | 89% | 0.3 | $0.27 |
| | claude opus-4.8 `medium` / `high` | 89% | 0.0 | $0.28–0.31 |
| | codex gpt-5.5 `low` / `high` / `xhigh` | 83% | 0.0 | $0.27–0.56 |
| | coderabbit `cli` ⟨native⟩ | 75% | 0.3 | — |

**Findings:**

1. **One bug beats everybody.** The unclamped discount that yields a *negative
   price* (C1) was missed **0/3 by every codex and every opus config**, by Bugbot,
   and by CodeRabbit; only composer caught it, and only 1/3. It's the single hardest
   item in the suite — plausibly because "should this function validate its input?"
   is a judgment call, not a mechanical defect.
2. **Effort barely moves it — and isn't monotonic.** codex is 83% at `low`,
   `high`, and `xhigh` (with a 89% blip at `medium`); opus `low` (92%) *ties* opus
   `max` (92%) — for **4× the cost** ($0.23 vs $0.93). Reasoning depth buys nothing here.
3. **codex has a crash blind spot.** The empty-input `ZeroDivisionError` (L3) it
   caught at `low`/`medium` but **missed 0/3 at `high` and `xhigh`** — more effort,
   fewer catches.
4. **CodeRabbit comes last** (75%) — the specialist reviewer is out-recalled by
   every general model configuration on the subtle-money project.

---

## Project 3 — `python-scheduling` (date/time & calendar correctness)

12 planted bugs: one-directional overlap, cross-date conflict miss, naive-vs-UTC
comparison, `timedelta.seconds` (drops `.days`), off-by-one recurrence, trailing
free-slot, no range validation, touching-end busy, 30-day "months", insertion-order
"first", inclusive-end `contains`, empty-schedule `max()` crash.

| # | Config | Recall | FP | $/run |
|:--:|--------|:------:|:--:|:-----:|
| 🥇 | claude opus-4.8 `high` | 100% | 0.0 | $0.26 |
| 🥈 | claude opus-4.8 `xhigh` | 100% | 0.0 | $0.44 |
| 🥉 | codex gpt-5.5 `low` | 97% | 0.3 | $0.17 |
| | claude opus-4.8 `max` | 97% | 0.0 | $0.66 |
| | cursor bugbot ⟨manual⟩ | 94% | 0.0 | — |
| | composer-2.5-fast | 92% | 0.0 | $0.21 |
| | codex gpt-5.5 `high` | 86% | 0.0 | $0.27 |
| | coderabbit `cli` ⟨native⟩ | 67% | 0.0 | — |

**Findings:** the one project where **opus leads** — and the one where **effort
actually helps**, but only up to `high` (low 92% → high 100%), then plateaus and
dips at `max` (97%). For codex it *inverts hard*: `low` scores **97% at $0.17 in
72s**, while `xhigh` scores **89% at $0.45 in 467s** — six times slower and worse.
codex also has a blind spot on the empty-schedule crash (L3): 0/3 at `medium`,
`high`, and `xhigh`, while opus, composer, and bugbot all catch it. The trailing
free-slot off-by-one (H3) is flaky for everyone — the genuine coin-flip of the set.
**CodeRabbit is last by a clear margin (67%)** — nearly 20 points below the field.

---

## What it all says

- **composer-2.5-fast is the value standout** — 🥇 on basic and pricing, mid-pack on
  scheduling (92%), **0.0 false positives on all three projects**, at $0.13–0.23/run. On
  this evidence it's the pick for routine bug-finding, and remarkable for its price.
- **The purpose-built review products don't win.** CodeRabbit — a dedicated AI code
  reviewer — lands last or 2nd-from-last on all three (83 / 75 / 67%), and Bugbot,
  though clean, never tops a project either. The general coding models and agents
  out-recall the specialist tools. And because the whole (small) project is in front
  of every tool, this is a **reasoning gap, not a retrieval one** — a tool that
  misses a bug it can fully see won't do *better* on a larger codebase, only worse.
- **bugbot is the precision play** — never wins a project (89 / 92 / 94%) but
  **never adds a single false positive**, and its extras are real. If a noisy
  reviewer is worse than a quiet one for your workflow, that profile matters more
  than raw recall. (CodeRabbit is the opposite trade: more extras, lower recall.)
- **No model wins everywhere.** composer takes the two correctness-heavy projects;
  opus owns date/time. Match the tool to the domain.
- **Effort ≠ care, and often ≠ value.** Higher reasoning effort helped only on
  scheduling, only up to `high`. Elsewhere it was flat (opus `low` = `max` on
  pricing) or inverted (codex `low` beat `xhigh` on scheduling; codex lost crash
  catches at `high`/`xhigh`). The `xhigh`/`max` tiers almost never earned their
  3–5× cost or their multi-minute latency. Thoroughness reads as a model property,
  not a knob you can turn up.
- **The discriminating axis is subtle correctness**, not exotic topics. Famous
  vulnerabilities (basic) near-saturate; famous *patterns* don't separate tools at
  all (an earlier concurrency project scored everyone ~100% and was scrapped). The
  sharpest single discriminators here were the quiet ones: a discount that goes
  negative, a swallowed exception, a float where cents belong.
- **False positives stayed rare and small.** Almost every FP > 0 came from codex —
  spread across `low`, `medium`, and `xhigh` (up to 1.3 on basic `xhigh`), not
  clustered at any one tier — plus a single opus `low` run and one CodeRabbit
  pricing run (0.3). composer and bugbot never produced one across all three projects.

Method, provenance, and how to add tools/projects: `harness/docs/` and
`harness/REFERENCES.md`. Full per-bug tables: `harness/reports/summary.md`.
