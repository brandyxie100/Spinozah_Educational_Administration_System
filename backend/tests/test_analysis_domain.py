"""Domain unit tests for analysis records."""

from __future__ import annotations

import uuid

import pytest
from app.domain.ai_analysis import AnalysisKind, AnalysisRecord


def test_analysis_record_requires_non_empty_payload() -> None:
    with pytest.raises(ValueError, match="payload must not be empty"):
        AnalysisRecord(
            tenant_id=uuid.uuid4(),
            kind=AnalysisKind.ESSAY,
            payload={},
        )


def test_analysis_record_accepts_exam_payload() -> None:
    record = AnalysisRecord(
        tenant_id=uuid.uuid4(),
        kind=AnalysisKind.EXAM,
        payload={"studentName": "Ada", "subject": "Math"},
        student_name="Ada",
        title="Math",
    )
    assert record.kind is AnalysisKind.EXAM
    assert record.payload["subject"] == "Math"
