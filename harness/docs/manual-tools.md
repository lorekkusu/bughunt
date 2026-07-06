# Scoring a manual (human-triggered) tool

Some review tools can't be driven headlessly from a CLI — you trigger them in an
IDE or on a PR (e.g. **Cursor Bugbot**, CodeRabbit, Greptile). This one guide
covers all of them: you run the tool by hand, capture its findings, and score
them with `bench judge`. The result lands in the same `results/` format and
shows up in the summary alongside the automated tools.

## 1. Register the provider (once)

The provider must exist in `config.toml`, even though it has no code adapter:

```toml
[providers.cursor]
manual         = true
native         = false          # false = you feed it OUR standard prompt; true = it uses its own
instructions   = "…how to trigger it…"
models         = ["bugbot"]     # a label; the tool's real model may be hidden
efforts        = ["default"]    # a label; most manual tools have no effort knob
default_model  = "bugbot"
default_effort = "default"
```

- `native = false` → the run *is* comparable to the automated tools (same prompt).
  You must paste the contents of `review_prompt.md` into the tool.
- `native = true` → the tool reviews with its **own** prompt. Still useful, but
  label it clearly — it is not an apples-to-apples prompt comparison.

Run `bench providers` to see every provider, its type (auto/manual), and its
`instructions`.

## 2. Trigger the tool

> **Diff-mode projects** (e.g. `python-crossfile`): the checkout to review is a
> *materialized PR repo*, not the project directory, and the prompt is
> `review_prompt_diff.md`. Follow the manual-tool steps in `diff-mode.md`
> instead of step 1 below; steps 3–4 (capture + judge) are identical.

1. Make sure you're reviewing **`projects/python-basic` at the current commit**
   with a **clean working tree** (`git status` clean) — the judge stamps the
   current `code_hash`, so a different checkout would mislabel the result.
2. Trigger the tool on that code.
   - If `native = false`: give it the **exact** text of `review_prompt.md`.
   - If `native = true`: use the tool's own review with no prompt.
3. *(Tool-specific steps go here — fill in what you actually did the first time,
   e.g. "In Cursor: `/bugbot review`, paste the prompt, wait for the panel.")*

## 3. Capture the findings

Copy **all** of the tool's findings into a plain-text file, verbatim — including
file/line/severity where shown. **Do not summarize or filter** (the judge decides
what matches; your editing would bias the score).

```
# e.g. bugbot-run1.txt
```

You can produce **1 or 3 files** — one per manual run. Three is better (it
captures variance, the same reason automated runs default to 3); one is fine to
start.

## 4. Score it

```bash
uv run bench judge --provider cursor --result bugbot-run1.txt
# or three runs:
uv run bench judge --provider cursor \
  --result run1.txt --result run2.txt --result run3.txt
```

The command:
- validates the provider is registered,
- picks the prompt id from `native` (`standard-v1` or `native`),
- runs each file through the judge against the answer key,
- writes `results/python-basic/cursor/bugbot/default.json`,
- copies your raw inputs to `manual-inputs/…` for provenance (they can't be
  regenerated),
- refreshes `reports/summary.md` + `index.html`.

Cost, speed, and token columns will be `—` (a manual tool doesn't report them) —
that's expected; manual tools are compared on recall / precision only.

## 5. Read it

Manual configs are tagged `⟨manual⟩` in the summary so nobody mistakes them for
automated, same-prompt runs. See `glossary.md` for what each metric means.
