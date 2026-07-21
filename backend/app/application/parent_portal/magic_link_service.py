"""Application service for parent magic-link auth and student scoping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast
from urllib.parse import urlencode
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.identity.auth_service import AuthenticatedUser, AuthTokens
from app.domain.identity.exceptions import InvalidCredentialsError
from app.domain.identity.token_service import TokenService
from app.domain.identity.tokens import AccessTokenClaims
from app.domain.parent_portal.entities import MagicLinkToken, ParentStudentLink
from app.infrastructure.email.magic_link_mailer import MagicLinkMailer
from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.parent_portal_repository import (
    SqlAlchemyMagicLinkTokenRepository,
    SqlAlchemyParentStudentLinkRepository,
)
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)


@dataclass(frozen=True, slots=True)
class MagicLinkRequestResult:
    """Outcome of requesting a magic link (never leaks account existence)."""

    accepted: bool
    # Populated only when the mailer is a capture/test double or debug is on.
    magic_url: str | None = None


@dataclass(frozen=True, slots=True)
class LinkedStudentSummary:
    """Parent-visible student fields."""

    id: UUID
    full_name: str
    email: str | None
    is_active: bool


class ParentNotFoundError(Exception):
    """Raised when linking targets a missing parent user."""


class StudentNotFoundError(Exception):
    """Raised when linking targets a missing student."""


class NotAParentError(Exception):
    """Raised when the user exists but is not role=parent."""


class CaptureMagicLinkMailer:
    """In-memory mailer used by tests to capture the last magic URL."""

    def __init__(self) -> None:
        self.last_to_email: str | None = None
        self.last_magic_url: str | None = None

    async def send_magic_link(self, *, to_email: str, magic_url: str) -> None:
        """Store the last delivery for assertions."""
        self.last_to_email = to_email
        self.last_magic_url = magic_url


class MagicLinkTokenRepositoryPort(Protocol):
    """Persistence port for magic-link challenges."""

    async def add(self, token: MagicLinkToken) -> MagicLinkToken: ...

    async def get_by_raw_token(self, raw_token: str) -> MagicLinkToken | None: ...

    async def save(self, token: MagicLinkToken) -> MagicLinkToken: ...


class ParentPortalService:
    """Magic-link login and parent↔student link management."""

    def __init__(
        self,
        session: AsyncSession,
        token_service: TokenService,
        mailer: MagicLinkMailer,
        *,
        magic_link_ttl_minutes: int = 15,
        magic_link_base_url: str = "http://localhost:3000/parent/magic-link",
        expose_magic_url: bool = False,
    ) -> None:
        """Bind session, JWT minting, and magic-link delivery."""
        self._session = session
        self._token_service = token_service
        self._mailer = mailer
        self._ttl_minutes = magic_link_ttl_minutes
        self._base_url = magic_link_base_url.rstrip("/")
        self._expose_magic_url = expose_magic_url
        self._magic_links: MagicLinkTokenRepositoryPort = (
            SqlAlchemyMagicLinkTokenRepository(session)
        )

    async def request_magic_link(
        self,
        *,
        tenant_slug: str,
        email: str,
    ) -> MagicLinkRequestResult:
        """Issue a magic link for an active parent; always look successful."""
        user = await self._load_active_parent(tenant_slug=tenant_slug, email=email)
        if user is None:
            # Anti-enumeration: identical response whether or not the parent exists.
            return MagicLinkRequestResult(accepted=True, magic_url=None)

        challenge, raw_token = MagicLinkToken.issue(
            tenant_id=user.tenant_id,
            user_id=user.id,
            email=user.email,
            ttl_minutes=self._ttl_minutes,
        )
        await self._magic_links.add(challenge)
        magic_url = (
            f"{self._base_url}?{urlencode({'token': raw_token, 'tenant': tenant_slug})}"
        )
        await self._mailer.send_magic_link(to_email=user.email, magic_url=magic_url)
        return MagicLinkRequestResult(
            accepted=True,
            magic_url=magic_url if self._expose_magic_url else None,
        )

    async def consume_magic_link(self, *, raw_token: str) -> AuthTokens:
        """Validate a one-time magic link and mint parent JWTs."""
        challenge = await self._magic_links.get_by_raw_token(raw_token)
        if challenge is None:
            raise InvalidCredentialsError("Invalid or expired magic link")
        try:
            challenge.consume()
        except ValueError as exc:
            raise InvalidCredentialsError(str(exc)) from exc
        await self._magic_links.save(challenge)

        user = await self._session.get(UserModel, challenge.user_id)
        if (
            user is None
            or not user.is_active
            or user.role != UserRole.PARENT
            or user.tenant_id != challenge.tenant_id
        ):
            raise InvalidCredentialsError("Invalid or expired magic link")
        return self._issue_tokens(user)

    async def link_student(
        self,
        *,
        tenant_id: UUID,
        parent_user_id: UUID,
        student_id: UUID,
    ) -> ParentStudentLink:
        """Associate a parent user with a student (frontdesk/admin)."""
        parent = await self._session.get(UserModel, parent_user_id)
        if parent is None or parent.tenant_id != tenant_id:
            raise ParentNotFoundError(f"Parent user not found: {parent_user_id}")
        if parent.role != UserRole.PARENT:
            raise NotAParentError(f"User is not a parent: {parent_user_id}")

        students = SqlAlchemyStudentRepository(self._session, tenant_id)
        student = await students.get_by_id(student_id)
        if student is None:
            raise StudentNotFoundError(f"Student not found: {student_id}")

        link_repo = SqlAlchemyParentStudentLinkRepository(self._session, tenant_id)
        return await link_repo.add(
            ParentStudentLink(
                tenant_id=tenant_id,
                parent_user_id=parent_user_id,
                student_id=student_id,
            ),
        )

    async def list_linked_students(
        self,
        *,
        tenant_id: UUID,
        parent_user_id: UUID,
    ) -> list[LinkedStudentSummary]:
        """Return only students linked to the parent (portal scoping)."""
        link_repo = SqlAlchemyParentStudentLinkRepository(self._session, tenant_id)
        student_ids = await link_repo.list_student_ids_for_parent(parent_user_id)
        if not student_ids:
            return []

        students = SqlAlchemyStudentRepository(self._session, tenant_id)
        summaries: list[LinkedStudentSummary] = []
        for student_id in student_ids:
            row = await students.get_by_id(student_id)
            if row is None:
                continue
            summaries.append(
                LinkedStudentSummary(
                    id=row.id,
                    full_name=row.full_name,
                    email=row.email,
                    is_active=row.is_active,
                ),
            )
        return summaries

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

    async def _load_active_parent(
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
                UserModel.role == UserRole.PARENT,
            )
            .options(selectinload(UserModel.tenant))
        )
        return cast(UserModel | None, await self._session.scalar(statement))


__all__ = [
    "CaptureMagicLinkMailer",
    "LinkedStudentSummary",
    "MagicLinkRequestResult",
    "NotAParentError",
    "ParentNotFoundError",
    "ParentPortalService",
    "StudentNotFoundError",
]
