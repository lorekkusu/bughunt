"""Interactive + scriptable CLI.

    uv run bench run                                  # interactive menus (3 runs)
    uv run bench run -p python-basic --provider codex -m gpt-5.5 -e high
    uv run bench run --provider codex -m gpt-5.5 --all-efforts     # low..xhigh
    uv run bench run --provider codex --all-models --all-efforts --runs 5
    uv run bench judge --provider cursor-bugbot --result out.txt   # score a manual tool
    uv run bench providers                            # list tools + how to run each
    uv run bench summary --serve                      # build + preview the report
"""

from __future__ import annotations

from pathlib import Path

import typer
import questionary
from rich.console import Console
from rich.table import Table

from . import report, summary as summary_mod
from .config import load_config
from .pricing import load_pricing
from .runner import judge_manual, run_config

console = Console()
app = typer.Typer(add_completion=False, help="Benchmark AI code-review tools.", no_args_is_help=True)


def _pick(label: str, choices: list[str], default: str | None = None) -> str:
    ans = questionary.select(label, choices=choices, default=default or choices[0]).ask()
    if ans is None:
        raise typer.Exit(1)
    return ans


def _need(value, label, choices, no_interactive, default=None):
    """Return value, else prompt (interactive) or error (--no-interactive)."""
    if value:
        return value
    if no_interactive:
        raise typer.BadParameter(f"missing {label} (choices: {', '.join(choices)})")
    return _pick(label, choices, default)


