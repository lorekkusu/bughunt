"""Per-config console output and fixed-format markdown report."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from .runner import ConfigResult

console = Console()

_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def stability(count: int, runs: int) -> tuple[str, str]:
    """Return (symbol, rich_color) for a found-count out of `runs`."""
    if count >= runs:
        return "✅", "green"
    if count == 0:
        return "❌", "red"
    return "⚠️", "yellow"


def _fmt(v, spec="", suffix=""):
    return f"{v:{spec}}{suffix}" if v is not None else "—"


def print_summary(r: ConfigResult) -> None:
    counts = r.per_bug_counts()
    m = r.metrics()

    tag = "  [magenta](manual)[/]" if r.manual else ""
    tag += f"  [dim]prompt={r.prompt_id}[/]"
    tag += "  [dim](cached)[/]" if r.skipped else ""
    table = Table(
        title=f"{r.project} · {r.provider}/{r.model} · effort={r.effort} · {r.runs} runs{tag}"
    )
    table.add_column("ID"); table.add_column("Sev"); table.add_column("Bug")
    table.add_column("Found", justify="center")
    for bug in sorted(r.planted, key=lambda b: (_SEV_ORDER.get(b.get("severity"), 9), b["id"])):
        sym, color = stability(counts[bug["id"]], r.runs)
        table.add_row(
            bug["id"], bug.get("severity", "?"), bug["title"],
            f"[{color}]{sym} {counts[bug['id']]}/{r.runs}[/]",
        )
    console.print(table)

    rec = m["recall"]
    console.print(
        f"[bold]Recall[/] mean {_fmt(rec['mean'] and rec['mean']*100, '.0f', '%')} "
        f"(min {_fmt(rec['min'] and rec['min']*100,'.0f','%')} / "
        f"max {_fmt(rec['max'] and rec['max']*100,'.0f','%')})   "
        f"[bold]FP[/] {_fmt(m['false_positives']['mean'], '.1f')}   "
        f"[bold]Bonus[/] {_fmt(m['bonus']['mean'], '.1f')}"
    )
    console.print(
        f"[bold]Speed[/] {_fmt(m['elapsed_s']['mean'], '.1f', 's')}   "
        f"[bold]Out-tok[/] {_fmt(m['output_tokens']['mean'] and round(m['output_tokens']['mean']), ',')}   "
        f"[bold]Est. cost[/] {_fmt(m['cost_usd']['mean'], '.4f') if m['cost_usd']['mean'] is not None else '—'}"
        + ("  [dim]$ API-equiv[/]" if m["cost_usd"]["mean"] is not None else "")
    )
    rc_bad = [i + 1 for i, rr in enumerate(r.rounds) if rr.returncode != 0]
    if rc_bad:
        console.print(f"[yellow]⚠️ non-zero exit on round(s) {rc_bad} "
                      f"(model may not support effort {r.effort!r})[/]")


def write_markdown(r: ConfigResult, reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    out = reports_dir / f"{r.project}__{r.provider}__{r.model}__{r.effort}.md"

    counts = r.per_bug_counts()
    m = r.metrics()

    def pct(x):
        return f"{x*100:.0f}%" if x is not None else "—"

    lines = [
        f"# {r.project} · {r.provider}/{r.model} · effort=`{r.effort}`",
        "",
        "| | |", "|---|---|",
        f"| Runs | {r.runs} |",
        f"| Mode | {'manual' if r.manual else 'automated'} · prompt `{r.prompt_id}` |",
        f"| Judge | `{r.judge_model}` (claude) |",
        f"| Code hash | `{r.code_hash}` |",
        f"| Created | {r.created} |",
        "",
        "## Metrics (across runs)",
        "",
        "| Metric | Mean | Min | Max |",
        "|--------|------|-----|-----|",
        f"| Recall | {pct(m['recall']['mean'])} | {pct(m['recall']['min'])} | {pct(m['recall']['max'])} |",
        f"| False positives | {_fmt(m['false_positives']['mean'], '.1f')} | {_fmt(m['false_positives']['min'])} | {_fmt(m['false_positives']['max'])} |",
        f"| Bonus real bugs | {_fmt(m['bonus']['mean'], '.1f')} | {_fmt(m['bonus']['min'])} | {_fmt(m['bonus']['max'])} |",
        f"| Speed (s) | {_fmt(m['elapsed_s']['mean'], '.1f')} | {_fmt(m['elapsed_s']['min'], '.1f')} | {_fmt(m['elapsed_s']['max'], '.1f')} |",
        f"| Output tokens | {_fmt(m['output_tokens']['mean'] and round(m['output_tokens']['mean']), ',')} | {_fmt(m['output_tokens']['min'])} | {_fmt(m['output_tokens']['max'])} |",
        f"| Est. cost (USD, API-equiv) | {_fmt(m['cost_usd']['mean'], '.4f')} | {_fmt(m['cost_usd']['min'], '.4f')} | {_fmt(m['cost_usd']['max'], '.4f')} |",
        "",
        "> Costs are **API-equivalent estimates** (what these tokens would cost on the",
        "> OpenAI API), not actual subscription spend. See `pricing.json`.",
        "",
        "## Detection stability",
        "",
        "Found in N of the runs. ✅ = every run · ⚠️ = some runs · ❌ = never.",
        "",
        "| ID | Severity | Bug | Found |",
        "|----|----------|-----|:-----:|",
    ]
    for bug in sorted(r.planted, key=lambda b: (_SEV_ORDER.get(b.get("severity"), 9), b["id"])):
        c = counts[bug["id"]]
        sym, _ = stability(c, r.runs)
        lines.append(f"| {bug['id']} | {bug.get('severity','?')} | {bug['title']} | {sym} {c}/{r.runs} |")

    # bonus / FP aggregated across rounds
    bonus_titles: dict[str, int] = {}
    for rr in r.rounds:
        for b in rr.bonus_items:
            t = b.get("title", "?")
            bonus_titles[t] = bonus_titles.get(t, 0) + 1
    if bonus_titles:
        lines += ["", "## Bonus findings (real, not planted)", ""]
        for t, c in sorted(bonus_titles.items(), key=lambda kv: -kv[1]):
            lines.append(f"- {t} — seen in {c}/{r.runs} runs")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
