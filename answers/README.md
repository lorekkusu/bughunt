# answers

🔑 Grading keys for the projects in `../projects/`.

**Never give these files to the tool under test.** The harness enforces this by
reviewing an isolated copy of a project (in `projects/.bench/`) that does not
contain this folder; the keys are used only afterwards, by the judge, to score.

Each key starts with a **YAML frontmatter manifest** (the machine-readable list of
planted bugs + noise that the judge consumes), followed by the human-readable
writeup: every planted bug (file, function, impact, fix), the intended noise, and a
scoring sheet.

## Keys

| Key | Matches project | Bugs (C/H/M/L) |
|-----|-----------------|----------------|
| `python-basic.md` | `projects/python-basic` | 3 / 3 / 3 / 3 |
| `python-pricing.md` | `projects/python-pricing` | 3 / 3 / 3 / 3 |
| `python-scheduling.md` | `projects/python-scheduling` | 3 / 3 / 3 / 3 |
| `python-crossfile.md` | `projects/python-crossfile` + `patches/python-crossfile` | 3 / 3 / 3 / 3 (+6 base, diff-mode) |
