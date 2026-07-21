"""Authentication HTTP endpoints (login, refresh, logout)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_token_service
from app.api.v1.auth_schemas import (
    REFRESH_COOKIE_NAME,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.application.identity.auth_service import AuthApplicationService, AuthTokens
from app.core.settings import Settings, get_settings
from app.domain.identity.exceptions import InvalidCredentialsError
from app.infrastructure.persistence.session import get_session
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import JwtTokenService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[JwtTokenService, Depends(get_token_service)],
) -> AuthApplicationService:
    """Compose the auth application service for the current request."""
    return AuthApplicationService(
        session=session,
        password_hasher=BcryptPasswordHasher(),
        token_service=token_service,
    )


def _set_refresh_cookie(
    response: Response,
    refresh_token: str,
    settings: Settings,
) -> None:
    """Attach the refresh JWT as an httpOnly cookie."""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.jwt_refresh_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response, settings: Settings) -> None:
    """Expire the refresh cookie."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/api/v1/auth",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )


def _to_token_response(tokens: AuthTokens) -> TokenResponse:
    """Map application tokens to the public API schema."""
    return TokenResponse(
        access_token=tokens.access_token,
        user=UserResponse(
            id=tokens.user.id,
            tenant_id=tokens.user.tenant_id,
            email=tokens.user.email,
            full_name=tokens.user.full_name,
            role=tokens.user.role,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    auth_service: Annotated[AuthApplicationService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Authenticate and return an access JWT; set refresh in httpOnly cookie."""
    try:
        tokens = await auth_service.login(
            tenant_slug=body.tenant_slug,
            email=body.email,
            password=body.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    _set_refresh_cookie(response, tokens.refresh_token, settings)
    return _to_token_response(tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthApplicationService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Issue a new access JWT from the httpOnly refresh cookie."""
    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not cookie_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    try:
        tokens = await auth_service.refresh(cookie_token)
    except InvalidCredentialsError as exc:
        _clear_refresh_cookie(response, settings)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    _set_refresh_cookie(response, tokens.refresh_token, settings)
    return _to_token_response(tokens)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Clear the refresh cookie (access token is client-discarded)."""
    _clear_refresh_cookie(response, settings)
