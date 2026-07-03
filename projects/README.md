# projects

Benchmark targets — deliberately buggy code. Each project hides a known set of
planted bugs plus "noise" (safe-but-suspicious code) for measuring false positives.

Grading keys live in `../answers/` (one per project) and are never shown to the
tool under test. Run benchmarks through the harness (see the top-level `README.md`),
which reviews an isolated copy in `projects/.bench/` — not the code in place.

| Project | Lang | Level | Bugs (C/H/M/L) | Focus |
|---------|------|-------|----------------|-------|
| `python-basic` | Python (UV/Flask) | Basic | 3 / 3 / 3 / 3 | Textbook web-backend vulns & correctness bugs |
