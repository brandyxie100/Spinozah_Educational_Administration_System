"""Alembic revision: teachers table with optional user link.

Revision ID: 0003_teachers
Revises: 0002_students
Create Date: 2026-07-21

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_teachers"
down_revision: str | None = "0002_students"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create teachers table with optional users.id foreign key."""
    op.create_table(
        "teachers",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_teachers_tenant_email"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_teachers_tenant_user"),
    )
    op.create_index("ix_teachers_tenant_id", "teachers", ["tenant_id"])
    op.create_index("ix_teachers_user_id", "teachers", ["user_id"])


def downgrade() -> None:
    """Drop teachers table."""
    op.drop_index("ix_teachers_user_id", table_name="teachers")
    op.drop_index("ix_teachers_tenant_id", table_name="teachers")
    op.drop_table("teachers")
