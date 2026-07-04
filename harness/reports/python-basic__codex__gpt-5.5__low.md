# python-basic · codex/gpt-5.5 · effort=`low`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 06:11:34 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 89% | 83% | 92% |
| False positives | 0.3 | 0 | 1 |
| Bonus real bugs | 4.3 | 4 | 5 |
| Speed (s) | 77.2 | 61.9 | 96.2 |
| Output tokens | 2,792 | 2617 | 3070 |
| Est. cost (USD, API-equiv) | 0.1936 | 0.1644 | 0.2170 |

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

- Broken access control on /transfer — seen in 1/3 runs
- No auth on /files download endpoint — seen in 1/3 runs
- Negative transfer amounts allowed — seen in 1/3 runs
- Hard-coded SECRET_KEY in source — seen in 1/3 runs
- Transfer accepts negative amounts — seen in 1/3 runs
- Self-transfer creates money — seen in 1/3 runs
- /transfer lacks authn/authz — seen in 1/3 runs
- /files download lacks authn/authz — seen in 1/3 runs
- Hardcoded token signing key — seen in 1/3 runs
- Negative/zero transfer amount not rejected — seen in 1/3 runs
- Same-account transfer creates money — seen in 1/3 runs
- Transfer endpoint lacks authentication/authorization — seen in 1/3 runs
- File serving endpoint lacks authentication — seen in 1/3 runs
