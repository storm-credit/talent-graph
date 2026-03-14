"""Tests for recommendation API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from talentgraph.api.app import app
from talentgraph.api import deps
from talentgraph.data.seed import create_sample_company


@pytest.fixture
def client():
    deps._engine = None
    return TestClient(app)


@pytest.fixture
def company():
    return create_sample_company()


class TestRecommendationAPI:
    """Test recommendation endpoints."""

    def test_person_recommendations(self, client, company):
        person = company.people[0]
        resp = client.get(f"/api/recommendations/person/{person.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert "fit_score" in data[0]
        assert "strengths" in data[0]
        assert "gaps" in data[0]
        assert "recommendation_en" in data[0]
        assert "recommendation_ko" in data[0]

    def test_role_recommendations(self, client, company):
        dept = company.departments[0]
        role_id = dept.roles[0]
        resp = client.get(f"/api/recommendations/role/{role_id}/{dept.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0

    def test_placement_matrix(self, client):
        resp = client.get("/api/recommendations/matrix")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert "person_name" in data[0]
        assert "role_title" in data[0]
        assert "fit_score" in data[0]

    def test_top_n_parameter(self, client, company):
        person = company.people[0]
        resp = client.get(f"/api/recommendations/person/{person.id}?top_n=1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) <= 1
