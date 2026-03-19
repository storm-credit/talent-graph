"""Domain models for the Bayesian skill estimation system."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .enums import (
    ProjectDifficulty,
    ProjectResult,
    ProjectRole,
    ProjectStatus,
    SkillTrend,
)


class Project(BaseModel):
    """A work project that exercises specific skills."""

    id: UUID
    name: str
    description: str = ""
    difficulty: ProjectDifficulty = ProjectDifficulty.MODERATE
    required_skill_ids: list[UUID] = Field(default_factory=list)
    start_date: date
    end_date: date | None = None
    status: ProjectStatus = ProjectStatus.PLANNED
    created_at: datetime = Field(default_factory=datetime.now)


class ProjectAssignment(BaseModel):
    """Links a person to a project with a specific role."""

    id: UUID
    project_id: UUID
    person_id: UUID
    role_in_project: ProjectRole = ProjectRole.CONTRIBUTOR


class ProjectOutcome(BaseModel):
    """Recorded result of a person's work on a project."""

    id: UUID
    project_id: UUID
    person_id: UUID
    result: ProjectResult
    evaluated_at: date = Field(default_factory=date.today)
    notes: str = ""


class EstimateSnapshot(BaseModel):
    """A point-in-time snapshot of a skill estimate (for history/trend)."""

    mu: float
    sigma: float
    timestamp: datetime = Field(default_factory=datetime.now)


class SkillEstimate(BaseModel):
    """Bayesian estimate of a person's skill level.

    mu: estimated mean skill level (continuous 1.0-5.0)
    sigma: standard deviation (uncertainty)
    confidence: 1.0 - (sigma / sigma_initial), range [0, 1]
    """

    person_id: UUID
    skill_id: UUID
    mu: float = 3.0
    sigma: float = 1.5
    confidence: float = 0.0
    trend: SkillTrend = SkillTrend.STABLE
    update_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)
    history: list[EstimateSnapshot] = Field(default_factory=list)

    @property
    def discrete_level(self) -> int:
        """Quantize mu to nearest integer skill level (1-5)."""
        return max(1, min(5, round(self.mu)))

    @property
    def level_name(self) -> str:
        names = {1: "Novice", 2: "Beginner", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
        return names[self.discrete_level]
