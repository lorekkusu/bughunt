# python-basic · coderabbit/cli · effort=`default`

| | |
|---|---|
| Runs | 3 |
| Mode | automated · prompt `native` |
| Judge | `opus` (claude) |
| Code hash | `e0072cdb0df6` |
| Created | 2026-07-05 06:17:09 |

## Metrics (across runs)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Recall | 83% | 83% | 83% |
| False positives | 0.0 | 0 | 0 |
| Bonus real bugs | 6.7 | 5 | 8 |
| Speed (s) | 212.8 | 203.7 | 219.1 |
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
| H1 | high | Path traversal | ⚠️ 2/3 |
| H2 | high | Weak password hashing (unsalted MD5) | ✅ 3/3 |
| H3 | high | Broken access control (IDOR) | ⚠️ 2/3 |
| M1 | medium | Race condition / TOCTOU on transfer | ⚠️ 1/3 |
| M2 | medium | Floating-point money arithmetic | ⚠️ 2/3 |
| M3 | medium | Off-by-one in pagination | ✅ 3/3 |
| L1 | low | Mutable default argument | ✅ 3/3 |
| L2 | low | Overly-broad except swallowing errors | ⚠️ 2/3 |
| L3 | low | Identity vs equality (is) | ✅ 3/3 |

## Bonus findings (real, not planted)

- SQLite foreign keys not enforced — seen in 2/3 runs
- Hardcoded SECRET_KEY — seen in 2/3 runs
- Non-dict YAML crashes config merge — seen in 1/3 runs
- Non-constant-time password comparison — seen in 1/3 runs
- Self-transfer mints funds — seen in 1/3 runs
- Negative transfer amount not rejected — seen in 1/3 runs
- /transfer endpoint lacks auth/ownership checks — seen in 1/3 runs
- login KeyError on missing fields — seen in 1/3 runs
- update_balance ignores rowcount (silent no-op on missing account) — seen in 1/3 runs
- transfer allows non-positive amounts — seen in 1/3 runs
- login handler unvalidated JSON body — seen in 1/3 runs
- config merge fails on non-mapping YAML — seen in 1/3 runs
- config.yaml not gitignored — seen in 1/3 runs
- Non-constant-time password hash comparison — seen in 1/3 runs
- Hardcoded SECRET_KEY committed literal — seen in 1/3 runs
- Missing non-positive amount guard in transfer — seen in 1/3 runs
- Missing auth/ownership check on /transfer endpoint — seen in 1/3 runs
- config.yaml tracked / sqlite sidecars not ignored — seen in 1/3 runs
