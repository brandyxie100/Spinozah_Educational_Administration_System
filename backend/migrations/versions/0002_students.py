"""Alembic revision: students and enrolments tables.

Revision ID: 0002_students
Revises: 0001_baseline
Create Date: 2026-07-21

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_students"
down_revision: str | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

enrolment_status = postgresql.ENUM(
    "active",
    "completed",
    "cancelled",
    name="enrolment_status",
    create_type=False,
)


def upgrade() -> None:
    """Create students, enrolments, and enrolment_status enum."""
    status_create = postgresql.ENUM(
        "active",
        "completed",
        "cancelled",
        name="enrolment_status",
    )
    status_create.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "students",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_students_tenant_email"),
    )
    op.create_index("ix_students_tenant_id", "students", ["tenant_id"])

    op.create_table(
        "enrolments",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_lessons", sa.Integer(), nullable=False),
        sa.Column("completed_lessons", sa.Integer(), nullable=False),
        sa.Column("status", enrolment_status, nullable=False),
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
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_enrolments_tenant_id", "enrolments", ["tenant_id"])
    op.create_index("ix_enrolments_student_id", "enrolments", ["student_id"])


def downgrade() -> None:
    """Drop enrolments and students tables."""
    op.drop_index("ix_enrolments_student_id", table_name="enrolments")
    op.drop_index("ix_enrolments_tenant_id", table_name="enrolments")
    op.drop_table("enrolments")
    op.drop_index("ix_students_tenant_id", table_name="students")
    op.drop_table("students")
    status_drop = postgresql.ENUM(name="enrolment_status")
    status_drop.drop(op.get_bind(), checkfirst=True)
