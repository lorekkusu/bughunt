"""Render run results to the console (rich) and to a markdown report file."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .runner import RunResult

console = Console()

_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def print_summary(r: RunResult) -> None:
    found = set(r.verdict.found_ids)
    title_by_id = {b["id"]: b for b in r.manifest.get("planted_bugs", [])}

    table = Table(title=f"{r.project} · {r.provider}/{r.model} · effort={r.effort}")
    table.add_column("ID"); table.add_column("Sev"); table.add_column("Bug")
    table.add_column("Found", justify="center")
    for bug in sorted(
        r.manifest.get("planted_bugs", []),
        key=lambda b: (_SEV_ORDER.get(b.get("severity"), 9), b["id"]),
    ):
        hit = bug["id"] in found
        table.add_row(
            bug["id"], bug.get("severity", "?"), bug["title"],
            "[green]✅[/]" if hit else "[red]❌[/]",
        )
    console.print(table)

    sev = r.severity_breakdown()
    sev_str = " · ".join(
        f"{k} {v[0]}/{v[1]}" for k, v in sorted(sev.items(), key=lambda kv: _SEV_ORDER.get(kv[0], 9))
    )
    console.print(
        f"[bold]Recall[/] {r.found}/{r.total_planted} "
        f"({r.recall*100:.0f}%)   [dim]{sev_str}[/]"
    )
    console.print(
        f"[bold]False positives[/] {r.false_positives}   "
        f"[bold]Bonus real bugs[/] {len(r.verdict.bonus_bugs)}"
    )
    if r.verdict.bonus_bugs:
        for b in r.verdict.bonus_bugs:
            console.print(f"  [yellow]+[/] {b.get('title','?')}")
    for note in r.notes:
        console.print(f"[yellow]{note}[/]")


def write_markdown(r: RunResult, reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = reports_dir / f"{r.project}__{r.provider}__{r.model}__{r.effort}__{stamp}.md"

    found = set(r.verdict.found_ids)
    lines = [
        f"# Benchmark Report — {r.project}",
        "",
        "| | |", "|---|---|",
        f"| Project | `{r.project}` |",
        f"| Tool | {r.provider} |",
        f"| Model | `{r.model}` |",
        f"| Effort | `{r.effort}` |",
        f"| Judge | `{r.judge_model}` (claude) |",
        f"| Started | {r.started} |",
        f"| Command | `{r.review.command}` |",
        "",
        "## Headline",
        "",
        f"- **Recall:** {r.found} / {r.total_planted} = {r.recall*100:.0f}%",
        f"- **False positives:** {r.false_positives}",
        f"- **Bonus real bugs:** {len(r.verdict.bonus_bugs)}",
        "",
        "## Detection scorecard",
        "",
        "| ID | Severity | Bug | Found? |",
        "|----|----------|-----|:------:|",
    ]
    for bug in sorted(
        r.manifest.get("planted_bugs", []),
        key=lambda b: (_SEV_ORDER.get(b.get("severity"), 9), b["id"]),
    ):
        mark = "✅" if bug["id"] in found else "❌ **miss**"
        lines.append(f"| {bug['id']} | {bug.get('severity','?')} | {bug['title']} | {mark} |")

    sev = r.severity_breakdown()
    sev_str = " · ".join(
        f"{k.capitalize()} {v[0]}/{v[1]}"
        for k, v in sorted(sev.items(), key=lambda kv: _SEV_ORDER.get(kv[0], 9))
    )
    lines += ["", f"**By severity:** {sev_str}", ""]

    if r.verdict.false_positives:
        lines += ["## False positives", ""]
        for fp in r.verdict.false_positives:
            lines.append(f"- `{fp.get('noise_id')}` — {fp.get('evidence','')}")
        lines.append("")

    if r.verdict.bonus_bugs:
        lines += ["## Bonus findings (real, not planted)", ""]
        for b in r.verdict.bonus_bugs:
            lines.append(f"- **{b.get('title','?')}** — {b.get('evidence','')}")
        lines.append("")

    if r.notes:
        lines += ["## Notes", ""] + [f"- {n}" for n in r.notes] + [""]

    out.write_text("\n".join(lines))

    # Persist raw artifacts next to the report for auditing / debugging.
    out.with_suffix(".review.txt").write_text(
        f"$ {r.review.command}\n(returncode {r.review.returncode})\n\n{r.review.raw_output}"
    )
    out.with_suffix(".judge.txt").write_text(r.verdict.raw_judge_output)
    return out
