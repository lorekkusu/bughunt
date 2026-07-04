# python-basic · codex/gpt-5.5 · effort=`xhigh`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 06:42:26 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 92% | 92% | 92% |
| False positives | 1.3 | 0 | 3 |
| Bonus real bugs | 4.0 | 3 | 5 |
| Speed (s) | 277.7 | 238.1 | 300.8 |
| Output tokens | 13,603 | 11700 | 14798 |
| Est. cost (USD, API-equiv) | 0.6657 | 0.5521 | 0.7803 |

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
| L2 | low | Overly-broad except swallowing errors | ❌ 0/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Negative transfer amounts accepted — seen in 2/3 runs
- Self-transfer mints money — seen in 2/3 runs
- Negative transfer amounts not rejected — seen in 1/3 runs
- Hard-coded token signing key — seen in 1/3 runs
- Unhandled input/errors cause 500s — seen in 1/3 runs
- /transfer endpoint missing auth — seen in 1/3 runs
- /files download missing auth — seen in 1/3 runs
- Client errors escape as 500s — seen in 1/3 runs
- Broken access control on /transfer — seen in 1/3 runs
- Missing error handling on API inputs — seen in 1/3 runs
