<!--
DIFF REVIEW PROMPT — id: diff-v1

The prompt for diff-mode projects (review_mode = "diff" in config.toml): the
subject reviews a PR in a materialized git repo, not a whole tree. This exact
prompt is sent to EVERY non-native tool so results stay comparable. Only this
HTML comment is stripped; everything below is the literal prompt. Changing it
invalidates prior diff-mode results — bump diff_prompt_id in config.toml if
you do.
-->
Review the pull request in the current git repository.

The PR branch is checked out. The base branch is `main`. Use
`git diff main...HEAD` to see what the PR changes and `git log main..HEAD`
for the PR description; read any other files in the repository you need for
context.

Report every genuine bug, security vulnerability, or correctness issue that
this PR introduces or exposes. For each finding, give:

- the file path and line number(s)
- a severity: one of critical, high, medium, or low
- a one- to two-sentence explanation of the problem and its impact

Scope: your findings should be attributable to this PR's changes. If you
notice a genuine pre-existing bug in code the PR does not touch, you may
report it in a separate section titled "Pre-existing issues" at the end,
clearly apart from the PR findings.

Be precise and thorough. Only report real defects — do not flag stylistic
preferences, and do not flag code that is actually safe.
