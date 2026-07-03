"""LLM-as-judge scoring via the local `claude` CLI (headless).

Given the answer-key manifest (planted bugs + noise) and a tool's raw findings,
ask Claude to decide — semantically, tolerant of wording and line-number drift —
which planted bugs were found, which noise items were wrongly flagged (false
positives), and which genuine bugs were found that were not planted (bonus).
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field


class JudgeError(RuntimeError):
    pass


@dataclass
class Verdict:
    planted: list[dict] = field(default_factory=list)          # {id, found, evidence}
    false_positives: list[dict] = field(default_factory=list)  # {noise_id, evidence}
    bonus_bugs: list[dict] = field(default_factory=list)       # {title, evidence}
    raw_judge_output: str = ""

    @property
    def found_ids(self) -> list[str]:
        return [p["id"] for p in self.planted if p.get("found")]

    @property
    def missed_ids(self) -> list[str]:
        return [p["id"] for p in self.planted if not p.get("found")]


_PROMPT = """\
You are grading an AI code reviewer against a fixed answer key. Judge by MEANING,
not wording: the reviewer may phrase things differently, use different severity
labels, or cite slightly different line numbers. A planted bug counts as FOUND if
the reviewer clearly describes that same underlying defect.

## Planted bugs (the reviewer SHOULD find these)
{planted}

## Noise (SAFE code — flagging any of these as a real defect is a FALSE POSITIVE)
{noise}

## The reviewer's raw output
<<<REVIEW
{review}
REVIEW

## Your task
Return ONLY a JSON object, no prose, with this exact shape:
{{
  "planted": [{{"id": "C1", "found": true, "evidence": "<short quote or ''>"}}, ...],
  "false_positives": [{{"noise_id": "N4 or null", "evidence": "<short quote>"}}, ...],
  "bonus_bugs": [{{"title": "<short>", "evidence": "<short quote>"}}, ...]
}}

Rules:
- Include EVERY planted id exactly once in "planted".
- "false_positives": only findings that call SAFE/noise code a real defect. A
  finding that matches a planted bug or a genuine real bug is NOT a false positive.
- "bonus_bugs": genuine defects the reviewer raised that are not in the planted
  list and are not false positives.
"""


def _fmt_items(items: list[dict]) -> str:
    lines = []
    for it in items:
        loc = it.get("file", "")
        sym = it.get("symbol", "")
        where = f" [{loc}::{sym}]" if loc else ""
        sev = it.get("severity")
        sev = f" ({sev})" if sev else ""
        lines.append(f"- {it['id']}{sev}: {it['title']}{where}")
    return "\n".join(lines)


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # strip ```json ... ``` fences
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))
    # fall back to first {...last }
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise JudgeError("could not parse JSON from judge output")


def score(manifest: dict, review_output: str, model: str = "opus") -> Verdict:
    prompt = _PROMPT.format(
        planted=_fmt_items(manifest.get("planted_bugs", [])),
        noise=_fmt_items(manifest.get("noise", [])),
        review=review_output[:200_000],
    )
    proc = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--model", model],
        input=prompt,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise JudgeError(f"claude judge failed (rc={proc.returncode}): {proc.stderr[:500]}")

    # `claude --output-format json` wraps the reply: {"result": "<text>", ...}
    try:
        wrapper = json.loads(proc.stdout)
        inner_text = wrapper.get("result", proc.stdout)
    except json.JSONDecodeError:
        inner_text = proc.stdout

    data = _extract_json(inner_text)
    return Verdict(
        planted=data.get("planted", []),
        false_positives=data.get("false_positives", []),
        bonus_bugs=data.get("bonus_bugs", []),
        raw_judge_output=inner_text,
    )
