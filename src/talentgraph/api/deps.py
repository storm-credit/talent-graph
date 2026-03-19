"""Dependency injection for FastAPI: shared SimulationEngine singleton."""

from __future__ import annotations

from talentgraph.data.seed import create_sample_company
from talentgraph.game.achievements import AchievementTracker
from talentgraph.scoring.weights import ScoringWeights
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures

from talentgraph.estimation.store import EstimationStore

_engine: SimulationEngine | None = None
_achievement_tracker: AchievementTracker | None = None
_score_history: list[dict] | None = None
_estimation_store: EstimationStore | None = None


def get_engine() -> SimulationEngine:
    global _engine
    if _engine is None:
        company = create_sample_company()
        features = SimulationFeatures(enhanced=True)
        _engine = SimulationEngine(company, seed=42, features=features)
    return _engine


def get_achievement_tracker() -> AchievementTracker:
    global _achievement_tracker
    if _achievement_tracker is None:
        _achievement_tracker = AchievementTracker()
    return _achievement_tracker


def get_score_history() -> list[dict]:
    global _score_history
    if _score_history is None:
        _score_history = []
    return _score_history


def get_estimation_store() -> EstimationStore:
    global _estimation_store
    if _estimation_store is None:
        _estimation_store = EstimationStore()
    return _estimation_store


def reset_engine() -> SimulationEngine:
    global _engine, _achievement_tracker, _score_history, _estimation_store
    _engine = None
    _achievement_tracker = None
    _score_history = None
    _estimation_store = None
    return get_engine()
