---
# Machine-readable manifest consumed by the harness judge.
# Keep this in sync with the prose below.
project: python-basic
planted_bugs:
  - {id: C1, severity: critical, title: "SQL injection",                  file: "src/vault_api/db.py",            symbol: "find_user_by_name"}
  - {id: C2, severity: critical, title: "OS command injection",           file: "src/vault_api/tasks.py",         symbol: "ping_host"}
  - {id: C3, severity: critical, title: "Insecure deserialization (pickle)", file: "src/vault_api/auth.py",       symbol: "load_session"}
  - {id: H1, severity: high,     title: "Path traversal",                 file: "src/vault_api/files.py",         symbol: "read_user_file"}
  - {id: H2, severity: high,     title: "Weak password hashing (unsalted MD5)", file: "src/vault_api/auth.py",     symbol: "hash_password"}
  - {id: H3, severity: high,     title: "Broken access control (IDOR)",   file: "src/vault_api/app.py",           symbol: "account"}
  - {id: M1, severity: medium,   title: "Race condition / TOCTOU on transfer", file: "src/vault_api/banking.py",   symbol: "transfer"}
  - {id: M2, severity: medium,   title: "Floating-point money arithmetic", file: "src/vault_api/banking.py",       symbol: "transfer/apply_interest"}
  - {id: M3, severity: medium,   title: "Off-by-one in pagination",       file: "src/vault_api/utils.py",         symbol: "paginate"}
  - {id: L1, severity: low,      title: "Mutable default argument",       file: "src/vault_api/utils.py",         symbol: "add_tag"}
  - {id: L2, severity: low,      title: "Overly-broad except swallowing errors", file: "src/vault_api/config_loader.py", symbol: "load_config"}
  - {id: L3, severity: low,      title: "Identity vs equality (is)",      file: "src/vault_api/utils.py",         symbol: "is_active"}
noise:
  - {id: N1, title: "Parameterized SQL (safe)",       file: "src/vault_api/db.py",            symbol: "create_user"}
  - {id: N2, title: "basename() on write (safe)",     file: "src/vault_api/files.py",         symbol: "save_file"}
  - {id: N3, title: "Correct HMAC token (safe)",      file: "src/vault_api/auth.py",          symbol: "issue_token"}
  - {id: N4, title: "ast.literal_eval (safe)",        file: "src/vault_api/tasks.py",         symbol: "parse_task_spec"}
  - {id: N5, title: "Non-crypto random jitter (safe)", file: "src/vault_api/tasks.py",        symbol: "backoff_delay"}
  - {id: N6, title: "yaml.safe_load (safe)",          file: "src/vault_api/config_loader.py", symbol: "load_config"}
---

# 🔑 ANSWER KEY — python-basic — DO NOT SHOW TO THE TOOL UNDER TEST

**Target project:** `projects/python-basic/` (in the `bughunt` monorepo)

The tool under test never sees this file: the harness reviews an isolated **copy**
of the project in a scratch dir, so `answers/` is never in the reviewer's context.

12 planted bugs: 3 Critical, 3 High, 3 Medium, 3 Low. Plus intentional **noise**
(safe-but-suspicious code) to measure false positives / precision.

---

## CRITICAL

### C1 — SQL Injection
- **File:** `src/vault_api/db.py` → `find_user_by_name()`
- **What:** Username is interpolated into the SQL string with an f-string:
  `f"SELECT * FROM users WHERE username = '{username}'"`.
- **Impact:** Auth bypass / full DB read-write via `' OR '1'='1` etc. Reachable
  from the unauthenticated `/login` endpoint.
- **Fix:** Use a parameterized query: `conn.execute("... WHERE username = ?", (username,))`.

### C2 — OS Command Injection
- **File:** `src/vault_api/tasks.py` → `ping_host()`
- **What:** `subprocess.run(f"ping -c 1 {host}", shell=True, ...)` with user input.
- **Impact:** RCE via `host = "x; rm -rf /"` etc.
- **Fix:** `subprocess.run(["ping", "-c", "1", host], shell=False, ...)` + validate host.

### C3 — Insecure Deserialization
- **File:** `src/vault_api/auth.py` → `load_session()`
- **What:** `pickle.loads()` on a client-supplied cookie.
- **Impact:** RCE — a crafted pickle runs arbitrary code on load.
- **Fix:** Never unpickle untrusted data. Use a signed JSON token (verify HMAC first).

---

## HIGH

### H1 — Path Traversal (directory traversal)
- **File:** `src/vault_api/files.py` → `read_user_file()` (reachable via `/files/<path:name>`)
- **What:** `os.path.join(UPLOAD_DIR, filename)` with no sanitization; `../../etc/passwd`
  escapes the upload dir. (Note: `save_file()` is SAFE — it uses `basename()`. That
  contrast is intentional.)
- **Impact:** Arbitrary file read.
- **Fix:** Resolve the path and confirm it stays within `UPLOAD_DIR` (e.g. `os.path.realpath` + `commonpath` check), or `basename()` the input.

