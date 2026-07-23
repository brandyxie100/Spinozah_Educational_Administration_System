"""Alembic revision: analysis_records for exam/essay persistence.

Revision ID: 0009_analysis_records
Revises: 0008_parent_magic_link
Create Date: 2026-07-24

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_analysis_records"
down_revision: str | None = "0008_parent_magic_link"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

analysis_kind = postgresql.ENUM(
    "exam",
    "essay",
    name="analysis_kind",
    create_type=False,
)


def upgrade() -> None:
    """Create analysis_records table and analysis_kind enum."""
    analysis_kind.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "analysis_records",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("kind", analysis_kind, nullable=False),
        sa.Column("student_name", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analysis_records_tenant_id",
        "analysis_records",
        ["tenant_id"],
    )
    op.create_index(
        "ix_analysis_records_student_id",
        "analysis_records",
        ["student_id"],
    )
    op.create_index(
        "ix_analysis_records_kind",
        "analysis_records",
        ["kind"],
    )


def downgrade() -> None:
    """Drop analysis_records table and analysis_kind enum."""
    op.drop_index("ix_analysis_records_kind", table_name="analysis_records")
    op.drop_index("ix_analysis_records_student_id", table_name="analysis_records")
    op.drop_index("ix_analysis_records_tenant_id", table_name="analysis_records")
    op.drop_table("analysis_records")
    analysis_kind.drop(op.get_bind(), checkfirst=True)
