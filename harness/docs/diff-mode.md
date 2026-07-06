# Diff-mode projects — reviewing a PR instead of a tree

Whole-tree projects ask "find every bug in this code". Diff-mode projects ask
the question real reviewers face: **"what does this PR break?"** — on a repo
too large to read end-to-end, where the interesting defects live one or more
files away from the hunks. The first diff-mode project is `python-crossfile`.

## What a diff-mode project measures

Every planted bug carries a **context distance**:

| Tier | Evidence needed to see the defect |
|------|-----------------------------------|
| `D0` | the diff hunk alone (sanity anchor — everyone should catch these) |
| `D1` | the whole modified file |
| `D2` | a one-hop caller/callee in another, unchanged file |
| `D3` | multi-hop reasoning: global invariants, serialized formats, runtime-registered plugins |

The headline output is the **recall-by-distance curve**. A tool that only reads
the diff decays hard after D1; a tool with real cross-file understanding
(agentic exploration or an index) holds its recall flat. This is the direct
measurement of "does indexing buy anything?".

Two secondary axes:

- **Out-of-diff discovery** — the base tree also contains pre-existing bugs
  (`base_bugs` in the answer key), split `on_path` (inside the files a reviewer
  must read to catch D2/D3 bugs) and `off_path` (cold code). Reporting them is
  neither recall nor FP — a separate "peripheral vision" score. One off-path
  bug is a deliberately *famous* vuln: a tripwire that proves a "diff reviewer"
  actually swept the whole repo.
- **FP under diff pressure** — the diff contains noise items: suspicious-looking
  but correct changes in the same storylines as the real bugs.

## Repo layout

```
projects/<name>/          # the BASE tree (state of `main`) — a normal project
patches/<name>/
├── manifest.toml         # [pr] branch/title/description + [files] added/deleted/renamed
└── overlay/              # head-state copy of every file the PR changes
```

The patch is **never stored**. The runner materializes each review copy as a
real git repo — copy base → `git init` → commit as `main` → branch → copy
`overlay/` over the tree → commit with the PR title/description — so
`git diff main...HEAD` is always produced by git itself and cannot drift.
Authoring stays pleasant: both sides are plain Python trees you can edit and
run tests on (`overlay/` may update tests the PR would realistically update).

## Scoring rules (enforced by the judge prompt + answer-key manifest)

1. Recall/FP are **diff-scoped**: only findings attributable to the PR count.
2. Cross-file bugs (manifest `evidence_file`) credit the find when the reviewer
   names the broken interaction from **either end**.
3. `base_bugs` findings are never FPs and never recall — they land on the
   out-of-diff axis.
4. Matching is by file+symbol, not theme: bug families deliberately share a
   storyline with one correct (noise) instance.

## Authoring checklist (on top of `authoring-advanced.md`)

- [ ] Answer key first; manifest rows carry `distance`, and `evidence_file/_symbol`
      for D2/D3; `base_bugs` rows carry `location: on_path|off_path`.
- [ ] ≤ 2 bugs per root-cause family, plus at most one same-theme noise item.
- [ ] One coherent PR narrative; every bug is a plausible slip inside it.
- [ ] Tests green on base AND head; planted-bug paths deliberately untested.
- [ ] `config.toml` entry gets `review_mode = "diff"` and `patch = "<name>"`.
- [ ] `uv run bench validate -p <name> --tests` passes.

## Running

```bash
uv run bench validate -p python-crossfile --tests   # consistency + both suites
uv run bench run -p python-crossfile --provider codex -m gpt-5.5 -e high
```

Non-native tools get `review_prompt_diff.md` (id `diff-v1`); CodeRabbit runs
native but now diffs against the real `main` — its home turf, making this the
first project where the prompt axis is fair to it. Manual tools (Bugbot) need a
real GitHub PR: materialize a repo with `bench run --keep-scratch` (or by hand
with the steps above), push `main` + the PR branch to a private GitHub repo,
open the PR, then score the captured findings with `bench judge`.
