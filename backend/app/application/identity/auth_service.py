"""Application service for login, refresh, and logout."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.identity.exceptions import InvalidCredentialsError
from app.domain.identity.passwords import PasswordHasher
from app.domain.identity.token_service import TokenService
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.models import TenantModel, UserModel


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """User profile returned after successful authentication."""

    id: UUID
    tenant_id: UUID
    email: str
    full_name: str
    role: str


@dataclass(frozen=True, slots=True)
class AuthTokens:
    """Pair of access JWT and refresh JWT for the HTTP layer."""

    access_token: str
    refresh_token: str
    user: AuthenticatedUser


class AuthApplicationService:
    """Orchestrate credential checks and token minting."""

    def __init__(
        self,
        session: AsyncSession,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        """Bind persistence and security adapters for one request."""
        self._session = session
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def login(
        self,
        *,
        tenant_slug: str,
        email: str,
        password: str,
    ) -> AuthTokens:
        """Authenticate by tenant slug + email + password."""
        user = await self._load_active_user(tenant_slug=tenant_slug, email=email)
        if user is None or not self._password_hasher.verify(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError("Invalid email or password")
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> AuthTokens:
        """Mint a new token pair from a valid refresh JWT."""
        claims = self._token_service.decode_refresh_token(refresh_token)
        user = await self._session.get(UserModel, claims.user_id)
        if (
            user is None
            or not user.is_active
            or user.tenant_id != claims.tenant_id
            or user.email != claims.email
        ):
            raise InvalidCredentialsError("Invalid refresh token")
        return self._issue_tokens(user)

    def _issue_tokens(self, user: UserModel) -> AuthTokens:
        claims = AccessTokenClaims(
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            role=user.role.value,
        )
        authenticated = AuthenticatedUser(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
        )
        return AuthTokens(
            access_token=self._token_service.create_access_token(claims),
            refresh_token=self._token_service.create_refresh_token(claims),
            user=authenticated,
        )

    async def _load_active_user(
        self,
        *,
        tenant_slug: str,
        email: str,
    ) -> UserModel | None:
        statement = (
            select(UserModel)
            .join(TenantModel, UserModel.tenant_id == TenantModel.id)
            .where(
                TenantModel.slug == tenant_slug,
                UserModel.email == email,
                UserModel.is_active.is_(True),
            )
            .options(selectinload(UserModel.tenant))
        )
        user: UserModel | None = await self._session.scalar(statement)
        return user
