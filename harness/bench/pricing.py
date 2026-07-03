"""API-equivalent cost estimation from token usage.

IMPORTANT: costs are *estimates of what the tokens would cost on the API*, not
actual subscription/plan spend. Providers without token accounting return None.
"""

from __future__ import annotations

import json
from pathlib import Path


def load_pricing(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cost_usd(model: str, usage: dict | None, pricing: dict) -> float | None:
    """Estimate API-equivalent USD cost for one review's token usage."""
    if not usage:
        return None
    rates = pricing.get("models", {}).get(model)
    if not rates:
        return None
    inp = usage.get("input_tokens", 0)
    cached = usage.get("cached_input_tokens", 0)
    out = usage.get("output_tokens", 0)  # already includes reasoning tokens
    uncached = max(inp - cached, 0)
    total = (
        uncached * rates["input"]
        + cached * rates.get("cached_input", rates["input"])
        + out * rates["output"]
    )
    return total / 1_000_000
