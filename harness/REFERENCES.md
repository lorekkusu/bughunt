# References & provenance

Where every non-obvious parameter in this harness comes from, so future edits
have a basis. When you change a value, update its row (and the "verified" date).

Conventions: **local** = observed by running the tool on this machine;
**doc** = an official documentation page; **skill** = the bundled `claude-api`
reference. Dates are when the value was last verified.

## Source links (canonical)

- Claude Code CLI reference — https://code.claude.com/docs/en/cli-reference
- Claude model config / effort — https://code.claude.com/docs/en/model-config
- Codex models — https://developers.openai.com/codex/models
- Codex CLI code review — https://developers.openai.com/codex/use-cases/github-code-reviews
- OpenAI API pricing — https://developers.openai.com/api/docs/pricing
- Anthropic pricing / models — https://platform.claude.com/docs/en/about-claude/models/overview
- Cursor models & pricing — https://cursor.com/docs/models-and-pricing
- Cursor Composer 2.5 model — https://cursor.com/docs/models/cursor-composer-2-5
- Cursor Composer 2.5 changelog — https://cursor.com/en-US/changelog/composer-2-5

The per-parameter tables below cite which of these (or a `local` probe) each value came from.

---

## Codex (subject under test)

| Parameter | Value | Source | Verified |
|-----------|-------|--------|----------|
| CLI version | `codex-cli 0.142.5` | local `codex --version` | 2026-07-03 |
| Invocation mode | `codex exec --json` (not `codex review`) | local `codex review --help` has no `--json`; `codex exec --help` documents `--json` (JSONL events) | 2026-07-03 |
| Why exec, not review | review is purpose-built but reports **no token usage**; exec streams usage. Same standard prompt to every tool keeps the benchmark fair. | local probe | 2026-07-03 |
| Sandbox flag | `-s read-only` | local `codex exec --help` (`--sandbox` values: read-only, workspace-write, danger-full-access) | 2026-07-03 |
| Model select | `-c model=<id>` | local `codex --help` (`-c key=value`, parsed as TOML) | 2026-07-03 |
| Effort select | `-c model_reasoning_effort=<level>` | local (no dedicated `--effort` flag in 0.142.5); community: codex.danielvaughan.com reasoning-effort-tuning | 2026-07-03 |
| Effort values | `minimal, low, medium, high, xhigh` (xhigh is model-dependent); harness sweeps `low, medium, high, xhigh` | community doc + local | 2026-07-03 |
| Token usage schema | `turn.completed.usage = {input_tokens, cached_input_tokens, output_tokens, reasoning_output_tokens}` | local probe of `codex exec --json` | 2026-07-03 |
| Findings text | `item.completed` events with `item.type == "agent_message"` → `item.text` | local probe | 2026-07-03 |
| Auth type | ChatGPT plan login (`~/.codex/auth.json`; requests go to `chatgpt.com/backend-api`) → **not** per-token billed; cost is API-equivalent only | local (`~/.codex/logs_2.sqlite`) | 2026-07-03 |

### Codex models & OpenAI pricing

| Item | Value | Source | Verified |
|------|-------|--------|----------|
| Strongest model | `gpt-5.5` | doc: https://developers.openai.com/codex/models | 2026-07-03 |
| Available models | `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex-spark` (Pro) | doc: same | 2026-07-03 |
| gpt-5.5 price ($/1M) | in 5.00 / cached 0.50 / out 30.00 | doc: https://developers.openai.com/api/docs/pricing | 2026-07-03 |
| gpt-5.4 price ($/1M) | in 2.50 / cached 0.25 / out 15.00 | doc: same | 2026-07-03 |
| gpt-5.4-mini price ($/1M) | in 0.75 / cached 0.075 / out 4.50 | doc: same | 2026-07-03 |

---

## Claude (subject under test — and the judge)

| Parameter | Value | Source | Verified |
|-----------|-------|--------|----------|
| CLI version | `2.1.199 (Claude Code)` | local `claude --version` | 2026-07-03 |
| Headless flag | `-p` / `--print` | doc: https://code.claude.com/docs/en/cli-reference | 2026-07-03 |
| Output format | `--output-format json` (wrapper with `result`, `usage`, `total_cost_usd`) | doc + local probe | 2026-07-03 |
| Model select | `--model <alias-or-id>` (aliases: opus, sonnet, haiku, fable) | doc: cli-reference | 2026-07-03 |
| Permission mode | `--permission-mode bypassPermissions` (no prompts) on the disposable copy. NOT `plan` — plan mode emits a sprawling plan at high effort that the judge can't map to findings (spurious 0% runs) | doc: cli-reference; local diagnosis | 2026-07-03 |
| Effort select | `--effort <level>` | doc: cli-reference (**not** shown in `claude --help`, but documented) | 2026-07-03 |
| Effort values | `low, medium, high, xhigh, max` (available levels depend on model); harness sweeps all five | doc: cli-reference | 2026-07-03 |
| Cost/usage schema | wrapper `total_cost_usd` + `usage.{input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens}` | local probe | 2026-07-03 |
| Cost handling | use `total_cost_usd` directly (already API-equivalent); no pricing.json math needed for claude | local | 2026-07-03 |

