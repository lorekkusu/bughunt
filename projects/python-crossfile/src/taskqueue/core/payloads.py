"""Payload hygiene: size limits and log redaction.

Job payloads are caller-supplied JSON objects. Before a payload is logged or
accepted, two questions come up again and again: "is it too big?" and "does
it contain credentials?". This module answers both without ever mutating the
caller's data — :func:`redact` returns a freshly built structure, leaving
the original payload byte-for-byte intact.
"""

from __future__ import annotations

import json
from typing import Any, Optional

#: Maximum accepted payload size in bytes (of the compact JSON encoding).
MAX_PAYLOAD_BYTES = 64_000

#: The replacement written in place of sensitive values.
REDACTED = "***"

#: A key is sensitive when its lowercase form contains any of these tokens.
_SENSITIVE_TOKENS = ("secret", "token", "password", "key")


def payload_size(payload: dict) -> int:
    """Size of *payload* in bytes when encoded as compact JSON.

    Serialized with ``ensure_ascii=False`` and then UTF-8 encoded, so the
    figure reflects the real byte cost of non-ASCII content rather than the
    inflated ``\\uXXXX`` escape form. Non-JSON-serializable values raise
    ``TypeError``, exactly as they would at persistence time.
    """
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return len(encoded.encode("utf-8"))


def check_size(payload: dict) -> Optional[str]:
    """Return an error message when *payload* exceeds the size limit.

    ``None`` means the payload is within bounds. The message includes both
    the measured size and the limit so callers can surface it verbatim in a
    400 response.
    """
    size = payload_size(payload)
    if size > MAX_PAYLOAD_BYTES:
        return f"payload is {size} bytes; the limit is {MAX_PAYLOAD_BYTES} bytes"
    return None


def _is_sensitive(key: Any) -> bool:
    """True when *key* is a string containing a sensitive token.

    Matching is case-insensitive and substring-based, so ``"apiKey"``,
    ``"DB_PASSWORD"``, and ``"refresh_token"`` are all caught. Non-string
    keys (possible in dicts that never round-tripped through JSON) are
    never treated as sensitive.
    """
    if not isinstance(key, str):
        return False
    lowered = key.lower()
    return any(token in lowered for token in _SENSITIVE_TOKENS)


def _redact_value(value: Any) -> Any:
    """Rebuild *value* with sensitive dict entries replaced by ``***``.

    Dicts and lists are always rebuilt (never returned by reference), so the
    result shares no mutable containers with the input. Scalar leaves are
    returned as-is — JSON scalars are immutable, so sharing them is safe.
    """
    if isinstance(value, dict):
        return {
            key: REDACTED if _is_sensitive(key) else _redact_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in value)
    return value


def redact(payload: dict) -> dict:
    """A deep copy of *payload* with sensitive values masked.

    Any entry whose key contains ``secret``, ``token``, ``password``, or
    ``key`` (case-insensitive) has its value replaced by ``"***"`` — the
    whole value, even when it is a nested object, since a dict stored under
    ``"credentials_token"`` is sensitive in its entirety. Redaction recurses
    into nested dicts and into lists (including lists of dicts). The input
    is never mutated: every container in the result is newly built.
    """
    return {
        key: REDACTED if _is_sensitive(key) else _redact_value(value)
        for key, value in payload.items()
    }
