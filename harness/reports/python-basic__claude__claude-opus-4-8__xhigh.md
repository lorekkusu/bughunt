# python-basic · claude/claude-opus-4-8 · effort=`xhigh`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 08:37:19 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 86% | 83% | 92% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 3.3 | 3 | 4 |
| Speed (s) | 114.9 | 104.8 | 122.6 |
| Output tokens | 7,810 | 7136 | 8953 |
| Est. cost (USD, API-equiv) | 0.4693 | 0.4271 | 0.5411 |

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
| L2 | low | Overly-broad except swallowing errors | ⚠️ 1/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Non-constant-time hash comparison — seen in 3/3 runs
- Negative-amount transfer allows theft — seen in 1/3 runs
- Hardcoded default signing key — seen in 1/3 runs
- Negative/zero transfer amounts allowed — seen in 1/3 runs
- Hardcoded signing secret — seen in 1/3 runs
- Missing positive-amount validation enables theft via negative transfer — seen in 1/3 runs
- Hardcoded/default signing secret — seen in 1/3 runs
- Unvalidated request fields cause 500s — seen in 1/3 runs
