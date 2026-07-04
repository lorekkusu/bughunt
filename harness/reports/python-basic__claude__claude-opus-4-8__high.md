# python-basic · claude/claude-opus-4-8 · effort=`high`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 08:30:32 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 83% | 83% | 83% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 4.0 | 4 | 4 |
| Speed (s) | 58.5 | 47.6 | 67.2 |
| Output tokens | 3,860 | 3650 | 3984 |
| Est. cost (USD, API-equiv) | 0.3074 | 0.2491 | 0.3746 |

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
| L2 | low | Overly-broad except swallowing errors | ❌ 0/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Hardcoded signing secret — seen in 3/3 runs
- Non-constant-time hash comparison — seen in 2/3 runs
- Negative-amount transfer drains destination — seen in 1/3 runs
- Token has no expiry enforcement — seen in 1/3 runs
- Missing auth on transfer + negative/zero amount — seen in 1/3 runs
- Unchecked JSON keys cause 500s — seen in 1/3 runs
- Negative-amount transfer allows theft — seen in 1/3 runs
- Non-constant-time password comparison — seen in 1/3 runs
- Unhandled missing keys / malformed JSON causing 500 — seen in 1/3 runs
