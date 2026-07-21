"""Domain unit tests for magic-link tokens and parent-student links."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.domain.parent_portal import (
    MagicLinkToken,
    ParentStudentLink,
    hash_magic_token,
)


def test_issue_magic_link_hashes_raw_token() -> None:
    entity, raw = MagicLinkToken.issue(
        tenant_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        email="parent@example.com",
        ttl_minutes=15,
        now=datetime(2026, 7, 22, tzinfo=UTC),
    )
    assert entity.token_hash == hash_magic_token(raw)
    assert entity.used_at is None
    assert entity.is_usable(now=datetime(2026, 7, 22, tzinfo=UTC))


def test_consume_marks_token_used() -> None:
    entity, _raw = MagicLinkToken.issue(
        tenant_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        email="parent@example.com",
        ttl_minutes=15,
        now=datetime(2026, 7, 22, tzinfo=UTC),
    )
    entity.consume(now=datetime(2026, 7, 22, 0, 1, tzinfo=UTC))
    assert entity.used_at is not None
    with pytest.raises(ValueError, match="already used"):
        entity.consume(now=datetime(2026, 7, 22, 0, 2, tzinfo=UTC))


def test_expired_token_not_usable() -> None:
    now = datetime(2026, 7, 22, tzinfo=UTC)
    entity, _raw = MagicLinkToken.issue(
        tenant_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        email="parent@example.com",
        ttl_minutes=15,
        now=now,
    )
    later = now + timedelta(minutes=16)
    assert entity.is_expired(now=later)
    assert not entity.is_usable(now=later)
    with pytest.raises(ValueError, match="expired"):
        entity.consume(now=later)


def test_ttl_must_be_positive() -> None:
    with pytest.raises(ValueError, match="ttl_minutes must be positive"):
        MagicLinkToken.issue(
            tenant_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            email="parent@example.com",
            ttl_minutes=0,
        )


def test_parent_student_link_identity() -> None:
    link = ParentStudentLink(
        tenant_id=uuid.uuid4(),
        parent_user_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
    )
    assert link.id is not None
