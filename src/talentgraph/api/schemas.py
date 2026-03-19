"""API request/response schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


# ── Response schemas ──


class PersonSummary(BaseModel):
    id: UUID
    name: str
    tenure_years: float
    skill_count: int
    active_role: str | None
    active_department: str | None
    burnout_risk: float
    morale: float = 0.7
    potential: float = 0.7
    departed: bool = False


class DepartmentSummary(BaseModel):
    id: UUID
    name: str
    role_count: int
    member_count: int


class RoleSummary(BaseModel):
    id: UUID
    title: str
    level: int
    department_name: str
    required_skill_count: int


class FitResultResponse(BaseModel):
    person_id: UUID
    person_name: str
    department_id: UUID
    department_name: str
    role_id: UUID
    role_title: str
    skill_match_score: float
    historical_score: float
    level_match_score: float
    burnout_risk_score: float
    fit_score: float
    predicted_performance: float
    breakdown: dict[str, float]


class SkillInfo(BaseModel):
    id: UUID
    name: str
    category: str
    person_level: str | None = None
    person_years: float | None = None
    potential_level: str | None = None
    quarters_active: int = 0
    quarters_idle: int = 0
    required_level: str | None = None
    weight: float | None = None


class PersonDetail(BaseModel):
    id: UUID
    name: str
    tenure_years: float
    skills: list[SkillInfo]
    active_role: str | None
    active_department: str | None
    burnout_risk: float
    morale: float = 0.7
    potential: float = 0.7
    learning_rate: float = 1.0
    departed: bool = False
    fit_results: list[FitResultResponse]


class CompanyOverview(BaseModel):
    name: str
    people_count: int
    department_count: int
    role_count: int
    skill_count: int
    avg_tenure: float
    avg_burnout_risk: float


class ChangeResponse(BaseModel):
    person_id: UUID
    person_name: str
    change_type: str
    description: str
    old_value: str | None = None
    new_value: str | None = None


class OutcomeChangeResponse(ChangeResponse):
    role_title: str = ""
    department_name: str = ""
    rating: str = ""
    predicted_performance: float = 0.0


class QuarterAdvanceResponse(BaseModel):
    quarter: str
    changes: list[ChangeResponse]
    next_quarter: str


class PlacementResponse(BaseModel):
    person_name: str
    role_title: str
    department_name: str
    previous_role_title: str | None


class RollbackResponse(BaseModel):
    rolled_back_to: str
    history_length: int


class SimulationStatusResponse(BaseModel):
    current_quarter: str
    history_length: int
    people_count: int
    active_people: int = 0
    departed_people: int = 0
    average_morale: float = 0.0
    enhanced_mode: bool = False


# ── Request schemas ──


class PlacementRequest(BaseModel):
    person_id: UUID
    role_id: UUID
    department_id: UUID


class PreviewPlacementRequest(BaseModel):
    person_id: UUID
    role_id: UUID
    department_id: UUID


class RollbackRequest(BaseModel):
    steps: int = 1


class EnhancedModeRequest(BaseModel):
    enhanced: bool = True
    growth: bool = True
    morale: bool = True
    attrition: bool = True
    events: bool = True


# ── Graph schemas ──


class GraphNode(BaseModel):
    id: str
    type: str  # "department", "role", "person"
    label: str
    data: dict = {}


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