### Claude model IDs & pricing

| Item | Value | Source | Verified |
|------|-------|--------|----------|
| Opus 4.8 ID | `claude-opus-4-8` | skill: `claude-api` model table (cached 2026-06-24) | 2026-07-03 |
| Sonnet 5 ID | `claude-sonnet-5` | skill: same | 2026-07-03 |
| Opus 4.8 price ($/1M) | in 5.00 / out 25.00 (cached read ≈ 0.1× = 0.50) | skill: same | 2026-07-03 |
| Sonnet 5 price ($/1M) | in 3.00 / out 15.00 (cached read ≈ 0.30) — **standard rate** | skill: same | 2026-07-03 |
| Sonnet 5 intro rate | 2.00 / 10.00 through 2026-08-31 — **intentionally NOT used** in `pricing.json` | skill: same | 2026-07-03 |

---

## Cursor Agent (subject under test — provider `cursor-agent`)

Distinct from the manual `cursor` provider (Bugbot in the IDE). `cursor-agent` is
Cursor's CLI, driven headlessly like codex/claude.

| Parameter | Value | Source | Verified |
|-----------|-------|--------|----------|
| CLI version | `cursor-agent 2026.06.26-7079533` | local `cursor-agent --version` | 2026-07-03 |
| Headless flag | `-p` / `--print` | local `cursor-agent --help` | 2026-07-03 |
| Output format | `--output-format json` (wrapper: `result`, `usage`, `duration_ms`) | local probe | 2026-07-03 |
| Model select | `--model <id>` (`--list-models` to enumerate) | local | 2026-07-03 |
| No plan mode | we omit `--mode plan` (it can emit a "plan"); run `--force --trust` on the fresh copy | project decision | 2026-07-03 |
| Usage schema | `usage = {inputTokens, outputTokens, cacheReadTokens, cacheWriteTokens}`; no cost field | local probe | 2026-07-03 |
| Cost handling | computed by the harness from usage + pricing.json (Cursor prices) | — | 2026-07-03 |
| Auth | Cursor login (`cursor-agent status`), no API key needed | local | 2026-07-03 |

### Composer models & Cursor pricing

| Item | Value | Source | Verified |
|------|-------|--------|----------|
| composer-2.5 price ($/1M) | in 0.50 / cache-read 0.20 / out 2.50 | doc: https://cursor.com/docs/models-and-pricing | 2026-07-03 |
| composer-2.5-fast price ($/1M) | in 3.00 / cache-read 0.50 / out 15.00 | doc: https://cursor.com/docs/models-and-pricing | 2026-07-03 |
| Context | Composer 2.5 ≈ Opus 4.7 on SWE-Bench Multilingual (79.8 vs 80.5) at ~1/10 the token cost | web (artificialanalysis, buildfastwithai) | 2026-07-03 |

---

## Harness choices

| Choice | Value | Rationale | Source |
|--------|-------|-----------|--------|
| Default runs | 3 | LLM reviews vary run-to-run; 3 is the agreed minimum for a stable read | project decision |
| Standard prompt | `review_prompt.md` (id `standard-v1`) | one identical prompt to every tool/model → fair comparison | this repo |
| Judge model | `claude` CLI, `opus` | different vendor than an OpenAI/Codex subject reduces self-preference bias; LLM-as-judge matches how public benchmarks (withmartian, Tenki) score | project decision; benchmark practice |
| Cost framing | "API-equivalent estimate" | subjects run on flat-rate plans, not per-token billing (see Codex auth row) — the number is what the tokens *would* cost on the API, not actual spend | local |

---

## Cross-platform notes

- **Portable:** the harness is pure Python 3.11+ (stdlib `tempfile`, `pathlib`,
  `subprocess`, `http.server`) — no shell-outs to `git`/`pkill`/etc. Review copies
  go to an OS temp dir via `tempfile.mkdtemp` (works on macOS/Linux/Windows). All
  file I/O pins `encoding="utf-8"` so the emoji/box-drawing in reports don't crash
  on Windows' locale codepage.
- **The one caveat — provider CLIs on Windows:** the adapters invoke `codex`,
  `claude`, and `cursor-agent` via `subprocess.run([...])`. On Windows these tools
  are usually `.cmd`/`.ps1` shims, which `subprocess` can't exec directly without
  `shell=True`. If running on Windows, either call the `.cmd` explicitly or wrap the
  provider command. macOS/Linux need no change.

## How to refresh

- **Prices** — re-check the two pricing docs above, update `pricing.json` (it carries `updated_at` + `sources`) and the rows here.
- **CLI flags / model IDs** — re-fetch the two CLI/doc pages, re-run `--version`, update the rows.
- **Token schema** — re-run a tiny probe (`codex exec --json …`, `claude -p --output-format json …`) and diff the `usage` shape.
