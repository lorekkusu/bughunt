"""Aggregate all results/*.json into a cross-config comparison.

Produces:
  reports/summary.md     — markdown table (browsable on GitHub)
  reports/index.html     — self-contained page (openable / GitHub-Pages-able)

`serve()` starts a local http.server to preview index.html.
"""

from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path

from .config import Config
from .runner import ConfigResult

_EFFORT_ORDER = {"low": 0, "medium": 1, "high": 2, "xhigh": 3}
_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _load_all(cfg: Config) -> list[ConfigResult]:
    out = []
    if cfg.results_dir.exists():
        for p in sorted(cfg.results_dir.rglob("*.json")):
            try:
                out.append(ConfigResult.from_dict(json.loads(p.read_text(encoding="utf-8"))))
            except Exception:
                continue
    return out


def _cfg_sort_key(r: ConfigResult):
    return (r.provider, r.model, _EFFORT_ORDER.get(r.effort, 9))


def _cell(count: int, runs: int) -> tuple[str, str]:
    """(text, css_class)."""
    if count >= runs:
        return f"{count}/{runs}", "ok"
    if count == 0:
        return f"{count}/{runs}", "no"
    return f"{count}/{runs}", "part"


def _tag(r: ConfigResult) -> str:
    """Short marker for manual / native-prompt configs (markdown)."""
    if r.manual:
        return f" ⟨manual·{r.prompt_id}⟩"
    if r.prompt_id not in ("standard-v1", "?"):
        return f" ⟨{r.prompt_id}⟩"
    return ""


def _leaderboard(results: list[ConfigResult]) -> list[dict]:
    """Configs ranked by recall (desc), then cost (asc), then FP (asc)."""
    rows = []
    for r in results:
        m = r.metrics()
        rows.append({
            "label": f"{r.provider}/{r.model}/{r.effort}",
            "manual": r.manual,
            "recall": m["recall"]["mean"],
            "fp": m["false_positives"]["mean"],
            "cost": m["cost_usd"]["mean"],
            "speed": m["elapsed_s"]["mean"],
            "runs": r.runs,
        })
    rows.sort(key=lambda x: (
        -(x["recall"] or 0),
        x["cost"] if x["cost"] is not None else 9e9,
        x["fp"] if x["fp"] is not None else 9e9,
    ))
    return rows


_MEDAL = {0: "🥇", 1: "🥈", 2: "🥉"}


# --------------------------------------------------------------------------- #
# markdown
# --------------------------------------------------------------------------- #
def _md_for_project(project: str, results: list[ConfigResult]) -> list[str]:
    lines = [f"## {project}", ""]

    # leaderboard — ranked by recall, then cost
    lines += [
        "### 🏆 Leaderboard (by recall, then cost)",
        "",
        "| # | Config | Recall | FP | $/run | Speed |",
        "|--:|--------|:------:|:--:|:-----:|:-----:|",
    ]
    for i, x in enumerate(_leaderboard(results)):
        rank = _MEDAL.get(i, str(i + 1))
        pct = f"{x['recall']*100:.0f}%" if x["recall"] is not None else "—"
        cost = f"${x['cost']:.4f}" if x["cost"] is not None else "—"
        speed = f"{x['speed']:.0f}s" if x["speed"] is not None else "—"
        label = x["label"] + (" ⟨manual⟩" if x["manual"] else "")
        lines.append(f"| {rank} | {label} | {pct} | {x['fp']:.1f} | {cost} | {speed} |")
    lines.append("")

    results = sorted(results, key=_cfg_sort_key)
    # metrics table
    lines += [
        "### Metrics (all configs)",
        "",
        "| Config | Runs | Recall (mean·min–max) | FP | Bonus | Speed | Out-tok | Est. $ |",
        "|--------|:----:|-----------------------|:--:|:-----:|:-----:|:-------:|:------:|",
    ]
    for r in results:
        m = r.metrics()
        rec = m["recall"]
        def p(x): return f"{x*100:.0f}%" if x is not None else "—"
        def n(x, s=""): return f"{x:{s}}" if x is not None else "—"
        cost = m["cost_usd"]["mean"]
        lines.append(
            f"| {r.provider}/{r.model}/`{r.effort}`{_tag(r)} | {r.runs} | "
            f"{p(rec['mean'])} · {p(rec['min'])}–{p(rec['max'])} | "
            f"{n(m['false_positives']['mean'], '.1f')} | {n(m['bonus']['mean'], '.1f')} | "
            f"{n(m['elapsed_s']['mean'], '.1f')}s | "
            f"{n(m['output_tokens']['mean'] and round(m['output_tokens']['mean']), ',')} | "
            f"{('$'+format(cost, '.4f')) if cost is not None else '—'} |"
        )
    lines.append("")

    # stability matrix
    planted = results[0].planted if results else []
    planted = sorted(planted, key=lambda b: (_SEV_ORDER.get(b.get("severity"), 9), b["id"]))
    header = "| Bug | " + " | ".join(f"{r.model}/`{r.effort}`{_tag(r)}" for r in results) + " |"
    sep = "|-----|" + "|".join([":---:"] * len(results)) + "|"
    lines += [header, sep]
    for bug in planted:
        row = [f"{bug['id']} {bug.get('severity','')[:4]} {bug['title']}"]
        for r in results:
            c = r.per_bug_counts().get(bug["id"], 0)
            txt, cls = _cell(c, r.runs)
            mark = {"ok": "✅", "part": "⚠️", "no": "❌"}[cls]
            row.append(f"{mark} {txt}")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return lines


