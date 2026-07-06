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
**CodeRabbit** CLI. The coding models and Bugbot share one **standard prompt**
(whole-tree projects) or its **diff-mode counterpart** `diff-v1` (project 4);
CodeRabbit runs its own review engine (marked `native`, and it reports no tokens so
it has speed but no cost). 41 automated configs × 3 runs, plus Bugbot × 4 projects.

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

## Project 4 — `python-crossfile` (PR review on a ~4k-line repo, diff mode)

The first **diff-mode** project: subjects review a 15-file PR
(`git diff main...HEAD`, prompt `diff-v1`) on a ~4k-line task-queue service
instead of a whole tree. 12 planted bugs tiered by **context distance** —
D0 (visible in the hunk) → D1 (whole modified file) → D2 (one-hop caller in
another file) → D3 (multi-hop: runtime-registered plugins, serialized formats,
enum invariants) — plus 6 pre-existing base bugs (scored separately) and 5
in-diff noise items. This is the purpose-built reviewers' **home turf**: a
real PR diffed against a real `main` — Bugbot's and CodeRabbit's native
workflow, with no prompt-axis excuse left.

| # | Config | Recall | D0/D1/D2/D3 | FP | $/run |
|:--:|--------|:------:|:-----------:|:--:|:-----:|
| 🥇 | composer-2.5-fast | 97% | 100/100/100/89 | 0.0 | $0.37 |
| 🥇 | cursor bugbot ⟨manual⟩ | 97% | 100/100/100/89 | 0.0 | — |
| 🥇 | codex gpt-5.5 `xhigh` | 97% | 100/89/100/100 | 0.0 | $1.05 |
| 🥉 | codex gpt-5.5 `high` | 92% | 89/89/100/89 | 0.0 | $0.72 |
| | claude opus-4.8 `max` | 89% | 100/89/100/67 | 0.0 | $1.91 |
| | codex gpt-5.5 `medium` | 83% | 78/89/100/67 | 0.0 | $0.66 |
| | codex gpt-5.5 `low` | 78% | 78/78/100/56 | 0.0 | $0.36 |
| | claude opus-4.8 `high` / `xhigh` | 78% | 100/67/89/56 | 0.0 | $0.91–1.26 |
| | claude opus-4.8 `medium` | 72% | 100/67/89/33 | 0.0 | $0.66 |
| | claude opus-4.8 `low` | 67% | 100/67/89/**11** | 0.0 | $0.59 |
| | coderabbit `cli` ⟨native⟩ | 47% | 100/33/56/**0** | 0.0 | — |

**Findings:**

1. **The first project where effort pays, monotonically.** codex climbs
   78→83→92→97 with effort, opus 67→72→78→89 — no inversion anywhere. When
   bugs require cross-file reasoning, reasoning depth finally buys recall
   (contrast: effort was flat or inverted on projects 1–3).
2. **D3 is the separating axis; D2 is table stakes.** Every config scores
   89–100% at D2 — chasing a one-hop caller via grep is a solved skill. D3
   spreads from **11%** (opus low) to **100%** (codex xhigh): defects reached
   only through runtime plugin registries, persisted file formats, or global
   enum invariants are where cheap configs die. That gap — codex `low` holds
   97% recall *overall* on scheduling but 56% D3 here for the same $0.36 — is
   the measured opportunity for retrieval/indexing assistance.
3. **The hardest bug was same-file, not cross-file.** M2 (`get_job` now
   returns `None`; `update_state` sixty lines down still dereferences blindly)
   was missed at least once by 8 of 10 configs — opus never caught it at
   low/medium/high. The "hunk looks complete, the file says otherwise" trap
   out-discriminated every exotic cross-file plant.
4. **Complementary blind spots.** opus reads hunks precisely (D0 100%
   everywhere) but explores reluctantly — it missed the audit-veto bypass (C3)
   0/3 at both `low` and `high`. codex is the inverse: sloppier in-hunk
   (D0 78% at low/medium) but a perfect 100% D2 at every effort.
5. **Scope discipline is universal.** 30/30 runs: zero false positives, zero
   out-of-diff reports. Nobody flagged the noise items, and nobody touched the
   off-path pickle-RCE tripwire — every tool stayed strictly inside the PR.
6. **composer is the value pick again**: ties codex `xhigh` at 1/3 the cost
   and 2.5× the speed, with the flattest curve of any config.
7. **The purpose-built reviewers bracket the whole field.** Bugbot posts its
   first (co-)win — 97%, a distance curve identical to composer's
   (100/100/100/89, strongly suggesting what runs underneath), 11/12 bugs
   stable at 3/3 including the audit bypass and M2. CodeRabbit, on the same
   home turf, lands last by 20 points (47%, variance 33–67%) with the
   steepest decay of the field: D0 100% → D1 33% → D2 56% → **D3 0/9**,
   missing the audit-bypass critical every round. Same category, same PR,
   opposite ends of the table — the lesson is that a review product's wrapper
   earns nothing by itself: unleash a strong agentic model and you match it;
   constrain the review to a pipeline and you fall off the context cliff.

---

## What it all says

- **composer-2.5-fast is the value standout** — 🥇 on basic and pricing, mid-pack on
  scheduling (92%), **0.0 false positives on all three projects**, at $0.13–0.23/run. On
  this evidence it's the pick for routine bug-finding, and remarkable for its price.
- **"Purpose-built" is not a category — it's a wrapper choice.** CodeRabbit lands
  last or 2nd-from-last on all four projects (83 / 75 / 67 / 47%), and crossfile
  removes its last excuse: on its native diff workflow, against a real base
  branch, it posts the steepest context-distance decay of the field (D3 0%). But
  Bugbot — also purpose-built — co-tops crossfile at 97% with a curve identical
  to composer's. The dividing line isn't specialist-vs-general; it's whether the
  product lets a strong agentic model roam (Bugbot) or locks review into a
  pipeline that never leaves the hunk (CodeRabbit). On the whole-tree projects
  this was already a **reasoning gap, not a retrieval one** (the code was fully
  in view); crossfile shows the same gap widening with context distance.
- **bugbot is the precision play — and finally a (co-)winner.** Clean on every
  project (89 / 92 / 94 / 97%) with **zero false positives anywhere**, it co-tops
  crossfile, its native diff workflow. If a noisy reviewer is worse than a quiet
  one for your workflow, that profile matters more than raw recall. (CodeRabbit
  is the opposite trade: more extras, lower recall.)
- **No model wins everywhere.** composer takes the two correctness-heavy projects;
  opus owns date/time. Match the tool to the domain.
- **Effort ≠ care, and often ≠ value — until the bugs are cross-file.** Higher
  reasoning effort helped only on scheduling (up to `high`) among the whole-tree
  projects; elsewhere it was flat (opus `low` = `max` on pricing) or inverted
  (codex `low` beat `xhigh` on scheduling; codex lost crash catches at
  `high`/`xhigh`). But **crossfile reverses this**: effort climbs monotonically
  for both vendors (codex 78→97, opus 67→89), because multi-hop reasoning is
  exactly what effort buys. The refined rule: effort is wasted on in-context
  bugs and earns its cost only when the evidence is far from the diff.
- **Context distance, not topic, is the frontier.** On crossfile every config
  handles one-hop callers (D2 ≥ 89%), while multi-hop D3 spreads 11–100% and
  cheap configs collapse there. Whole-tree recall numbers overstate what a tool
  will find in a real PR on a real repo — the missing skill is reaching
  evidence that isn't in front of it.
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
