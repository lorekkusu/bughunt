"""Interactive + scriptable CLI entry point.

    uv run bench                         # interactive menus
    uv run bench -p python-basic --provider codex -m gpt-5.5 -e high
    uv run bench --provider codex -m gpt-5.5 -e xhigh --runs 3
"""

from __future__ import annotations

import typer
import questionary
from rich.console import Console

from . import report
from .config import load_config
from .runner import run_once

console = Console()


def _pick(label: str, choices: list[str], default: str | None = None) -> str:
    ans = questionary.select(label, choices=choices, default=default or choices[0]).ask()
    if ans is None:
        raise typer.Exit(1)
    return ans


def run_cmd(
    project: str = typer.Option(None, "--project", "-p", help="Project name"),
    provider: str = typer.Option(None, "--provider", help="Tool under test"),
    model: str = typer.Option(None, "--model", "-m", help="Model id"),
    effort: str = typer.Option(None, "--effort", "-e", help="Reasoning effort"),
    judge_model: str = typer.Option(None, "--judge-model", help="Override judge model"),
    runs: int = typer.Option(1, "--runs", help="Repeat N times (LLM reviews vary)"),
    keep_scratch: bool = typer.Option(False, "--keep-scratch", help="Keep the review copy"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Error instead of prompting"),
):
    """Run a benchmark. Any option left out is prompted for interactively."""
    cfg = load_config()

    def need(value, label, choices, default=None):
        if value:
            return value
        if no_interactive:
            raise typer.BadParameter(f"missing {label} (choices: {', '.join(choices)})")
        return _pick(label, choices, default)

    project = need(project, "Project", cfg.project_names)
    provider = need(provider, "Provider (tool under test)", cfg.provider_names)

    pcfg = cfg.provider_cfg(provider)
    model = need(model, "Model", pcfg.get("models", []), pcfg.get("default_model"))
    effort = need(effort, "Reasoning effort", pcfg.get("efforts", []), pcfg.get("default_effort"))

    console.print(
        f"\n[bold]Running[/] {project} · {provider}/{model} · effort={effort} · "
        f"runs={runs} · judge={judge_model or cfg.judge_model}\n"
    )

    for i in range(1, runs + 1):
        if runs > 1:
            console.rule(f"run {i}/{runs}")
        with console.status("reviewing + judging…"):
            result = run_once(
                cfg, project, provider, model, effort,
                judge_model=judge_model, keep_scratch=keep_scratch,
            )
        report.print_summary(result)
        path = report.write_markdown(result, cfg.reports_dir)
        console.print(f"[dim]report → {path}[/]\n")


def main():
    typer.run(run_cmd)


if __name__ == "__main__":
    main()
