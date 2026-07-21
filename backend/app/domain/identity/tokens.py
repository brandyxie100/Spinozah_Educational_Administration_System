"""JWT claim models for access and refresh tokens."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class TokenType(StrEnum):
    """Distinguishes access tokens from refresh tokens."""

    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    """Subject claims embedded in access and refresh JWTs."""

    user_id: UUID
    tenant_id: UUID
    email: str
    role: str
    token_type: TokenType = TokenType.ACCESS
