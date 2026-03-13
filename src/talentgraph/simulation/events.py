"""Simulation event types for placement and outcomes."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from talentgraph.ontology.enums import OutcomeRating


class OutcomeEvent(BaseModel):
    """An outcome rating generated during quarter simulation."""

    person_id: UUID
    person_name: str
    role_id: UUID
    role_title: str
    department_id: UUID
    department_name: str
    rating: OutcomeRating
    predicted_performance: float


class PlacementEvent(BaseModel):
    """A person placement (new assignment) event."""

    person_id: UUID
    person_name: str
    role_id: UUID
    role_title: str
    department_id: UUID
    department_name: str
    previous_role_id: UUID | None = None
    previous_role_title: str | None = None
