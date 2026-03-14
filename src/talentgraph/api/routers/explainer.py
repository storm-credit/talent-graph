"""API router for algorithm explainer: formulas, glossary, score breakdowns."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from talentgraph.api.deps import get_engine
from talentgraph.explainer.definitions import (
    FormulaDefinition,
    GlossaryEntry,
    ScoreBreakdown,
)
from talentgraph.explainer.registry import get_all_formulas, get_glossary
from talentgraph.explainer.score_breakdown import compute_score_breakdown
from talentgraph.simulation.engine import SimulationEngine

router = APIRouter(prefix="/api/explainer", tags=["explainer"])


@router.get("/formulas", response_model=list[FormulaDefinition])
def list_formulas() -> list[FormulaDefinition]:
    """Return all algorithm formula definitions with academic references."""
    return get_all_formulas()


@router.get("/formulas/{formula_id}", response_model=FormulaDefinition)
def get_formula(formula_id: str) -> FormulaDefinition:
    """Return a single formula definition by ID."""
    formulas = get_all_formulas()
    for f in formulas:
        if f.id == formula_id:
            return f
    raise HTTPException(status_code=404, detail=f"Formula not found: {formula_id}")


@router.get("/glossary", response_model=list[GlossaryEntry])
def list_glossary() -> list[GlossaryEntry]:
    """Return all glossary term definitions."""
    return get_glossary()


@router.get("/glossary/{category}", response_model=list[GlossaryEntry])
def list_glossary_by_category(category: str) -> list[GlossaryEntry]:
    """Return glossary entries filtered by category."""
    entries = [g for g in get_glossary() if g.category == category]
    if not entries:
        raise HTTPException(
            status_code=404,
            detail=f"No glossary entries for category: {category}",
        )
    return entries


@router.get(
    "/breakdown/{person_id}/{role_id}/{department_id}",
    response_model=ScoreBreakdown,
)
def get_score_breakdown(
    person_id: UUID,
    role_id: UUID,
    department_id: UUID,
    engine: SimulationEngine = Depends(get_engine),
) -> ScoreBreakdown:
    """Return a step-by-step score breakdown for a person+role+department combination."""
    try:
        return compute_score_breakdown(
            company=engine.company,
            person_id=person_id,
            role_id=role_id,
            department_id=department_id,
            weights=engine.weights,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
