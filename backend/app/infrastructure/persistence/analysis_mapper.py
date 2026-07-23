"""Map analysis domain entities to ORM rows."""

from __future__ import annotations

from app.domain.ai_analysis.entities import AnalysisKind, AnalysisRecord
from app.infrastructure.persistence.analysis_models import (
    AnalysisKindDB,
    AnalysisRecordModel,
)


def analysis_to_model(record: AnalysisRecord) -> AnalysisRecordModel:
    """Convert a domain analysis record into a persistence model."""
    return AnalysisRecordModel(
        id=record.id,
        tenant_id=record.tenant_id,
        student_id=record.student_id,
        kind=AnalysisKindDB(record.kind.value),
        student_name=record.student_name,
        title=record.title,
        payload=record.payload,
    )


def model_to_analysis(model: AnalysisRecordModel) -> AnalysisRecord:
    """Convert a persistence row into a domain analysis record."""
    return AnalysisRecord(
        id=model.id,
        tenant_id=model.tenant_id,
        student_id=model.student_id,
        kind=AnalysisKind(model.kind.value),
        student_name=model.student_name,
        title=model.title,
        payload=dict(model.payload),
    )
