# python-basic · claude/claude-opus-4-8 · effort=`low`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 08:23:15 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 78% | 75% | 83% |
| False positives | 0.7 | 0 | 1 |
| Bonus real bugs | 5.0 | 5 | 5 |
| Speed (s) | 35.8 | 33.8 | 38.1 |
| Output tokens | 2,286 | 2043 | 2698 |
| Est. cost (USD, API-equiv) | 0.2108 | 0.2029 | 0.2245 |

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
| H3 | high | Broken access control (IDOR) | ⚠️ 1/3 |
| M1 | medium | Race condition / TOCTOU on transfer | ✅ 3/3 |
| M2 | medium | Floating-point money arithmetic | ❌ 0/3 |
| M3 | medium | Off-by-one in pagination | ✅ 3/3 |
| L1 | low | Mutable default argument | ✅ 3/3 |
| L2 | low | Overly-broad except swallowing errors | ❌ 0/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Hardcoded default signing key — seen in 1/3 runs
- Timing-unsafe password comparison — seen in 1/3 runs
- No upload size enforcement — seen in 1/3 runs
- Unvalidated/negative transfer amount — seen in 1/3 runs
- Unchecked JSON keys cause 500 — seen in 1/3 runs
- Hardcoded default HMAC secret key — seen in 1/3 runs
- Missing auth on /transfer endpoint — seen in 1/3 runs
- No validation of negative/invalid transfer amount — seen in 1/3 runs
- Non-constant-time hash comparison — seen in 1/3 runs
- Unhandled KeyError/500 on malformed JSON input — seen in 1/3 runs
- Hardcoded default signing secret — seen in 1/3 runs
- Negative amount allows theft in transfer — seen in 1/3 runs
- Non-constant-time password/hash comparison — seen in 1/3 runs
- Unhandled malformed input (KeyError/uncaught 500) — seen in 1/3 runs
- Non-dict YAML top-level crashes merge — seen in 1/3 runs
