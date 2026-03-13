"""Weights endpoint: get/update scoring weights."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from talentgraph.api.deps import get_engine
from talentgraph.scoring.weights import ScoringWeights
from talentgraph.simulation.engine import SimulationEngine

router = APIRouter(prefix="/api/weights", tags=["weights"])


@router.get("", response_model=ScoringWeights)
def get_weights(engine: SimulationEngine = Depends(get_engine)):
    return engine.weights


@router.put("", response_model=ScoringWeights)
def update_weights(weights: ScoringWeights, engine: SimulationEngine = Depends(get_engine)):
    engine.weights = weights
    return engine.weights
