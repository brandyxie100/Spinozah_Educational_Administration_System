"""Tenant-scoped repositories for parent portal persistence."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.parent_portal.entities import (
    MagicLinkToken,
    ParentStudentLink,
    hash_magic_token,
)
from app.infrastructure.persistence.parent_portal_mapper import (
    apply_magic_link_to_model,
    link_to_model,
    magic_link_to_model,
    model_to_link,
    model_to_magic_link,
)
from app.infrastructure.persistence.parent_portal_models import (
    MagicLinkTokenModel,
    ParentStudentLinkModel,
)
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyParentStudentLinkRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate parent↔student links within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create a link repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def add(self, link: ParentStudentLink) -> ParentStudentLink:
        """Persist a new parent-student association."""
        if link.tenant_id != self._tenant_id:
            raise ValueError("Cannot add link for a different tenant")
        model = link_to_model(link)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_link(model)

    async def list_student_ids_for_parent(self, parent_user_id: UUID) -> list[UUID]:
        """Return student ids linked to the parent in this tenant."""
        statement = self._scoped(
            select(ParentStudentLinkModel.student_id).where(
                ParentStudentLinkModel.parent_user_id == parent_user_id,
            ),
            ParentStudentLinkModel,
        )
        result = await self._session.scalars(statement)
        return list(result.all())


class SqlAlchemyMagicLinkTokenRepository:
    """Persist and look up magic-link challenges (hash lookup is global)."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to a unit-of-work session."""
        self._session = session

    async def add(self, token: MagicLinkToken) -> MagicLinkToken:
        """Store a new magic-link challenge."""
        model = magic_link_to_model(token)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_magic_link(model)

    async def get_by_raw_token(self, raw_token: str) -> MagicLinkToken | None:
        """Load a challenge by hashing the opaque raw token."""
        token_hash = hash_magic_token(raw_token)
        statement = select(MagicLinkTokenModel).where(
            MagicLinkTokenModel.token_hash == token_hash,
        )
        model = cast(
            MagicLinkTokenModel | None,
            await self._session.scalar(statement),
        )
        return model_to_magic_link(model) if model is not None else None

    async def save(self, token: MagicLinkToken) -> MagicLinkToken:
        """Persist updates (e.g. ``used_at``) for an existing challenge."""
        statement = select(MagicLinkTokenModel).where(
            MagicLinkTokenModel.id == token.id,
        )
        model = cast(
            MagicLinkTokenModel | None,
            await self._session.scalar(statement),
        )
        if model is None:
            raise ValueError(f"Magic link token not found: {token.id}")
        apply_magic_link_to_model(model, token)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_magic_link(model)
