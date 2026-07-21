"""Schema tests for parent portal tables."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.parent_portal_models import (
    MagicLinkTokenModel,
    ParentStudentLinkModel,
)


def test_parent_portal_tables_registered() -> None:
    assert "parent_student_links" in Base.metadata.tables
    assert "magic_link_tokens" in Base.metadata.tables


def test_magic_link_stores_hash_not_raw_column() -> None:
    columns = MagicLinkTokenModel.__table__.c
    assert "token_hash" in columns
    assert "token" not in columns


def test_parent_student_link_unique_constraint() -> None:
    names = {
        constraint.name for constraint in ParentStudentLinkModel.__table__.constraints
    }
    assert "uq_parent_student_links_triplet" in names
