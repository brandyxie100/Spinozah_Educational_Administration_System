"""AI analysis record domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class AnalysisKind(StrEnum):
    """Supported persisted analysis report kinds."""

    EXAM = "exam"
    ESSAY = "essay"


@dataclass(slots=True)
class AnalysisRecord:
    """Persisted exam or essay analysis report for a tenant."""

    tenant_id: UUID
    kind: AnalysisKind
    payload: dict[str, Any]
    student_id: UUID | None = None
    student_name: str | None = None
    title: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Require a non-empty payload object."""
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be an object")
        if not self.payload:
            raise ValueError("payload must not be empty")