def write_markdown(cfg: Config) -> Path:
    results = _load_all(cfg)
    by_project: dict[str, list[ConfigResult]] = defaultdict(list)
    for r in results:
        by_project[r.project].append(r)

    lines = [
        "# bughunt — benchmark summary",
        "",
        "Recall = planted bugs found. **✅** found every run · **⚠️** some runs · "
        "**❌** never. Costs are **API-equivalent estimates**, not actual spend.",
        "",
        "⟨manual⟩ = human-triggered tool scored via `bench judge` (no cost/speed/token). "
        "`prompt` = which review prompt ran (`standard-v1` for automated tools; `native` "
        "means the tool used its own prompt — not directly comparable).",
        "",
    ]
    if not results:
        lines.append("_No results yet. Run `bench run` first._")
    for project in sorted(by_project):
        lines += _md_for_project(project, by_project[project])

    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.reports_dir / "summary.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


# --------------------------------------------------------------------------- #
# html
# --------------------------------------------------------------------------- #
_CSS = """
:root { color-scheme: light dark; }
body { font-family: -apple-system, system-ui, sans-serif; margin: 2rem auto; max-width: 1100px; padding: 0 1rem; line-height: 1.5; }
h1 { margin-bottom: .2rem; } .sub { opacity:.7; margin-top:0; }
h2 { margin-top: 2rem; border-bottom: 1px solid #8884; padding-bottom: .2rem; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 14px; overflow-x:auto; display:block; }
th, td { border: 1px solid #8883; padding: 4px 8px; text-align: center; }
th { background: #8881; } td.bug { text-align: left; white-space: nowrap; }
.ok { background: rgba(40,180,80,.22); } .part { background: rgba(230,180,30,.28); } .no { background: rgba(220,60,60,.22); }
.metrics td, .metrics th { text-align: center; } .metrics td.cfg { text-align: left; font-family: ui-monospace, monospace; }
.badge { font-family: -apple-system, system-ui, sans-serif; font-size: 11px; padding: 1px 6px; border-radius: 10px; background: #a05ac033; color: #a05ac0; }
"""


