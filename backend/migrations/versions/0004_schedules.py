"""Alembic revision: schedules table with status and weekly recurrence.

Revision ID: 0004_schedules
Revises: 0003_teachers
Create Date: 2026-07-21

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_schedules"
down_revision: str | None = "0003_teachers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

schedule_status = postgresql.ENUM(
    "not_started",
    "in_progress",
    "completed",
    "cancelled",
    "rescheduled",
    name="schedule_status",
    create_type=False,
)


def upgrade() -> None:
    """Create schedules table and schedule_status enum."""
    status_create = postgresql.ENUM(
        "not_started",
        "in_progress",
        "completed",
        "cancelled",
        "rescheduled",
        name="schedule_status",
    )
    status_create.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "schedules",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("classroom", sa.String(length=100), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", schedule_status, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False),
        sa.Column("recurrence_weekday", sa.Integer(), nullable=True),
        sa.Column("recurrence_until", sa.Date(), nullable=True),
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
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schedules_tenant_id", "schedules", ["tenant_id"])
    op.create_index("ix_schedules_teacher_id", "schedules", ["teacher_id"])
    op.create_index("ix_schedules_student_id", "schedules", ["student_id"])


def downgrade() -> None:
    """Drop schedules table and schedule_status enum."""
    op.drop_index("ix_schedules_student_id", table_name="schedules")
    op.drop_index("ix_schedules_teacher_id", table_name="schedules")
    op.drop_index("ix_schedules_tenant_id", table_name="schedules")
    op.drop_table("schedules")
    status_drop = postgresql.ENUM(name="schedule_status")
    status_drop.drop(op.get_bind(), checkfirst=True)
