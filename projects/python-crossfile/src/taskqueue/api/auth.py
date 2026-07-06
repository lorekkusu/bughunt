"""Static bearer-token authentication.

The app is configured with a fixed ``token -> owner`` mapping. Requests
present ``Authorization: Bearer <token>``; both the header name and the
scheme are matched case-insensitively. Token comparison uses
``hmac.compare_digest`` so lookup time does not depend on how much of a
guessed token matches.
"""

from __future__ import annotations

import hmac
from typing import Mapping, Optional


class Unauthorized(Exception):
    """Raised by :meth:`TokenAuth.require` for missing or unknown tokens."""


def _bearer_token(headers: Mapping[str, str]) -> Optional[str]:
    """Extract the bearer token from *headers*, or None if absent/malformed."""
    if not headers:
        return None
    value: Optional[str] = None
    for key, candidate in headers.items():
        if isinstance(key, str) and key.lower() == "authorization":
            value = candidate
            break
    if not isinstance(value, str):
        return None
    scheme, _, token = value.strip().partition(" ")
    if scheme.lower() != "bearer":
        return None
    token = token.strip()
    return token if token else None


class TokenAuth:
    """Resolve request headers to an owner via a static token table."""

    def __init__(self, tokens: Optional[Mapping[str, str]] = None):
        self._tokens: dict[str, str] = dict(tokens or {})

    def identify(self, headers: Mapping[str, str]) -> Optional[str]:
        """Return the owner for the presented token, or None if unidentified."""
        token = _bearer_token(headers)
        if token is None:
            return None
        presented = token.encode("utf-8")
        for known_token, owner in self._tokens.items():
            if hmac.compare_digest(known_token.encode("utf-8"), presented):
                return owner
        return None

    def require(self, headers: Mapping[str, str]) -> str:
        """Return the owner, or raise :class:`Unauthorized`."""
        owner = self.identify(headers)
        if owner is None:
            raise Unauthorized("missing or unknown bearer token")
        return owner

    def __len__(self) -> int:
        return len(self._tokens)
