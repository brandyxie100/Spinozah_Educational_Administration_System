"""Map parent portal domain entities to ORM rows."""

from __future__ import annotations

from app.domain.parent_portal.entities import MagicLinkToken, ParentStudentLink
from app.infrastructure.persistence.parent_portal_models import (
    MagicLinkTokenModel,
    ParentStudentLinkModel,
)


def link_to_model(link: ParentStudentLink) -> ParentStudentLinkModel:
    """Convert a domain parent-student link into a persistence model."""
    return ParentStudentLinkModel(
        id=link.id,
        tenant_id=link.tenant_id,
        parent_user_id=link.parent_user_id,
        student_id=link.student_id,
    )


def model_to_link(model: ParentStudentLinkModel) -> ParentStudentLink:
    """Convert a persistence row into a domain parent-student link."""
    return ParentStudentLink(
        id=model.id,
        tenant_id=model.tenant_id,
        parent_user_id=model.parent_user_id,
        student_id=model.student_id,
    )


def magic_link_to_model(token: MagicLinkToken) -> MagicLinkTokenModel:
    """Convert a domain magic-link challenge into a persistence model."""
    return MagicLinkTokenModel(
        id=token.id,
        tenant_id=token.tenant_id,
        user_id=token.user_id,
        email=token.email,
        token_hash=token.token_hash,
        expires_at=token.expires_at,
        used_at=token.used_at,
    )


def model_to_magic_link(model: MagicLinkTokenModel) -> MagicLinkToken:
    """Convert a persistence row into a domain magic-link challenge."""
    return MagicLinkToken(
        id=model.id,
        tenant_id=model.tenant_id,
        user_id=model.user_id,
        email=model.email,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        used_at=model.used_at,
    )


def apply_magic_link_to_model(
    model: MagicLinkTokenModel,
    token: MagicLinkToken,
) -> None:
    """Copy mutable magic-link fields onto an existing ORM row."""
    model.used_at = token.used_at
