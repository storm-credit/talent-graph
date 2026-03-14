"""Tests for explainer API endpoints."""

import pytest
from fastapi.testclient import TestClient

from talentgraph.api.app import app
from talentgraph.api.deps import reset_engine, get_engine


@pytest.fixture(autouse=True)
def _reset():
    """Reset engine before each test."""
    reset_engine()
    yield


@pytest.fixture
def client():
    return TestClient(app)


class TestFormulasEndpoint:
    """Tests for GET /api/explainer/formulas."""

    def test_get_all_formulas(self, client):
        resp = client.get("/api/explainer/formulas")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 12
        assert all("id" in f for f in data)
        assert all("name_ko" in f for f in data)

    def test_get_single_formula(self, client):
        resp = client.get("/api/explainer/formulas/fit_score")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "fit_score"
        assert data["category"] == "scoring"

    def test_get_nonexistent_formula(self, client):
        resp = client.get("/api/explainer/formulas/nonexistent")
        assert resp.status_code == 404


class TestGlossaryEndpoint:
    """Tests for GET /api/explainer/glossary."""

    def test_get_all_glossary(self, client):
        resp = client.get("/api/explainer/glossary")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 20
        assert all("term_ko" in g for g in data)

    def test_get_glossary_by_category(self, client):
        resp = client.get("/api/explainer/glossary/core")
        assert resp.status_code == 200
        data = resp.json()
        assert all(g["category"] == "core" for g in data)

    def test_get_glossary_invalid_category(self, client):
        resp = client.get("/api/explainer/glossary/nonexistent")
        assert resp.status_code == 404


class TestBreakdownEndpoint:
    """Tests for GET /api/explainer/breakdown/{p}/{r}/{d}."""

    def test_get_breakdown(self, client):
        engine = get_engine()
        person = engine.company.people[0]
        dept = engine.company.departments[0]
        role_id = dept.roles[0]  # dept.roles is list[UUID]
        role = next(r for r in engine.company.roles if r.id == role_id)

        resp = client.get(
            f"/api/explainer/breakdown/{person.id}/{role_id}/{dept.id}"
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["person_name"] == person.name
        assert data["role_title"] == role.title
        assert len(data["steps"]) == 4
        assert 0.0 <= data["final_fit_score"] <= 1.0
        assert 1.0 <= data["final_predicted_performance"] <= 5.0
        assert data["summary_ko"]
        assert data["summary_en"]

    def test_breakdown_invalid_person(self, client):
        engine = get_engine()
        dept = engine.company.departments[0]
        role_id = dept.roles[0]

        resp = client.get(
            f"/api/explainer/breakdown/00000000-0000-0000-0000-000000000000/{role_id}/{dept.id}"
        )
        assert resp.status_code == 404

    def test_breakdown_steps_structure(self, client):
        engine = get_engine()
        person = engine.company.people[0]
        dept = engine.company.departments[0]
        role_id = dept.roles[0]

        resp = client.get(
            f"/api/explainer/breakdown/{person.id}/{role_id}/{dept.id}"
        )
        data = resp.json()

        for step in data["steps"]:
            assert "step_number" in step
            assert "component" in step
            assert "component_ko" in step
            assert "formula_applied" in step
            assert "intermediate_value" in step
            assert "weight" in step
            assert "weighted_value" in step
            assert "explanation_ko" in step
            assert "explanation_en" in step
