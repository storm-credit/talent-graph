"""API endpoint tests using FastAPI TestClient."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from talentgraph.api.app import app
from talentgraph.api import deps
from talentgraph.data.seed import _id, create_sample_company
from talentgraph.simulation.engine import SimulationEngine


@pytest.fixture(autouse=True)
def fresh_engine():
    """Reset the engine singleton for each test."""
    engine = SimulationEngine(create_sample_company(), seed=42)
    app.dependency_overrides[deps.get_engine] = lambda: engine
    yield engine
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


class TestHealth:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestCompany:
    def test_get_company(self, client):
        r = client.get("/api/company")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Acme Corp"
        assert data["people_count"] == 5
        assert data["department_count"] == 4
        assert data["role_count"] == 6
        assert data["skill_count"] == 8


class TestPeople:
    def test_list_people(self, client):
        r = client.get("/api/people")
        assert r.status_code == 200
        people = r.json()
        assert len(people) == 5
        names = {p["name"] for p in people}
        assert "Alice Chen" in names

    def test_get_person(self, client):
        alice_id = str(_id("person:alice"))
        r = client.get(f"/api/people/{alice_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Alice Chen"
        assert len(data["skills"]) > 0
        assert len(data["fit_results"]) > 0

    def test_get_person_not_found(self, client):
        r = client.get("/api/people/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_evaluate_person(self, client):
        alice_id = str(_id("person:alice"))
        r = client.get(f"/api/people/{alice_id}/evaluate")
        assert r.status_code == 200
        results = r.json()
        assert len(results) > 0
        assert all(0 <= r["fit_score"] <= 1 for r in results)


class TestSimulation:
    def test_status(self, client):
        r = client.get("/api/simulation/status")
        assert r.status_code == 200
        data = r.json()
        assert data["current_quarter"] == "2025-Q1"
        assert data["history_length"] == 0

    def test_advance(self, client):
        r = client.post("/api/simulation/advance")
        assert r.status_code == 200
        data = r.json()
        assert data["quarter"] == "2025-Q1"
        assert data["next_quarter"] == "2025-Q2"
        assert len(data["changes"]) > 0

    def test_advance_twice(self, client):
        client.post("/api/simulation/advance")
        r = client.post("/api/simulation/advance")
        assert r.status_code == 200
        data = r.json()
        assert data["quarter"] == "2025-Q2"

    def test_place(self, client):
        r = client.post(
            "/api/simulation/place",
            json={
                "person_id": str(_id("person:bob")),
                "role_id": str(_id("role:sr_data_eng")),
                "department_id": str(_id("dept:data_eng")),
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["person_name"] == "Bob Park"
        assert data["role_title"] == "Senior Data Engineer"

    def test_preview_place(self, client):
        r = client.post(
            "/api/simulation/preview-place",
            json={
                "person_id": str(_id("person:alice")),
                "role_id": str(_id("role:eng_manager")),
                "department_id": str(_id("dept:eng_mgmt")),
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["role_title"] == "Engineering Manager"
        assert 0 <= data["fit_score"] <= 1

    def test_rollback(self, client):
        client.post("/api/simulation/advance")
        client.post("/api/simulation/advance")
        r = client.post("/api/simulation/rollback", json={"steps": 1})
        assert r.status_code == 200
        data = r.json()
        assert data["rolled_back_to"] == "2025-Q2"

    def test_reset(self, client):
        client.post("/api/simulation/advance")
        r = client.post("/api/simulation/reset")
        assert r.status_code == 200
        data = r.json()
        assert data["current_quarter"] == "2025-Q1"
        assert data["history_length"] == 0


class TestGraph:
    def test_get_graph(self, client):
        r = client.get("/api/graph")
        assert r.status_code == 200
        data = r.json()
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0

        types = {n["type"] for n in data["nodes"]}
        assert "department" in types
        assert "role" in types
        assert "person" in types


class TestWeights:
    def test_get_weights(self, client):
        r = client.get("/api/weights")
        assert r.status_code == 200
        data = r.json()
        assert data["skill_match"] == 0.4

    def test_update_weights(self, client):
        r = client.put(
            "/api/weights",
            json={
                "skill_match": 0.5,
                "historical_performance": 0.2,
                "level_match": 0.2,
                "burnout_risk": 0.1,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["skill_match"] == 0.5
