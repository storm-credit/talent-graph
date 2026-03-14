"""API endpoint tests for game module."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from talentgraph.api.app import app
from talentgraph.api import deps
from talentgraph.data.seed import create_sample_company
from talentgraph.game.achievements import AchievementTracker
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures


@pytest.fixture(autouse=True)
def fresh_state():
    """Reset engine, tracker, and score history for each test."""
    engine = SimulationEngine(
        create_sample_company(),
        seed=42,
        features=SimulationFeatures(enhanced=True),
    )
    tracker = AchievementTracker()
    score_history: list[dict] = []

    app.dependency_overrides[deps.get_engine] = lambda: engine
    app.dependency_overrides[deps.get_achievement_tracker] = lambda: tracker
    app.dependency_overrides[deps.get_score_history] = lambda: score_history
    yield engine, tracker, score_history
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


class TestGameScore:
    def test_get_score(self, client):
        r = client.get("/api/game/score")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert 0 <= data["total"] <= 100

    def test_score_history_empty(self, client):
        r = client.get("/api/game/score/history")
        assert r.status_code == 200
        assert r.json() == []


class TestGameAchievements:
    def test_get_achievements(self, client):
        r = client.get("/api/game/achievements")
        assert r.status_code == 200
        data = r.json()
        assert "achievements" in data
        assert "progress" in data
        assert len(data["achievements"]) == 15

    def test_get_unlocked_achievements_initially_empty(self, client):
        r = client.get("/api/game/achievements/unlocked")
        assert r.status_code == 200
        assert r.json() == []


class TestGameAdvance:
    def test_advance_with_report(self, client):
        r = client.post("/api/game/advance")
        assert r.status_code == 200
        data = r.json()
        assert "report" in data
        assert "newly_unlocked" in data
        assert "achievement_progress" in data
        assert "next_quarter" in data

        report = data["report"]
        assert "quarter" in report
        assert "company_score" in report
        assert "headlines" in report
        assert "total_active" in report

    def test_advance_unlocks_first_quarter(self, client):
        r = client.post("/api/game/advance")
        data = r.json()
        unlocked_ids = [a["id"] for a in data["newly_unlocked"]]
        assert "first_quarter" in unlocked_ids

    def test_advance_builds_score_history(self, client):
        # Advance 3 times
        for _ in range(3):
            client.post("/api/game/advance")

        r = client.get("/api/game/score/history")
        history = r.json()
        assert len(history) == 3
        assert all("quarter" in h and "total" in h for h in history)

    def test_advance_has_score_delta_after_first(self, client):
        # First advance: no delta
        r1 = client.post("/api/game/advance")
        assert r1.json()["report"]["score_delta"] is None

        # Second advance: has delta
        r2 = client.post("/api/game/advance")
        assert r2.json()["report"]["score_delta"] is not None

    def test_latest_report_before_advance(self, client):
        r = client.get("/api/game/report/latest")
        assert r.status_code == 200
        assert "detail" in r.json()  # "No quarters simulated yet"

    def test_latest_report_after_advance(self, client):
        client.post("/api/game/advance")
        r = client.get("/api/game/report/latest")
        assert r.status_code == 200
        data = r.json()
        assert "quarter" in data
        assert "company_score" in data
