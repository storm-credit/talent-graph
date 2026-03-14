"""Tests for recommendation engine."""

from __future__ import annotations

import pytest

from talentgraph.data.seed import create_sample_company
from talentgraph.recommendation.engine import (
    PlacementCell,
    Recommendation,
    RecommendationEngine,
    SkillGap,
)


@pytest.fixture
def company():
    return create_sample_company()


@pytest.fixture
def engine(company):
    return RecommendationEngine(company)


class TestBestRolesForPerson:
    """Test best_roles_for_person recommendations."""

    def test_returns_recommendations(self, engine, company):
        person = company.people[0]
        recs = engine.best_roles_for_person(person.id)
        assert len(recs) > 0
        assert all(isinstance(r, Recommendation) for r in recs)

    def test_sorted_by_fit_score(self, engine, company):
        person = company.people[0]
        recs = engine.best_roles_for_person(person.id, top_n=10)
        scores = [r.fit_score for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_top_n_limits_results(self, engine, company):
        person = company.people[0]
        recs = engine.best_roles_for_person(person.id, top_n=2)
        assert len(recs) <= 2

    def test_recommendation_has_strengths(self, engine, company):
        person = company.people[0]
        recs = engine.best_roles_for_person(person.id)
        # At least one rec should have strengths
        has_strengths = any(len(r.strengths) > 0 for r in recs)
        assert has_strengths

    def test_recommendation_has_bilingual_text(self, engine, company):
        person = company.people[0]
        recs = engine.best_roles_for_person(person.id)
        for rec in recs:
            assert rec.recommendation_en
            assert rec.recommendation_ko

    def test_nonexistent_person_returns_empty(self, engine):
        from uuid import uuid4
        recs = engine.best_roles_for_person(uuid4())
        assert recs == []

    def test_all_people_get_recommendations(self, engine, company):
        for person in company.people:
            if not person.departed:
                recs = engine.best_roles_for_person(person.id)
                assert len(recs) > 0, f"{person.name} got no recommendations"


class TestBestCandidatesForRole:
    """Test best_candidates_for_role recommendations."""

    def test_returns_candidates(self, engine, company):
        dept = company.departments[0]
        role_id = dept.roles[0]
        recs = engine.best_candidates_for_role(role_id, dept.id)
        assert len(recs) > 0

    def test_sorted_by_fit_score(self, engine, company):
        dept = company.departments[0]
        role_id = dept.roles[0]
        recs = engine.best_candidates_for_role(role_id, dept.id, top_n=10)
        scores = [r.fit_score for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_excludes_departed(self, engine, company):
        # Mark someone as departed
        company.people[0].departed = True
        engine2 = RecommendationEngine(company)
        dept = company.departments[0]
        role_id = dept.roles[0]
        recs = engine2.best_candidates_for_role(role_id, dept.id, top_n=10)
        person_ids = {r.person_id for r in recs}
        assert company.people[0].id not in person_ids

    def test_top_n_limits_results(self, engine, company):
        dept = company.departments[0]
        role_id = dept.roles[0]
        recs = engine.best_candidates_for_role(role_id, dept.id, top_n=2)
        assert len(recs) <= 2


class TestPlacementMatrix:
    """Test placement matrix generation."""

    def test_returns_cells(self, engine):
        cells = engine.placement_matrix()
        assert len(cells) > 0
        assert all(isinstance(c, PlacementCell) for c in cells)

    def test_cells_have_valid_scores(self, engine):
        cells = engine.placement_matrix()
        for cell in cells:
            assert 0.0 <= cell.fit_score <= 1.0 or cell.fit_score < 0  # can be negative with burnout

    def test_covers_all_active_people(self, engine, company):
        cells = engine.placement_matrix()
        active_ids = {p.id for p in company.people if not p.departed}
        matrix_person_ids = {c.person_id for c in cells}
        assert active_ids == matrix_person_ids

    def test_excludes_departed(self, engine, company):
        company.people[0].departed = True
        engine2 = RecommendationEngine(company)
        cells = engine2.placement_matrix()
        person_ids = {c.person_id for c in cells}
        assert company.people[0].id not in person_ids


class TestSkillAnalysis:
    """Test strength/gap analysis."""

    def test_gaps_have_valid_structure(self, engine, company):
        person = company.people[0]
        recs = engine.best_roles_for_person(person.id)
        for rec in recs:
            for gap in rec.gaps:
                assert isinstance(gap, SkillGap)
                assert gap.skill_name
                assert gap.gap > 0

    def test_growth_potential_valid_values(self, engine, company):
        for person in company.people:
            if not person.departed:
                recs = engine.best_roles_for_person(person.id)
                for rec in recs:
                    assert rec.growth_potential in ("high", "medium", "low")
