# python-basic · claude/claude-opus-4-8 · effort=`medium`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 08:26:34 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 86% | 75% | 92% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 4.3 | 4 | 5 |
| Speed (s) | 44.2 | 42.3 | 46.9 |
| Output tokens | 2,991 | 2746 | 3119 |
| Est. cost (USD, API-equiv) | 0.2487 | 0.2425 | 0.2547 |

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
| H3 | high | Broken access control (IDOR) | ⚠️ 2/3 |
| M1 | medium | Race condition / TOCTOU on transfer | ✅ 3/3 |
| M2 | medium | Floating-point money arithmetic | ❌ 0/3 |
| M3 | medium | Off-by-one in pagination | ✅ 3/3 |
| L1 | low | Mutable default argument | ✅ 3/3 |
| L2 | low | Overly-broad except swallowing errors | ⚠️ 2/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Missing negative-amount check in transfer (fund theft) — seen in 1/3 runs
- Hardcoded default signing secret — seen in 1/3 runs
- Non-constant-time password/hash comparison — seen in 1/3 runs
- Unhandled KeyError -> 500 on missing JSON keys — seen in 1/3 runs
- Non-constant-time password comparison — seen in 1/3 runs
- Hard-coded default signing secret — seen in 1/3 runs
- No validation of transfer amount (negative amounts) — seen in 1/3 runs
- Unchecked JSON keys cause 500s — seen in 1/3 runs
- Flask dev server in production — seen in 1/3 runs
- Hardcoded signing secret — seen in 1/3 runs
- Non-constant-time hash comparison in verify_password — seen in 1/3 runs
- Missing positive-amount validation on transfer (negative amount) — seen in 1/3 runs
- No token expiry/validation enforcement — seen in 1/3 runs
