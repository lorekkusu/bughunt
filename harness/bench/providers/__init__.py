"""Provider adapters — one per tool under test."""

from .base import Provider, ReviewResult
from .claude import ClaudeProvider
from .codex import CodexProvider
from .cursor_agent import CursorAgentProvider

# Registry: provider name -> adapter class. Add new tools here.
REGISTRY: dict[str, type[Provider]] = {
    CodexProvider.name: CodexProvider,
    ClaudeProvider.name: ClaudeProvider,
    CursorAgentProvider.name: CursorAgentProvider,
}


def get_provider(name: str) -> Provider:
    try:
        return REGISTRY[name]()
    except KeyError:
        raise SystemExit(
            f"Unknown provider {name!r}. Known: {', '.join(sorted(REGISTRY))}"
        )


__all__ = ["Provider", "ReviewResult", "REGISTRY", "get_provider"]