def _html_for_project(project: str, results: list[ConfigResult]) -> str:
    esc = html.escape
    parts = [f"<h2>{esc(project)}</h2>"]

    # leaderboard — ranked by recall, then cost
    parts.append("<h3>🏆 Leaderboard</h3>")
    parts.append('<table class="metrics"><thead><tr>'
                 "<th>#</th><th>Config</th><th>Recall</th><th>FP</th>"
                 "<th>$/run</th><th>Speed</th></tr></thead><tbody>")
    for i, x in enumerate(_leaderboard(results)):
        rank = _MEDAL.get(i, str(i + 1))
        pct = f"{x['recall']*100:.0f}%" if x["recall"] is not None else "—"
        cost = f"${x['cost']:.4f}" if x["cost"] is not None else "—"
        speed = f"{x['speed']:.0f}s" if x["speed"] is not None else "—"
        label = esc(x["label"]) + (' <span class="badge">manual</span>' if x["manual"] else "")
        parts.append(
            f'<tr><td>{rank}</td><td class="cfg">{label}</td><td>{pct}</td>'
            f'<td>{x["fp"]:.1f}</td><td>{cost}</td><td>{speed}</td></tr>'
        )
    parts.append("</tbody></table>")

    results = sorted(results, key=_cfg_sort_key)
    # metrics
    parts.append("<h3>Metrics</h3>")
    parts.append('<table class="metrics"><thead><tr>'
                 "<th>Config</th><th>Runs</th><th>Recall mean</th><th>min–max</th>"
                 "<th>FP</th><th>Bonus</th><th>Speed</th><th>Out-tok</th><th>Est. $</th>"
                 "</tr></thead><tbody>")
    for r in results:
        m = r.metrics(); rec = m["recall"]
        def p(x): return f"{x*100:.0f}%" if x is not None else "—"
        def n(x, s=""): return f"{x:{s}}" if x is not None else "—"
        cost = m["cost_usd"]["mean"]
        badge = f' <span class="badge">manual·{esc(r.prompt_id)}</span>' if r.manual else ""
        parts.append(
            f'<tr><td class="cfg">{esc(r.provider)}/{esc(r.model)}/{esc(r.effort)}{badge}</td>'
            f"<td>{r.runs}</td><td>{p(rec['mean'])}</td>"
            f"<td>{p(rec['min'])}–{p(rec['max'])}</td>"
            f"<td>{n(m['false_positives']['mean'], '.1f')}</td>"
            f"<td>{n(m['bonus']['mean'], '.1f')}</td>"
            f"<td>{n(m['elapsed_s']['mean'], '.1f')}s</td>"
            f"<td>{n(m['output_tokens']['mean'] and round(m['output_tokens']['mean']), ',')}</td>"
            f"<td>{('$'+format(cost, '.4f')) if cost is not None else '—'}</td></tr>"
        )
    parts.append("</tbody></table>")

    # stability matrix
    planted = sorted(results[0].planted, key=lambda b: (_SEV_ORDER.get(b.get("severity"), 9), b["id"]))
    parts.append("<table><thead><tr><th>Bug</th>"
                 + "".join(f"<th>{esc(r.model)}<br>{esc(r.effort)}</th>" for r in results)
                 + "</tr></thead><tbody>")
    for bug in planted:
        cells = [f'<td class="bug">{esc(bug["id"])} · {esc(bug.get("severity",""))} · {esc(bug["title"])}</td>']
        for r in results:
            c = r.per_bug_counts().get(bug["id"], 0)
            txt, cls = _cell(c, r.runs)
            cells.append(f'<td class="{cls}">{txt}</td>')
        parts.append("<tr>" + "".join(cells) + "</tr>")
    parts.append("</tbody></table>")
    return "\n".join(parts)


def write_html(cfg: Config) -> Path:
    results = _load_all(cfg)
    by_project: dict[str, list[ConfigResult]] = defaultdict(list)
    for r in results:
        by_project[r.project].append(r)

    body = [
        "<h1>bughunt — benchmark summary</h1>",
        '<p class="sub">✅ found every run · ⚠️ some runs · ❌ never. '
        "Costs are API-equivalent estimates, not actual spend. "
        '<span class="badge">manual</span> = human-triggered tool scored via '
        "<code>bench judge</code>; a <code>native</code> prompt means the tool used its "
        "own prompt (not directly comparable to standard-v1).</p>",
    ]
    if not results:
        body.append("<p><em>No results yet. Run <code>bench run</code> first.</em></p>")
    for project in sorted(by_project):
        body.append(_html_for_project(project, by_project[project]))

    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>bughunt summary</title><style>" + _CSS + "</style></head><body>"
        + "\n".join(body) + "</body></html>"
    )
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.reports_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    return out


def serve(cfg: Config, port: int = 8000) -> None:
    import functools
    import http.server
    import socketserver

    directory = str(cfg.reports_dir)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/index.html"
        print(f"serving {directory} at {url}  (Ctrl-C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
