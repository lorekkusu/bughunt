# bughunt

Single source of truth for benchmarking AI code-review tools (Codex, Claude, and
Cursor — bugbot + cursor-agent — today; GLM/opencode, Grok, CodeRabbit, Greptile,
… later) against projects with a known, planted set of bugs.

## Why this exists

This is an informal benchmark, not a rigorous one — and it's honest about that. I
lean on AI code review in my own day-to-day workflow, so I genuinely need to know
which tools actually catch real bugs. But most public comparisons are opaque: the
prompt, the test code, and the scoring are rarely shown, so there's no way to tell
what was really measured. Rather than trust numbers I can't inspect, I built my own
test where everything is in the open — the exact projects, the planted bugs, the
one shared prompt, and how each finding is graded. Take the results as one person's
transparent experiment, not an authoritative ranking.

```
bughunt/
├── projects/     # benchmark targets (deliberately buggy code)
│   ├── python-basic/       # textbook web-backend vulns
│   ├── python-pricing/     # subtle money-math correctness
│   └── python-scheduling/  # date/time & calendar correctness
├── answers/      # grading keys — one per project (YAML manifest + writeup)
│   ├── python-basic.md
│   ├── python-pricing.md
│   └── python-scheduling.md
└── harness/      # the benchmark tool (Python + UV)
    ├── config.toml
    ├── review_prompt.md   # the ONE prompt sent to every tool/model (id: standard-v1)
    ├── pricing.json       # API list prices, for cost ESTIMATES
    ├── REFERENCES.md      # provenance: where every parameter/flag/price comes from
    ├── bench/
    ├── results/           # committed structured results (one json per config)
    └── reports/           # generated summary.md + index.html (+ per-config .md)
```

## How it works

For each **config** (`project × provider × model × effort`) the harness runs **3
rounds** by default (LLM reviews vary run-to-run, so a single run isn't
trustworthy). Each round:

1. copies the project into a throwaway `projects/.bench/<run>/` (gitignored) — the
   tool under test **never sees `answers/`**;
2. runs the tool with the **shared standard prompt** (`review_prompt.md`) so every
   tool/model is measured on equal footing;
3. an **LLM-as-judge** (the local `claude` CLI, headless — no API key) scores the
   findings against the answer-key manifest.

Results are aggregated into recall (with per-bug stability: **✅** found every run,
**⚠️** some runs, **❌** never), false positives, bonus real bugs, speed, tokens,
and an **estimated cost**.

> **Costs are API-equivalent estimates** — what the measured tokens *would* cost on
> the OpenAI API (see `pricing.json`), **not** actual subscription/plan spend.
> Tools/models that don't report token usage simply skip the cost column.

## Quick start

```bash
cd harness
uv sync

# interactive: pick project / provider / model / effort  (3 runs)
uv run bench run

# scriptable
uv run bench run --project python-basic --provider codex --model gpt-5.5 --effort high

# sweep every effort for a model (low..xhigh) — the cost/quality tradeoff
uv run bench run --provider codex --model gpt-5.5 --all-efforts

# list every tool, whether it's automated or manual, and how to run it
uv run bench providers

# score a manual (human-triggered) tool's findings — see docs/manual-tools.md
uv run bench judge --provider cursor --result findings.txt

# rebuild + preview the cross-config comparison as a web page
uv run bench summary --serve
```

Automated tools (codex, claude, cursor-agent) are driven headlessly and get the
same standard prompt. Manual tools (Cursor Bugbot, …) are triggered by hand and scored with
`bench judge` — see [`harness/docs/manual-tools.md`](harness/docs/manual-tools.md).
New to the metrics? [`harness/docs/glossary.md`](harness/docs/glossary.md).

Re-running a config is **skipped** if a fresh result already exists (same code +
enough runs); pass `--force` to redo it. Change the project's code and the skip key
(a content hash) changes automatically, so stale results never mask a re-test.

## Adding things

- **New project:** name it `<lang>-<theme>` — the theme can be a difficulty level
  (`python-basic`) or an important topic (`python-authz`, `python-money`, …).
  Create `projects/<lang>-<theme>/`, plant bugs, add `answers/<lang>-<theme>.md`
  (with the YAML frontmatter manifest), and a `[[projects]]` entry in
  `harness/config.toml`. See [`harness/docs/authoring-advanced.md`](harness/docs/authoring-advanced.md)
  for what makes a bug "advanced" and how to plant discriminating ones.
- **New tool:** add `harness/bench/providers/<name>.py` implementing `run_review`
  (return findings text + optional token usage), register it in
  `providers/__init__.py`, add a `[providers.<name>]` block. It automatically uses
  the same standard prompt.
- **New model / effort:** edit the lists in `harness/config.toml`.
- **Prices:** refresh `harness/pricing.json` (it carries `updated_at` + source).
- **Provenance:** every parameter, CLI flag, model ID, and price is sourced in
  `harness/REFERENCES.md` (with the doc/probe it came from and a verified date).
  When you change a value anywhere, update its row there too.
