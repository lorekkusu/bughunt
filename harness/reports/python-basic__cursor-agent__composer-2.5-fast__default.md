# python-basic · cursor-agent/composer-2.5-fast · effort=`default`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `standard-v1` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-04 08:11:23 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 100% | 100% | 100% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 8.0 | 6 | 10 |
| Speed (s) | 62.1 | 37.6 | 88.3 |
| Output tokens | 8,960 | 6303 | 10907 |
| Est. cost (USD, API-equiv) | 0.2305 | 0.1426 | 0.2925 |

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
| L2 | low | Overly-broad except swallowing errors | ✅ 3/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- Hardcoded signing secret — seen in 1/3 runs
- Tokens issued but never validated — seen in 1/3 runs
- Negative transfer amounts not rejected — seen in 1/3 runs
- Missing request validation (KeyError/TypeError as 500) — seen in 1/3 runs
- Unhandled ValueError from transfers — seen in 1/3 runs
- DB not initialized on WSGI import — seen in 1/3 runs
- Token expiry not enforced — seen in 1/3 runs
- Unhandled missing files (FileNotFoundError as 500) — seen in 1/3 runs
- Hardcoded signing key — seen in 1/3 runs
- Negative transfer amounts allowed — seen in 1/3 runs
- /transfer does not handle ValueError — seen in 1/3 runs
- Login lacks input validation — seen in 1/3 runs
- Missing file reads surface as 500 — seen in 1/3 runs
- No token expiration enforcement — seen in 1/3 runs
- Hardcoded default signing key — seen in 1/3 runs
- Missing authentication on endpoints — seen in 1/3 runs
- No token verification implemented — seen in 1/3 runs
- Negative transfer amounts create money — seen in 1/3 runs
- Non-atomic transfer loses funds on partial failure — seen in 1/3 runs
- Unhandled ValueError in /transfer route — seen in 1/3 runs
- Missing amount type/positivity validation — seen in 1/3 runs
- Unvalidated JSON keys cause 500s — seen in 1/3 runs
- YAML non-dict value corrupts config — seen in 1/3 runs
- Non-constant-time hash comparison — seen in 1/3 runs
