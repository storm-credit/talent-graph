"""Tests for company profile API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from talentgraph.api.app import app
from talentgraph.api import deps
from talentgraph.company.profile import IndustryType


@pytest.fixture
def client():
    deps._engine = None
    return TestClient(app)


class TestTemplateAPI:
    """Test template listing and detail endpoints."""

    def test_list_templates(self, client):
        resp = client.get("/api/company-profile/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == len(IndustryType)

    def test_list_templates_has_required_fields(self, client):
        resp = client.get("/api/company-profile/templates")
        for item in resp.json():
            assert "industry" in item
            assert "name_en" in item
            assert "name_ko" in item
            assert "description_en" in item
            assert "skills" in item

    def test_get_template_detail(self, client):
        resp = client.get("/api/company-profile/templates/tech_startup")
        assert resp.status_code == 200
        data = resp.json()
        assert data["industry"] == "tech_startup"
        assert len(data["skills"]) >= 5
        assert len(data["roles"]) >= 3
        assert len(data["departments"]) >= 2

    def test_get_template_404(self, client):
        resp = client.get("/api/company-profile/templates/nonexistent")
        assert resp.status_code == 404

    def test_each_industry_detail_accessible(self, client):
        for ind in IndustryType:
            resp = client.get(f"/api/company-profile/templates/{ind.value}")
            assert resp.status_code == 200, f"Failed for {ind.value}"


class TestCreateCompanyAPI:
    """Test company creation endpoint."""

    def test_create_company(self, client):
        resp = client.post(
            "/api/company-profile/create",
            json={
                "industry": "tech_startup",
                "name": "NewCo",
                "num_people": 8,
                "growth_stage": "growth",
                "culture_type": "adhocracy",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "NewCo"
        assert data["people_count"] == 8
        assert data["industry"] == "tech_startup"

    def test_create_company_resets_engine(self, client):
        # First check current status
        status1 = client.get("/api/simulation/status").json()

        # Create new company
        client.post(
            "/api/company-profile/create",
            json={
                "industry": "consulting",
                "name": "ConsultCo",
                "num_people": 5,
            },
        )

        # Status should reflect new company
        status2 = client.get("/api/simulation/status").json()
        assert status2["people_count"] == 5

    def test_created_company_is_simulatable(self, client):
        client.post(
            "/api/company-profile/create",
            json={
                "industry": "finance",
                "name": "FinanceCo",
                "num_people": 10,
            },
        )

        # Advance should work
        resp = client.post("/api/simulation/advance")
        assert resp.status_code == 200
