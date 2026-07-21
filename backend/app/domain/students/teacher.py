"""Teacher domain entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(slots=True)
class Teacher:
    """Instructor profile belonging to a single tenant.

    Optionally links to a platform user account (login identity).
    """

    tenant_id: UUID
    full_name: str
    email: str | None = None
    user_id: UUID | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Require a non-empty display name."""
        if not self.full_name.strip():
            raise ValueError("full_name must not be empty")

    def link_user(self, user_id: UUID) -> None:
        """Associate this teacher with a platform user account."""
        self.user_id = user_id

    def unlink_user(self) -> None:
        """Clear the optional platform user link."""
        self.user_id = None

    def deactivate(self) -> None:
        """Soft-deactivate the teacher profile."""
        self.is_active = False
