# python-basic · cursor/bugbot · effort=`default`

| | |
|---|---|
| Runs | 3 |
| Mode | manual · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 18:25:41 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 89% | 83% | 92% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 4.3 | 3 | 6 |
| Speed (s) | — | — | — |
| Output tokens | — | — | — |
| Est. cost (USD, API-equiv) | — | — | — |

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
| M2 | medium | Floating-point money arithmetic | ❌ 0/3 |
| M3 | medium | Off-by-one in pagination | ✅ 3/3 |
| L1 | low | Mutable default argument | ✅ 3/3 |
| L2 | low | Overly-broad except swallowing errors | ⚠️ 2/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Unauthenticated /transfer endpoint — seen in 1/3 runs
- Unauthenticated /files endpoint — seen in 1/3 runs
- Hardcoded SECRET_KEY — seen in 1/3 runs
- Transfer accepts negative amounts — seen in 1/3 runs
- Unhandled ValueError in do_transfer becomes HTTP 500 — seen in 1/3 runs
- login does not validate JSON shape — seen in 1/3 runs
- Transfer not atomic across accounts — seen in 1/3 runs
- Negative transfer amount allowed — seen in 1/3 runs
- Hardcoded token signing secret — seen in 1/3 runs
- Hardcoded SECRET_KEY enables token forgery — seen in 1/3 runs
- Self-transfer inflates balance via stale in-memory value — seen in 1/3 runs
- Negative transfer amount reverses direction — seen in 1/3 runs
- Unhandled ValueError yields HTTP 500 instead of client error — seen in 1/3 runs
