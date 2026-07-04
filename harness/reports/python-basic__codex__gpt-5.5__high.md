# python-basic · codex/gpt-5.5 · effort=`high`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 06:25:41 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 94% | 92% | 100% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 5.7 | 5 | 7 |
| Speed (s) | 113.7 | 98.9 | 129.7 |
| Output tokens | 4,815 | 3859 | 5620 |
| Est. cost (USD, API-equiv) | 0.2699 | 0.2343 | 0.3262 |

> Costs are **API-equivalent estimates** (what these tokens would cost on the
> OpenAI API), not actual subscription spend. See `pricing.json`.

## Detection stability

Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.

| ID | Severity | Bug | Found |
|----|----------|-----|:-----:|
| C1 | critical | SQL injection | ✅ 3/3 |
| C2 | critical | OS command injection | ✅ 3/3 |
| C3 | critical | Insecure deserialization (pickle) | ✅ 3/3 |
| H1 | high | Path traversal | ✅ 3/3 |
| H2 | high | Weak password hashing (unsalted MD5) | ✅ 3/3 |
| H3 | high | Broken access control (IDOR) | ✅ 3/3 |
| M1 | medium | Race condition / TOCTOU on transfer | ✅ 3/3 |
| M2 | medium | Floating-point money arithmetic | ✅ 3/3 |
| M3 | medium | Off-by-one in pagination | ✅ 3/3 |
| L1 | low | Mutable default argument | ✅ 3/3 |
| L2 | low | Overly-broad except swallowing errors | ⚠️ 1/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Self-transfer creates money — seen in 2/3 runs
- Missing auth on /transfer — seen in 1/3 runs
- Negative transfer amounts — seen in 1/3 runs
- Hardcoded token signing key — seen in 1/3 runs
- Missing auth on /files — seen in 1/3 runs
- Unhandled transfer errors return 500 — seen in 1/3 runs
- Missing file returns 500 not 404 — seen in 1/3 runs
- Transfer endpoint missing auth — seen in 1/3 runs
- Files endpoint missing auth — seen in 1/3 runs
- Transfer accepts negative amounts — seen in 1/3 runs
- Same-account transfer creates money — seen in 1/3 runs
- Non-atomic debit/credit — seen in 1/3 runs
- Transfer endpoint missing auth/ownership check — seen in 1/3 runs
- Negative transfer amount abuse — seen in 1/3 runs
- File download endpoint missing auth/ownership check — seen in 1/3 runs
- Hardcoded default signing secret — seen in 1/3 runs
