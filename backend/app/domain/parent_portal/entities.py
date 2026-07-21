"""Parent portal domain: magic-link auth and student scoping."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4


def hash_magic_token(raw_token: str) -> str:
    """Return a SHA-256 hex digest of the opaque magic-link token."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_raw_magic_token() -> str:
    """Create a URL-safe one-time magic-link token."""
    return secrets.token_urlsafe(32)


@dataclass(frozen=True, slots=True)
class ParentStudentLink:
    """Associates a parent user with one student in the same tenant."""

    tenant_id: UUID
    parent_user_id: UUID
    student_id: UUID
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class MagicLinkToken:
    """One-time email login challenge for a parent user."""

    tenant_id: UUID
    user_id: UUID
    email: str
    token_hash: str
    expires_at: datetime
    id: UUID = field(default_factory=uuid4)
    used_at: datetime | None = None

    @classmethod
    def issue(
        cls,
        *,
        tenant_id: UUID,
        user_id: UUID,
        email: str,
        ttl_minutes: int,
        now: datetime | None = None,
    ) -> tuple[MagicLinkToken, str]:
        """Create a persisted challenge and return ``(entity, raw_token)``."""
        if ttl_minutes <= 0:
            raise ValueError("ttl_minutes must be positive")
        issued_at = now or datetime.now(UTC)
        raw = generate_raw_magic_token()
        entity = cls(
            tenant_id=tenant_id,
            user_id=user_id,
            email=email,
            token_hash=hash_magic_token(raw),
            expires_at=issued_at + timedelta(minutes=ttl_minutes),
        )
        return entity, raw

    def is_expired(self, *, now: datetime | None = None) -> bool:
        """Return True when the challenge is past ``expires_at``."""
        current = now or datetime.now(UTC)
        return current >= self.expires_at

    def is_usable(self, *, now: datetime | None = None) -> bool:
        """Return True when the token is unused and not expired."""
        return self.used_at is None and not self.is_expired(now=now)

    def consume(self, *, now: datetime | None = None) -> None:
        """Mark the token as used; raises if already used or expired."""
        if self.used_at is not None:
            raise ValueError("Magic link token already used")
        if self.is_expired(now=now):
            raise ValueError("Magic link token expired")
        self.used_at = now or datetime.now(UTC)
