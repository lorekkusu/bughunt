<!--
STANDARD REVIEW PROMPT — id: standard-v1

This exact prompt is sent to EVERY tool and model under test, so results are
comparable across providers (codex today; claude, glm, grok, coderabbit,
greptile, … later). Only the HTML comment above is stripped; everything below the
comment is the literal prompt. Changing it invalidates prior results — bump the
prompt_id in config.toml if you do.
-->
Review the code in the current project directory for defects.

Read the source files and report every genuine bug, security vulnerability, and
correctness issue you can find. For each finding, give:

- the file path and line number(s)
- a severity: one of critical, high, medium, or low
- a one- to two-sentence explanation of the problem and its impact

Be precise and thorough. Only report real defects — do not flag stylistic
preferences, and do not flag code that is actually safe. List every finding you
identify.
