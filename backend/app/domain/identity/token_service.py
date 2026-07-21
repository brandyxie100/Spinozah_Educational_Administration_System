"""Token minting and validation port for the identity context."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.domain.identity.tokens import AccessTokenClaims


class TokenService(Protocol):
    """Create and decode JWTs for authentication."""

    def create_access_token(
        self,
        claims: AccessTokenClaims,
        *,
        now: datetime | None = None,
    ) -> str:
        """Mint a short-lived access JWT."""

    def create_refresh_token(
        self,
        claims: AccessTokenClaims,
        *,
        now: datetime | None = None,
    ) -> str:
        """Mint a long-lived refresh JWT (stored in httpOnly cookie)."""

    def decode_access_token(self, token: str) -> AccessTokenClaims:
        """Validate and decode an access JWT."""

    def decode_refresh_token(self, token: str) -> AccessTokenClaims:
        """Validate and decode a refresh JWT."""
