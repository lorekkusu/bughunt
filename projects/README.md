# projects

Benchmark targets — deliberately buggy code. Each project hides a known set of
planted bugs plus "noise" (safe-but-suspicious code) for measuring false positives.

Grading keys live in `../answers/` (one per project) and are never shown to the
tool under test. Run benchmarks through the harness (see the top-level `README.md`),
which reviews an isolated copy in `projects/.bench/` — not the code in place.

Projects are named `<lang>-<theme>` — the theme is a difficulty level or an
important topic (see `../harness/docs/authoring-advanced.md`).

| Project | Lang | Theme | Bugs (C/H/M/L) | Focus |
|---------|------|-------|----------------|-------|
| `python-basic` | Python (UV/Flask) | Basic | 3 / 3 / 3 / 3 | Textbook web-backend vulns & correctness bugs |
| `python-pricing` | Python (UV) | Money | 3 / 3 / 3 / 3 | Subtle money-math correctness (float/rounding/tax/discount) |
| `python-scheduling` | Python (UV) | Date/time | 3 / 3 / 3 / 3 | Calendar & datetime correctness (intervals, tz, recurrence) |
| `python-crossfile` | Python (UV) | Cross-file / diff | 3 / 3 / 3 / 3 (+6 base) | PR review on a ~4k-line task-queue service; recall vs context distance D0–D3 (see `../harness/docs/diff-mode.md`) |
