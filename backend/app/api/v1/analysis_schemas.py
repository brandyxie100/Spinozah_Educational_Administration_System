"""Pydantic schemas for analysis persistence APIs."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.ai_analysis.entities import AnalysisKind


class AnalysisCreateRequest(BaseModel):
    """Payload to persist an exam or essay analysis report."""

    kind: AnalysisKind
    payload: dict[str, Any] = Field(min_length=1)
    student_id: UUID | None = None


class AnalysisOut(BaseModel):
    """Public analysis record representation."""

    id: UUID
    tenant_id: UUID
    kind: str
    student_id: UUID | None
    student_name: str | None
    title: str | None
    payload: dict[str, Any]