### H2 — Weak Password Hashing
- **File:** `src/vault_api/auth.py` → `hash_password()`
- **What:** Unsalted `hashlib.md5()` for passwords.
- **Impact:** Trivial offline cracking / rainbow tables on DB compromise.
- **Fix:** Use `bcrypt`/`argon2`/`scrypt` with a per-user salt.

### H3 — Broken Access Control (IDOR)
- **File:** `src/vault_api/app.py` → `account()` route `GET /account/<id>`
- **What:** Returns any account by id with no ownership/authorization check (no token
  is even required).
- **Impact:** Any user can read any account's balance by enumerating ids.
- **Fix:** Require auth, and verify the authenticated user owns the account.

---

## MEDIUM

### M1 — Race Condition / TOCTOU on transfer
- **File:** `src/vault_api/banking.py` → `transfer()`
- **What:** Read balance → check → write, with no locking or atomic transaction.
  Concurrent transfers can overdraw or lose updates (lost-update / double-spend).
- **Impact:** Incorrect balances under concurrency.
- **Fix:** Do it in a single atomic SQL UPDATE with a guard
  (`UPDATE ... SET balance = balance - ? WHERE id = ? AND balance >= ?`) inside one transaction.

### M2 — Floating-point money arithmetic
- **File:** `src/vault_api/banking.py` → `transfer()` / `apply_interest()`
- **What:** Balances and interest use `float`, accumulating rounding errors
  (e.g. `0.1 + 0.2`). Schema also stores `balance REAL`.
- **Impact:** Money drifts by fractions of a cent; reconciliation failures.
- **Fix:** Use `decimal.Decimal` (and store integer cents).

### M3 — Off-by-one in pagination
- **File:** `src/vault_api/utils.py` → `paginate()`
- **What:** `end = start + size + 1` returns `size + 1` items and overlaps the next
  page by one element.
- **Impact:** Duplicated/leaked rows across pages.
- **Fix:** `end = start + size`.

---

## LOW

### L1 — Mutable default argument
- **File:** `src/vault_api/utils.py` → `add_tag(tag, tags=[])`
- **What:** Shared mutable default list persists across calls.
- **Fix:** `tags=None` then `tags = tags or []`.

### L2 — Overly-broad exception swallowing
- **File:** `src/vault_api/config_loader.py` → `load_config()`
- **What:** `except Exception:` silently hides *all* errors (bad path, malformed
  YAML) and quietly returns defaults — misconfig goes unnoticed.
- **Fix:** Catch only expected errors (`FileNotFoundError`, `yaml.YAMLError`), log them.

### L3 — Identity comparison instead of equality
- **File:** `src/vault_api/utils.py` → `is_active()`
- **What:** `user_status is "active"` compares identity, not value. Works by luck via
  string interning for literals but breaks for computed/non-interned strings.
  (The test `test_is_active_true` passes for exactly this reason — masking the bug.)
- **Fix:** `user_status == "active"`.

---

## NOISE / RED HERRINGS (these are NOT bugs — flagging them = false positive)

| # | Location | Why it looks suspicious | Why it's actually fine |
|---|----------|--------------------------|-------------------------|
| N1 | `db.py` `create_user`, `get_account`, `update_balance` | raw SQL | Properly parameterized with `?` |
| N2 | `files.py` `save_file` | filesystem write from input | Uses `os.path.basename()` — traversal-safe |
| N3 | `auth.py` `issue_token` | hand-rolled token | Correct HMAC-SHA256 signing |
| N4 | `tasks.py` `parse_task_spec` | looks like `eval` | `ast.literal_eval` — safe |
| N5 | `tasks.py` `backoff_delay` | `random.random()` | Non-crypto jitter — insecure-RNG flag would be a false positive |
| N6 | `config_loader.py` | YAML loading | Uses `yaml.safe_load` (the L2 bug is the *except*, not the loader) |

Acceptable "extra" nits (won't count against precision, but not planted bugs):
hardcoded `SECRET_KEY` placeholder, missing input validation on JSON bodies.

---

## Scoring sheet

**Recall (detection):**  planted bugs found / 12

| Severity | Found? (C/H/M/L) |
|----------|------------------|
| C1 SQLi | ☐ |
| C2 Cmd inj | ☐ |
| C3 Pickle | ☐ |
| H1 Path traversal | ☐ |
| H2 MD5 pw | ☐ |
| H3 IDOR | ☐ |
| M1 Race/TOCTOU | ☐ |
| M2 Float money | ☐ |
| M3 Off-by-one | ☐ |
| L1 Mutable default | ☐ |
| L2 Broad except | ☐ |
| L3 `is` vs `==` | ☐ |

**Precision (noise):** false positives raised on N1–N6 = ______

Suggested run: point Codex at the repo/branch and ask for a review, then tick
boxes above. Compare severity labels too (did it rank SQLi as critical?).
