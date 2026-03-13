"""Simulation state models: snapshots, change records, quarter tracking."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from talentgraph.ontology.enums import OutcomeRating
from talentgraph.ontology.models import Company


class QuarterLabel(BaseModel):
    """Represents a fiscal quarter like 2025-Q1."""

    year: int
    quarter: int = Field(ge=1, le=4)

    def next(self) -> QuarterLabel:
        if self.quarter == 4:
            return QuarterLabel(year=self.year + 1, quarter=1)
        return QuarterLabel(year=self.year, quarter=self.quarter + 1)

    def __str__(self) -> str:
        return f"{self.year}-Q{self.quarter}"


class ChangeRecord(BaseModel):
    """A single change that happened during a quarter advance."""

    person_id: UUID
    person_name: str
    change_type: str  # "outcome", "placement", "burnout_change"
    description: str
    old_value: str | None = None
    new_value: str | None = None


class OutcomeRecord(ChangeRecord):
    """Outcome generated for a person during quarter advance."""

    role_title: str = ""
    department_name: str = ""
    rating: OutcomeRating = OutcomeRating.MEETS
    predicted_performance: float = 3.0


class QuarterSnapshot(BaseModel):
    """Snapshot of state after a quarter is processed."""

    quarter: QuarterLabel
    company: Company
    changes: list[ChangeRecord] = []


class SimulationState(BaseModel):
    """Full simulation state with history and rollback support."""

    current_quarter: QuarterLabel = Field(
        default_factory=lambda: QuarterLabel(year=2025, quarter=1)
    )
    history: list[QuarterSnapshot] = []
    initial_company: Company | None = None
