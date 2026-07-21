"""Alembic revision: leave_requests + enrolment extension_days.

Revision ID: 0006_leave_policy
Revises: 0005_attendance
Create Date: 2026-07-22

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_leave_policy"
down_revision: str | None = "0005_attendance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

leave_kind = postgresql.ENUM(
    "sick",
    "personal",
    name="leave_kind",
    create_type=False,
)
leave_status = postgresql.ENUM(
    "pending",
    "approved",
    "rejected",
    name="leave_status",
    create_type=False,
)


def upgrade() -> None:
    """Add extension_days to enrolments and create leave_requests."""
    op.add_column(
        "enrolments",
        sa.Column(
            "extension_days",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    kind_create = postgresql.ENUM("sick", "personal", name="leave_kind")
    kind_create.create(op.get_bind(), checkfirst=True)
    status_create = postgresql.ENUM(
        "pending",
        "approved",
        "rejected",
        name="leave_status",
    )
    status_create.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "leave_requests",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enrolment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("leave_date", sa.Date(), nullable=False),
        sa.Column("kind", leave_kind, nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("status", leave_status, nullable=False),
        sa.Column("is_free", sa.Boolean(), nullable=True),
        sa.Column("extension_days_applied", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["enrolment_id"],
            ["enrolments.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leave_requests_tenant_id", "leave_requests", ["tenant_id"])
    op.create_index("ix_leave_requests_student_id", "leave_requests", ["student_id"])
    op.create_index(
        "ix_leave_requests_enrolment_id",
        "leave_requests",
        ["enrolment_id"],
    )


def downgrade() -> None:
    """Drop leave_requests and enrolment extension_days."""
    op.drop_index("ix_leave_requests_enrolment_id", table_name="leave_requests")
    op.drop_index("ix_leave_requests_student_id", table_name="leave_requests")
    op.drop_index("ix_leave_requests_tenant_id", table_name="leave_requests")
    op.drop_table("leave_requests")
    postgresql.ENUM(name="leave_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="leave_kind").drop(op.get_bind(), checkfirst=True)
    op.drop_column("enrolments", "extension_days")
