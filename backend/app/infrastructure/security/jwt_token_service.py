"""PyJWT-backed access and refresh token service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

import jwt

from app.domain.identity.exceptions import InvalidCredentialsError
from app.domain.identity.tokens import AccessTokenClaims, TokenType

ALGORITHM = "HS256"


class JwtTokenService:
    """Mint and validate HS256 JWTs for access and refresh flows."""

    def __init__(
        self,
        secret: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
    ) -> None:
        """Configure signing secret and TTLs.

        Args:
            secret: HMAC secret used to sign tokens.
            access_expire_minutes: Access token lifetime in minutes.
            refresh_expire_days: Refresh token lifetime in days.
        """
        self._secret = secret
        self._access_expire_minutes = access_expire_minutes
        self._refresh_expire_days = refresh_expire_days

    def create_access_token(
        self,
        claims: AccessTokenClaims,
        *,
        now: datetime | None = None,
    ) -> str:
        """Mint a short-lived access JWT."""
        issued_at = now or datetime.now(UTC)
        # Force expiry in the past when callers pass a historical `now` for tests.
        expires = issued_at + timedelta(minutes=self._access_expire_minutes)
        return self._encode(claims, TokenType.ACCESS, issued_at, expires)

    def create_refresh_token(
        self,
        claims: AccessTokenClaims,
        *,
        now: datetime | None = None,
    ) -> str:
        """Mint a long-lived refresh JWT for the httpOnly cookie."""
        issued_at = now or datetime.now(UTC)
        expires = issued_at + timedelta(days=self._refresh_expire_days)
        return self._encode(claims, TokenType.REFRESH, issued_at, expires)

    def decode_access_token(self, token: str) -> AccessTokenClaims:
        """Validate and decode an access JWT."""
        return self._decode(token, expected=TokenType.ACCESS)

    def decode_refresh_token(self, token: str) -> AccessTokenClaims:
        """Validate and decode a refresh JWT."""
        return self._decode(token, expected=TokenType.REFRESH)

    def _encode(
        self,
        claims: AccessTokenClaims,
        token_type: TokenType,
        issued_at: datetime,
        expires: datetime,
    ) -> str:
        payload: dict[str, Any] = {
            "sub": str(claims.user_id),
            "tenant_id": str(claims.tenant_id),
            "email": claims.email,
            "role": claims.role,
            "type": token_type.value,
            # Unique id so tokens minted in the same second still differ.
            "jti": str(uuid.uuid4()),
            "iat": issued_at,
            "exp": expires,
        }
        return jwt.encode(payload, self._secret, algorithm=ALGORITHM)

    def _decode(self, token: str, *, expected: TokenType) -> AccessTokenClaims:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[ALGORITHM])
        except jwt.PyJWTError as exc:
            raise InvalidCredentialsError("Invalid or expired token") from exc

        token_type = payload.get("type")
        if token_type != expected.value:
            raise InvalidCredentialsError("Unexpected token type")

        try:
            return AccessTokenClaims(
                user_id=UUID(cast(str, payload["sub"])),
                tenant_id=UUID(cast(str, payload["tenant_id"])),
                email=str(payload["email"]),
                role=str(payload["role"]),
                token_type=expected,
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise InvalidCredentialsError("Malformed token claims") from exc
