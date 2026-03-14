"""Pydantic models for algorithm explanations, glossary, and score breakdowns."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class VariableDefinition(BaseModel):
    """A variable used in a formula."""

    symbol: str
    name_ko: str
    name_en: str
    range: str  # e.g., "[0.0, 1.0]"
    description_ko: str
    description_en: str


class ConstantDefinition(BaseModel):
    """A constant/parameter used in a formula."""

    symbol: str
    name_en: str
    value: str  # string to support both numeric and descriptive
    description_ko: str
    description_en: str
    source: str  # academic reference or design rationale


class FormulaDefinition(BaseModel):
    """Full description of an algorithm formula."""

    id: str
    name_ko: str
    name_en: str
    formula_plain: str  # plain text formula
    description_ko: str
    description_en: str
    variables: list[VariableDefinition] = []
    constants: list[ConstantDefinition] = []
    theoretical_basis: str  # academic reference
    theoretical_basis_ko: str
    category: str  # "scoring", "simulation", "growth", "morale", "attrition", "events"
    related_formulas: list[str] = []  # IDs of related formulas


class GlossaryEntry(BaseModel):
    """A glossary term definition."""

    id: str
    term_ko: str
    term_en: str
    definition_ko: str
    definition_en: str
    category: str  # "core", "scoring", "simulation", "skill", "metric"


class ScoreStep(BaseModel):
    """A single step in a score breakdown."""

    step_number: int
    component: str  # "skill_match", "historical", "level_match", "burnout_risk"
    component_ko: str
    formula_applied: str  # e.g., "min(4/4, 1.0) * 5.0 = 5.0"
    inputs: dict[str, Any]
    intermediate_value: float
    weight: float
    weighted_value: float
    explanation_ko: str
    explanation_en: str


class ScoreBreakdown(BaseModel):
    """Step-by-step breakdown of a fit score calculation."""

    person_id: str
    person_name: str
    role_id: str
    role_title: str
    department_id: str
    department_name: str
    steps: list[ScoreStep]
    final_fit_score: float
    final_predicted_performance: float
    summary_ko: str
    summary_en: str
