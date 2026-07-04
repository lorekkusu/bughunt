# python-basic · codex/gpt-5.5 · effort=`medium`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 06:18:17 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 89% | 83% | 92% |
| False positives | 0.7 | 0 | 1 |
| Bonus real bugs | 3.7 | 3 | 5 |
| Speed (s) | 91.8 | 76.1 | 101.3 |
| Output tokens | 3,602 | 2701 | 4073 |
| Est. cost (USD, API-equiv) | 0.2340 | 0.2182 | 0.2544 |

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
| M2 | medium | Floating-point money arithmetic | ⚠️ 2/3 |
| M3 | medium | Off-by-one in pagination | ✅ 3/3 |
| L1 | low | Mutable default argument | ✅ 3/3 |
| L2 | low | Overly-broad except swallowing errors | ❌ 0/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- /transfer lacks authn/authz — seen in 1/3 runs
- Negative-amount transfer — seen in 1/3 runs
- /files route lacks authn — seen in 1/3 runs
- Transfer endpoint missing authentication/ownership check — seen in 1/3 runs
- File download endpoint missing authorization — seen in 1/3 runs
- Transfer allows negative/zero amounts — seen in 1/3 runs
- /transfer missing auth — seen in 1/3 runs
- Self-transfer inflates balance — seen in 1/3 runs
- /files missing auth — seen in 1/3 runs
- Negative/zero transfer amount not rejected — seen in 1/3 runs
- Hardcoded token signing key — seen in 1/3 runs
