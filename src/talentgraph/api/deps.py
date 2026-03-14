"""Dependency injection for FastAPI: shared SimulationEngine singleton."""

from __future__ import annotations

from talentgraph.data.seed import create_sample_company
from talentgraph.scoring.weights import ScoringWeights
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures

_engine: SimulationEngine | None = None


def get_engine() -> SimulationEngine:
    global _engine
    if _engine is None:
        company = create_sample_company()
        features = SimulationFeatures(enhanced=True)
        _engine = SimulationEngine(company, seed=42, features=features)
    return _engine


def reset_engine() -> SimulationEngine:
    global _engine
    _engine = None
    return get_engine()
