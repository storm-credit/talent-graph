"""Recommendation API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from talentgraph.api.deps import get_engine
from talentgraph.recommendation.engine import RecommendationEngine
from talentgraph.simulation.engine import SimulationEngine

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _get_rec_engine(engine: SimulationEngine = Depends(get_engine)) -> RecommendationEngine:
    return RecommendationEngine(engine.company, engine.weights)


@router.get("/person/{person_id}")
def best_roles_for_person(
    person_id: UUID,
    top_n: int = 3,
    rec_engine: RecommendationEngine = Depends(_get_rec_engine),
):
    """Get top N role recommendations for a person."""
    recs = rec_engine.best_roles_for_person(person_id, top_n)
    return [r.model_dump() for r in recs]


@router.get("/role/{role_id}/{department_id}")
def best_candidates_for_role(
    role_id: UUID,
    department_id: UUID,
    top_n: int = 5,
    rec_engine: RecommendationEngine = Depends(_get_rec_engine),
):
    """Get top N candidate recommendations for a role."""
    recs = rec_engine.best_candidates_for_role(role_id, department_id, top_n)
    return [r.model_dump() for r in recs]


@router.get("/matrix")
def placement_matrix(
    rec_engine: RecommendationEngine = Depends(_get_rec_engine),
):
    """Get full person × role fit score matrix."""
    cells = rec_engine.placement_matrix()
    return [c.model_dump() for c in cells]
