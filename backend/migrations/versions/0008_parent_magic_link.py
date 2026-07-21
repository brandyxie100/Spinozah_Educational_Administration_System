"""Alembic revision: parent-student links and magic-link tokens.

Revision ID: 0008_parent_magic_link
Revises: 0007_invoices
Create Date: 2026-07-22

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_parent_magic_link"
down_revision: str | None = "0007_invoices"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create parent_student_links and magic_link_tokens tables."""
    op.create_table(
        "parent_student_links",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.ForeignKeyConstraint(["parent_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "parent_user_id",
            "student_id",
            name="uq_parent_student_links_triplet",
        ),
    )
    op.create_index(
        "ix_parent_student_links_tenant_id",
        "parent_student_links",
        ["tenant_id"],
    )
    op.create_index(
        "ix_parent_student_links_parent_user_id",
        "parent_student_links",
        ["parent_user_id"],
    )
    op.create_index(
        "ix_parent_student_links_student_id",
        "parent_student_links",
        ["student_id"],
    )

    op.create_table(
        "magic_link_tokens",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_magic_link_tokens_tenant_id",
        "magic_link_tokens",
        ["tenant_id"],
    )
    op.create_index(
        "ix_magic_link_tokens_user_id",
        "magic_link_tokens",
        ["user_id"],
    )


def downgrade() -> None:
    """Drop magic-link and parent-student link tables."""
    op.drop_index("ix_magic_link_tokens_user_id", table_name="magic_link_tokens")
    op.drop_index("ix_magic_link_tokens_tenant_id", table_name="magic_link_tokens")
    op.drop_table("magic_link_tokens")
    op.drop_index(
        "ix_parent_student_links_student_id",
        table_name="parent_student_links",
    )
    op.drop_index(
        "ix_parent_student_links_parent_user_id",
        table_name="parent_student_links",
    )
    op.drop_index(
        "ix_parent_student_links_tenant_id",
        table_name="parent_student_links",
    )
    op.drop_table("parent_student_links")
