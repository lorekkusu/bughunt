# python-basic · claude/claude-opus-4-8 · effort=`max`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 08:49:20 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 86% | 83% | 92% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 4.3 | 3 | 5 |
| Speed (s) | 202.3 | 151.6 | 231.4 |
| Output tokens | 14,245 | 10834 | 16222 |
| Est. cost (USD, API-equiv) | 0.6657 | 0.4885 | 0.7544 |

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
| M2 | medium | Floating-point money arithmetic | ⚠️ 1/3 |
| M3 | medium | Off-by-one in pagination | ✅ 3/3 |
| L1 | low | Mutable default argument | ✅ 3/3 |
| L2 | low | Overly-broad except swallowing errors | ❌ 0/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Negative-amount transfer allows money theft — seen in 1/3 runs
- Hardcoded signing key — seen in 1/3 runs
- Non-constant-time hash comparison in verify_password — seen in 1/3 runs
- Hardcoded token signing key — seen in 1/3 runs
- Negative-amount transfer allows theft — seen in 1/3 runs
- Non-constant-time password comparison — seen in 1/3 runs
- load_config crashes on non-dict YAML — seen in 1/3 runs
- Missing input validation on request bodies (KeyError → 500) — seen in 1/3 runs
- Negative transfer amount enables fund theft — seen in 1/3 runs
- Hardcoded signing key never sourced from environment — seen in 1/3 runs
- Config load crashes on non-dict YAML — seen in 1/3 runs
- Non-constant-time hash comparison — seen in 1/3 runs
- Missing request-input validation (KeyError/TypeError -> 500) — seen in 1/3 runs
