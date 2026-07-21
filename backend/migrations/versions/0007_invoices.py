"""Alembic revision: invoices table with payment status.

Revision ID: 0007_invoices
Revises: 0006_leave_policy
Create Date: 2026-07-22

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_invoices"
down_revision: str | None = "0006_leave_policy"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

payment_status = postgresql.ENUM(
    "unpaid",
    "partial",
    "paid",
    "void",
    name="payment_status",
    create_type=False,
)


def upgrade() -> None:
    """Create invoices table and payment_status enum."""
    status_create = postgresql.ENUM(
        "unpaid",
        "partial",
        "paid",
        "void",
        name="payment_status",
    )
    status_create.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "invoices",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enrolment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("semester_label", sa.String(length=100), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("credit", sa.Numeric(12, 2), nullable=False),
        sa.Column("final_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", payment_status, nullable=False),
        sa.Column(
            "line_items",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
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
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "student_id",
            "semester_label",
            name="uq_invoices_tenant_student_semester",
        ),
    )
    op.create_index("ix_invoices_tenant_id", "invoices", ["tenant_id"])
    op.create_index("ix_invoices_student_id", "invoices", ["student_id"])
    op.create_index("ix_invoices_enrolment_id", "invoices", ["enrolment_id"])


def downgrade() -> None:
    """Drop invoices table and payment_status enum."""
    op.drop_index("ix_invoices_enrolment_id", table_name="invoices")
    op.drop_index("ix_invoices_student_id", table_name="invoices")
    op.drop_index("ix_invoices_tenant_id", table_name="invoices")
    op.drop_table("invoices")
    postgresql.ENUM(name="payment_status").drop(op.get_bind(), checkfirst=True)
