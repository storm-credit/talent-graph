"""Tests for company_score module."""

import pytest

from talentgraph.game.company_score import CompanyScore, compute_company_score
from talentgraph.simulation.state import ChangeRecord
from talentgraph.data.seed import create_sample_company


class TestCompanyScore:
    """Tests for the CompanyScore model and compute function."""

    def test_company_score_model(self):
        score = CompanyScore(
            total=72.5,
            team_performance=80.0,
            morale_health=75.0,
            retention_rate=90.0,
            skill_coverage=60.0,
            growth_rate=50.0,
        )
        assert score.total == 72.5
        assert score.team_performance == 80.0

    def test_compute_score_with_sample_company(self, sample_company):
        score = compute_company_score(sample_company)
        assert 0 <= score.total <= 100
        assert 0 <= score.team_performance <= 100
        assert 0 <= score.morale_health <= 100
        assert 0 <= score.retention_rate <= 100
        assert 0 <= score.skill_coverage <= 100
        assert 0 <= score.growth_rate <= 100

    def test_empty_company_returns_zero(self):
        from talentgraph.ontology.models import Company
        from uuid import uuid4

        company = Company(id=uuid4(), name="Empty Corp")
        score = compute_company_score(company)
        assert score.total == 0.0

    def test_retention_rate_with_no_departures(self, sample_company):
        # Ensure no one is departed
        for p in sample_company.people:
            p.departed = False
        score = compute_company_score(sample_company)
        assert score.retention_rate == 100.0

    def test_retention_rate_with_departures(self, sample_company):
        # Mark someone as departed
        sample_company.people[0].departed = True
        score = compute_company_score(sample_company)
        assert score.retention_rate < 100.0

    def test_morale_health_all_happy(self, sample_company):
        for p in sample_company.people:
            p.morale = 0.8
            p.departed = False
        score = compute_company_score(sample_company)
        assert score.morale_health == 100.0

    def test_morale_health_all_low(self, sample_company):
        for p in sample_company.people:
            p.morale = 0.2
            p.departed = False
        score = compute_company_score(sample_company)
        assert score.morale_health == 0.0

    def test_growth_rate_with_growth_events(self, sample_company):
        from uuid import uuid4

        changes = [
            ChangeRecord(
                person_id=uuid4(),
                person_name="Test",
                change_type="skill_growth",
                description="skill grew",
            )
            for _ in range(3)
        ]
        score = compute_company_score(sample_company, changes)
        # 50 + 3*15 = 95, clamped to 100
        assert score.growth_rate == 95.0

    def test_growth_rate_with_decay_events(self, sample_company):
        from uuid import uuid4

        changes = [
            ChangeRecord(
                person_id=uuid4(),
                person_name="Test",
                change_type="skill_decay",
                description="skill decayed",
            )
            for _ in range(3)
        ]
        score = compute_company_score(sample_company, changes)
        # 50 - 3*15 = 5
        assert score.growth_rate == 5.0

    def test_score_total_is_weighted_sum(self, sample_company):
        for p in sample_company.people:
            p.departed = False
        score = compute_company_score(sample_company)
        expected = (
            0.30 * score.team_performance
            + 0.25 * score.morale_health
            + 0.20 * score.retention_rate
            + 0.15 * score.skill_coverage
            + 0.10 * score.growth_rate
        )
        assert abs(score.total - round(expected, 1)) < 0.2  # rounding tolerance

    def test_all_departed_returns_zero(self, sample_company):
        for p in sample_company.people:
            p.departed = True
        score = compute_company_score(sample_company)
        assert score.total == 0.0