@app.command()
def run(
    project: str = typer.Option(None, "--project", "-p", help="Project name"),
    provider: str = typer.Option(None, "--provider", help="Tool under test"),
    model: str = typer.Option(None, "--model", "-m", help="Model id"),
    effort: str = typer.Option(None, "--effort", "-e", help="Reasoning effort"),
    all_models: bool = typer.Option(False, "--all-models", help="Every model for the provider"),
    all_efforts: bool = typer.Option(False, "--all-efforts", help="Every effort (low..xhigh)"),
    runs: int = typer.Option(None, "--runs", help="Rounds per config (default from config)"),
    judge_model: str = typer.Option(None, "--judge-model", help="Override judge model"),
    force: bool = typer.Option(False, "--force", help="Re-run even if a fresh result exists"),
    keep_scratch: bool = typer.Option(False, "--keep-scratch", help="Keep review copies"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Error instead of prompting"),
):
    """Run one or more automated benchmark configs (project × provider × model × effort)."""
    cfg = load_config()
    prompt = cfg.review_prompt()
    pricing = load_pricing(cfg.pricing_file)
    runs = runs or cfg.default_runs

    project = _need(project, "Project", cfg.project_names, no_interactive)
    # manual tools are scored via `bench judge` only — keep them out of the run menu
    runnable = [p for p in cfg.provider_names if not cfg.provider_cfg(p).get("manual")]
    provider = _need(provider, "Provider (tool under test)", runnable, no_interactive)
    pcfg = cfg.provider_cfg(provider)
    if pcfg.get("manual"):  # guards an explicit --provider <manual tool>
        raise typer.BadParameter(
            f"{provider!r} is a manual tool — use `bench judge`, not `bench run`. "
            f"({pcfg.get('instructions', '')})"
        )

    models = pcfg.get("models", []) if all_models else [
        _need(model, "Model", pcfg.get("models", []), no_interactive, pcfg.get("default_model"))
    ]
    efforts = pcfg.get("efforts", []) if all_efforts else [
        _need(effort, "Reasoning effort", pcfg.get("efforts", []), no_interactive, pcfg.get("default_effort"))
    ]

    combos = [(mo, ef) for mo in models for ef in efforts]
    console.print(
        f"\n[bold]Plan[/] {project} · {provider} · "
        f"{len(combos)} config(s) × {runs} runs · judge={judge_model or cfg.judge_model}\n"
    )

    for mo, ef in combos:
        console.rule(f"{provider}/{mo} · effort={ef}")

        def on_round(i, n, rr):
            console.print(f"  [dim]round {i}/{n}: found {len(rr.found)}, "
                          f"{rr.elapsed_s:.0f}s[/]")

        with console.status(f"{mo}/{ef}: reviewing + judging…"):
            result = run_config(
                cfg, project, provider, mo, ef, runs, prompt, pricing,
                judge_model=judge_model, force=force, keep_scratch=keep_scratch,
                on_round=None if no_interactive else on_round,
            )
        if result.skipped:
            console.print("[dim]cached (same code + enough runs) — use --force to re-run[/]")
        report.print_summary(result)
        report.write_markdown(result, cfg.reports_dir)
        console.print()

    summary_mod.write_markdown(cfg)
    summary_mod.write_html(cfg)
    console.print(f"[dim]summary → {cfg.reports_dir}/summary.md · index.html[/]")


@app.command()
def judge(
    result: list[Path] = typer.Option(..., "--result", "-r", help="Findings file (repeat for multiple runs)"),
    project: str = typer.Option(None, "--project", "-p", help="Project name"),
    provider: str = typer.Option(None, "--provider", help="Provider (must be registered in config.toml)"),
    model: str = typer.Option(None, "--model", "-m", help="Model label"),
    effort: str = typer.Option(None, "--effort", "-e", help="Effort label"),
    judge_model: str = typer.Option(None, "--judge-model", help="Override judge model"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Error instead of prompting"),
):
    """Score a manually-produced review (e.g. Cursor Bugbot) against the answer key.

    The provider must be registered in config.toml. Each --result file is one run.
    See docs/manual-tools.md for the capture workflow."""
    cfg = load_config()

    project = _need(project, "Project", cfg.project_names, no_interactive)
    provider = _need(provider, "Provider", cfg.provider_names, no_interactive)
    pcfg = cfg.provider_cfg(provider)
    model = _need(model, "Model", pcfg.get("models", []), no_interactive, pcfg.get("default_model"))
    effort = _need(effort, "Effort", pcfg.get("efforts", []), no_interactive, pcfg.get("default_effort"))

    texts: list[str] = []
    for f in result:
        if not f.exists():
            raise typer.BadParameter(f"no such file: {f}")
        t = f.read_text(encoding="utf-8").strip()
        if not t:
            raise typer.BadParameter(f"empty file: {f}")
        texts.append(t)

    prompt_id = "native" if pcfg.get("native") else cfg.prompt_id
    console.print(
        f"\n[bold]Judging[/] {len(texts)} manual result(s) · {provider}/{model}/{effort} · "
        f"prompt={prompt_id} · judge={judge_model or cfg.judge_model}\n"
    )
    with console.status("judging…"):
        res = judge_manual(cfg, project, provider, model, effort, texts, prompt_id, judge_model=judge_model)

    # keep the raw inputs for provenance (manual results can't be regenerated)
    raw_dir = cfg.reports_dir.parent / "manual-inputs" / provider / model / effort
    raw_dir.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(texts, 1):
        (raw_dir / f"r{i}.txt").write_text(t, encoding="utf-8")

    report.print_summary(res)
    report.write_markdown(res, cfg.reports_dir)
    summary_mod.write_markdown(cfg)
    summary_mod.write_html(cfg)
    console.print(f"[dim]raw inputs → {raw_dir}  ·  summary refreshed[/]")


@app.command()
def providers():
    """List registered providers, whether they are automated or manual, and how to run each."""
    cfg = load_config()
    t = Table(title="providers")
    t.add_column("name"); t.add_column("type"); t.add_column("prompt")
    t.add_column("models"); t.add_column("how to run")
    for name in cfg.provider_names:
        pc = cfg.provider_cfg(name)
        typ = "[magenta]manual[/]" if pc.get("manual") else "[green]auto[/]"
        prm = "native" if pc.get("native") else "standard"
        t.add_row(name, typ, prm, ", ".join(pc.get("models", [])), pc.get("instructions", "—"))
    console.print(t)


@app.command()
def summary(
    serve: bool = typer.Option(False, "--serve", help="Preview index.html on a local server"),
    port: int = typer.Option(8000, "--port", help="Port for --serve"),
):
    """Rebuild the cross-config summary (markdown + HTML)."""
    cfg = load_config()
    md = summary_mod.write_markdown(cfg)
    html = summary_mod.write_html(cfg)
    console.print(f"[green]wrote[/] {md}\n[green]wrote[/] {html}")
    if serve:
        summary_mod.serve(cfg, port=port)


def main():
    app()


if __name__ == "__main__":
    main()
