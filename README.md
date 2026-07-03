# bughunt

Single source of truth for benchmarking AI code-review tools (Codex, Claude, …)
against projects with a known, planted set of bugs.

```
bughunt/
├── projects/     # benchmark targets (deliberately buggy code)
│   └── python-basic/
├── answers/      # grading keys — one per project (with a machine-readable manifest)
│   └── python-basic.md
└── harness/      # the benchmark tool (Python + UV)
    ├── config.toml
    ├── bench/
    └── reports/  # generated reports (gitignored by default)
```

## How isolation works

The tool under test **never sees `answers/`**. For each run the harness copies the
target project into a throwaway `projects/.bench/<run>/` (gitignored), turns it into
a fresh single-commit git repo, and points the reviewer at *that copy*. The answer
key is only used afterwards by the judge to score the output.

> Don't run a review tool directly at the repo root — always go through the harness.

## Quick start

```bash
cd harness
uv sync
uv run bench                 # interactive: pick project / provider / model / effort
```

Non-interactive / scriptable:

```bash
uv run bench --project python-basic --provider codex --model gpt-5.5 --effort high
uv run bench --provider codex -m gpt-5.5 -e xhigh --runs 3
```

Scoring is done by an **LLM-as-judge** (the local `claude` CLI, headless — no API
key needed; a different vendor than an OpenAI/Codex subject). It reports recall
(planted bugs found), false positives (safe "noise" wrongly flagged), and bonus
real bugs found that weren't planted.

## Adding things

- **New project:** create `projects/<lang>-<level>/`, plant bugs, add
  `answers/<lang>-<level>.md` (with the YAML frontmatter manifest), and add a
  `[[projects]]` entry in `harness/config.toml`. Project and answer key are one
  commit — they can never drift.
- **New tool:** add `harness/bench/providers/<name>.py` implementing `run_review`,
  register it in `providers/__init__.py`, and add a `[providers.<name>]` block.
- **New model / effort:** just edit the lists in `harness/config.toml`.
