# Authoring harder projects — what makes a bug "advanced"

Basis for authoring discriminating projects. The `python-basic` project is
single-file, syntactic, OWASP-textbook — every tool scores high (composer-2.5-fast
hit 100%). The two correctness-themed projects that followed (`python-pricing`,
`python-scheduling`) are where tools actually separate. To *discriminate* tools you
must plant the classes AI reviewers actually miss.

## What research + our own data agree on

CR-Bench (2026) and the Qodo State-of-AI-Code-Quality report find AI reviewers
"excel at isolated functions but consistently trip on" the classes below. Our own
runs match it: everyone aced the security bugs; the ones that separated tools were
the **non-obvious correctness** bugs (float money `M2`, swallowed-exception `L2`).

| Hard class | Why AI misses it |
|------------|------------------|
| **Cross-file / contract violations** | Only visible when a caller in file A breaks a callee's precondition in file B; single-file analysis can't see it. |
| **Business logic / missing rules** | The defect is an *absent* check/rule, not a suspicious line — you must know the intended behaviour to notice it's gone. |
| **Concurrency / execution order** | Requires reasoning about interleavings (races, TOCTOU, atomicity, deadlock) — current models are weak at execution-path reasoning. |
| **Conditional / path-dependent** | Only triggers under a specific input combination or execution order. |
| **Non-obvious correctness** | Float money, rounding, swallowed errors, resource leaks — real bugs that don't *look* like vulnerabilities, so they don't get flagged. |

Sources: CR-Bench (arXiv 2603.11078), Survey of Software Defect Datasets
(arXiv 2504.17977), Greptile "Best AI Code Review Tools 2026", Qodo report.

## Themes, not just levels

A project's name is `<lang>-<theme>`, where the theme can be a **difficulty level**
(`python-basic`) OR an **important topic** (`python-pricing`, `python-scheduling`,
`python-authz`, `go-concurrency`, `js-async`, …). Difficulty can vary *within* a
theme. This keeps the benchmark organised around what actually matters instead of
an artificial basic/advanced ladder.

Themes, ranked by how well they discriminate tools (✅ = already shipped):

| Theme | Targets | Discrimination |
|-------|---------|----------------|
| `*-concurrency` | races, TOCTOU, atomicity, deadlock, lost updates | ★★★★★ |
| `*-crossfile` ✅ `python-crossfile` | broken invariants / contracts across modules, measured per context distance (diff mode — see `diff-mode.md`) | ★★★★★ |
| `*-money` ✅ `python-pricing` | float/Decimal, rounding, negative/overflow, idempotency | ★★★★ |
| `*-datetime` ✅ `python-scheduling` | intervals, tz/naive-vs-UTC, recurrence, off-by-one slots | ★★★★ |
| `*-authz` | missing/conditional auth, IDOR, workflow-state violations | ★★★★ |
| `*-errors` | swallowed exceptions, resource leaks, partial failure | ★★★ |

Note: an earlier `*-concurrency` attempt was scrapped — famous race/TOCTOU patterns
scored ~100% for every tool, so they don't discriminate despite the ★★★★★ *targets*.
The shipped correctness themes (money, datetime) separate tools far better in practice.

## Design principles for planting advanced bugs

1. **Missing-rule over present-wrong.** The bug is an *absent* lock/check/rule —
   there's no scary line to pattern-match. (E.g. 9 methods lock correctly, 1 doesn't.)
2. **Cross-file only.** The defect manifests only when a caller violates a callee's
   contract; neither file is wrong in isolation.
3. **Conditional / order-dependent.** Triggers under a specific input combo or
   thread interleaving, not on every run.
4. **Intent-dependent.** Requires knowing the domain rule (refunds must be
   idempotent; ship only after payment clears; a limited resource can't oversell).
5. **Raise false-positive pressure.** Add more safe-but-scary code so precision,
   not just recall, separates tools.
6. **Look like production code**, not a CTF puzzle.

## Language caveats

Plant only bugs that are *genuine on the target runtime*. E.g. in CPython, `x += 1`
and `d[k] += 1` are **not** atomic (LOAD/ADD/STORE across the GIL) → real lost
updates; but `list.append` and `dict[k] = v` **are** atomic, so "append without a
lock" is *not* a bug there — don't plant it, and it makes good noise.

## Authoring checklist (per new theme project)

- [ ] Realistic, runnable project under `projects/<lang>-<theme>/` (UV for Python).
- [ ] Plant a known set of bugs skewed toward the hard classes above; keep a mix of
      severities. Record each with file, symbol, impact, fix.
- [ ] Add noise: safe-but-suspicious code (correctly-locked, thread-safe primitives,
      immutable data) to test precision.
- [ ] Write `answers/<lang>-<theme>.md` with the YAML frontmatter manifest
      (`planted_bugs` + `noise`) the judge consumes, then the prose writeup.
- [ ] Add a `[[projects]]` entry in `config.toml`.
- [ ] A basic test that imports/exercises the code and passes (proves it runs).
