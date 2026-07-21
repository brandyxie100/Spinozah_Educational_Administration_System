"""Shared FastAPI dependencies: JWT auth and RBAC role guards."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.settings import Settings, get_settings
from app.domain.identity.exceptions import (
    InsufficientPermissionsError,
    InvalidCredentialsError,
)
from app.domain.identity.rbac import assert_role_allowed
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.security.jwt_token_service import JwtTokenService

_bearer_scheme = HTTPBearer(auto_error=False)


def get_token_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JwtTokenService:
    """Build the JWT service from application settings."""
    return JwtTokenService(
        secret=settings.jwt_secret,
        access_expire_minutes=settings.jwt_access_expire_minutes,
        refresh_expire_days=settings.jwt_refresh_expire_days,
    )


async def get_current_access_claims(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
    token_service: Annotated[JwtTokenService, Depends(get_token_service)],
) -> AccessTokenClaims:
    """Decode the Bearer access JWT or raise 401."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        return token_service.decode_access_token(credentials.credentials)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def require_roles(
    *allowed: Role | str,
) -> Callable[..., Coroutine[Any, Any, AccessTokenClaims]]:
    """Return a dependency that enforces one of the allowed roles.

    Usage::

        @router.get("/admin")
        async def admin_only(
            claims: AccessTokenClaims = Depends(require_roles(Role.ADMIN)),
        ) -> dict[str, str]:
            ...
    """

    async def _require(
        claims: Annotated[AccessTokenClaims, Depends(get_current_access_claims)],
    ) -> AccessTokenClaims:
        try:
            assert_role_allowed(claims.role, allowed)
        except InsufficientPermissionsError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            ) from exc
        return claims

    return _require
