<div align="center">

<img src=".github/bughunt-mark.svg" alt="bughunt logo" width="76" height="76" />

# bughunt

**An honest, open benchmark of AI code-review tools.**

</div>

Single source of truth for benchmarking AI code-review tools (Codex, Claude,
Cursor — bugbot + cursor-agent — and CodeRabbit today; GLM/opencode, Grok,
Greptile, … later) against projects with a known, planted set of bugs.

## Why this exists

I care about code review. As AI writes more of the code — and writes it faster —
picking the right reviewer has quietly become the thing I spend the most effort on,
and the thing I could find the least honest data about. Almost every tool claims
higher recall and less noise than the rest; almost none of them show the numbers.

This isn't a formal or authoritative benchmark, and it may not discriminate as
sharply as I'd like. But even a small, open experiment starts to surface the
questions that actually matter: does more reasoning effort really help? Do the
purpose-built reviewers earn their price? — especially as that price climbs: free
tiers are tightening, and hosted reviews are creeping toward a dollar a pull
request. When review gets expensive, running your own in CI (something like
pr-agent, or a small harness of your own) becomes a real way to keep costs down —
which turns "which model, at what effort, for how much time and money?" into a
question worth measuring.

I don't expect this to be the last word. I just hope it's a useful reference for
anyone wrestling with the same choice — read the results here, or fork it, add your
own projects, and run it yourself.

```
bughunt/
├── projects/     # benchmark targets (deliberately buggy code)
│   ├── python-basic/       # textbook web-backend vulns
│   ├── python-pricing/     # subtle money-math correctness
│   ├── python-scheduling/  # date/time & calendar correctness
│   └── python-crossfile/   # cross-file contracts under a PR diff (diff mode)
├── patches/      # diff-mode PR overlays (base tree lives in projects/)
│   └── python-crossfile/   # manifest.toml (PR metadata) + overlay/ (changed files)
├── answers/      # grading keys — one per project (YAML manifest + writeup)
│   ├── python-basic.md
│   ├── python-pricing.md
│   ├── python-scheduling.md
│   └── python-crossfile.md
└── harness/      # the benchmark tool (Python + UV)
    ├── config.toml
    ├── review_prompt.md        # the ONE prompt sent to every tool/model (id: standard-v1)
    ├── review_prompt_diff.md   # its diff-mode counterpart (id: diff-v1)
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

## License

[MIT](LICENSE) — fork it, add your own projects, and run it yourself.
