"""Alembic revision: attendance_records table for check-in flow.

Revision ID: 0005_attendance
Revises: 0004_schedules
Create Date: 2026-07-22

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_attendance"
down_revision: str | None = "0004_schedules"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

attendance_status = postgresql.ENUM(
    "pending_confirmation",
    "present",
    "absent",
    name="attendance_status",
    create_type=False,
)


def upgrade() -> None:
    """Create attendance_records and attendance_status enum."""
    status_create = postgresql.ENUM(
        "pending_confirmation",
        "present",
        "absent",
        name="attendance_status",
    )
    status_create.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "attendance_records",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("schedule_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enrolment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", attendance_status, nullable=False),
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
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["schedules.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "schedule_id",
            name="uq_attendance_tenant_schedule",
        ),
    )
    op.create_index(
        "ix_attendance_records_tenant_id",
        "attendance_records",
        ["tenant_id"],
    )
    op.create_index(
        "ix_attendance_records_schedule_id",
        "attendance_records",
        ["schedule_id"],
    )
    op.create_index(
        "ix_attendance_records_student_id",
        "attendance_records",
        ["student_id"],
    )
    op.create_index(
        "ix_attendance_records_enrolment_id",
        "attendance_records",
        ["enrolment_id"],
    )


def downgrade() -> None:
    """Drop attendance_records table and attendance_status enum."""
    op.drop_index(
        "ix_attendance_records_enrolment_id",
        table_name="attendance_records",
    )
    op.drop_index(
        "ix_attendance_records_student_id",
        table_name="attendance_records",
    )
    op.drop_index(
        "ix_attendance_records_schedule_id",
        table_name="attendance_records",
    )
    op.drop_index(
        "ix_attendance_records_tenant_id",
        table_name="attendance_records",
    )
    op.drop_table("attendance_records")
    status_drop = postgresql.ENUM(name="attendance_status")
    status_drop.drop(op.get_bind(), checkfirst=True)
