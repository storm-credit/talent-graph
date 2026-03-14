"""Tests for score breakdown step-by-step tracer."""

import pytest
from uuid import UUID

from talentgraph.data.seed import create_sample_company, _id
from talentgraph.explainer.definitions import ScoreBreakdown, ScoreStep
from talentgraph.explainer.score_breakdown import compute_score_breakdown
from talentgraph.scoring.engine import FitScoreEngine
from talentgraph.scoring.weights import ScoringWeights


@pytest.fixture
def company():
    return create_sample_company()


@pytest.fixture
def weights():
    return ScoringWeights()


def _first_role_id_and_dept(company):
    """Return (role_id, dept_id) for the first role in the first department."""
    dept = company.departments[0]
    role_id = dept.roles[0]  # dept.roles is list[UUID]
    return role_id, dept.id


class TestScoreBreakdown:
    """Tests for score breakdown computation."""

    def test_breakdown_returns_score_breakdown(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )
        assert isinstance(result, ScoreBreakdown)

    def test_breakdown_has_four_steps(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )
        assert len(result.steps) == 4

    def test_step_components_correct(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        components = [s.component for s in result.steps]
        assert components == [
            "skill_match",
            "historical_performance",
            "level_match",
            "burnout_risk",
        ]

    def test_step_numbers_sequential(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        for i, step in enumerate(result.steps):
            assert step.step_number == i + 1

    def test_weighted_values_sum_to_fit_score(self, company, weights):
        """The sum of weighted values should equal the final fit score (approximately)."""
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        weighted_sum = sum(s.weighted_value for s in result.steps)
        # Fit score is clamped to [0, 1], so sum may differ if clamped
        raw = max(0.0, min(1.0, weighted_sum))
        assert abs(result.final_fit_score - round(raw, 4)) < 0.001

    def test_fit_score_in_valid_range(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        assert 0.0 <= result.final_fit_score <= 1.0

    def test_predicted_performance_in_valid_range(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        assert 1.0 <= result.final_predicted_performance <= 5.0

    def test_breakdown_has_bilingual_explanations(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        for step in result.steps:
            assert step.explanation_ko, f"Step {step.step_number} missing Korean explanation"
            assert step.explanation_en, f"Step {step.step_number} missing English explanation"

        assert result.summary_ko
        assert result.summary_en

    def test_breakdown_has_formula_applied(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        for step in result.steps:
            assert step.formula_applied, f"Step {step.step_number} missing formula_applied"

    def test_person_not_found_raises(self, company, weights):
        fake_id = UUID("00000000-0000-0000-0000-000000000000")
        role_id, dept_id = _first_role_id_and_dept(company)

        with pytest.raises(ValueError, match="Person not found"):
            compute_score_breakdown(company, fake_id, role_id, dept_id, weights)

    def test_role_not_found_raises(self, company, weights):
        person = company.people[0]
        dept = company.departments[0]
        fake_id = UUID("00000000-0000-0000-0000-000000000000")

        with pytest.raises(ValueError, match="Role"):
            compute_score_breakdown(company, person.id, fake_id, dept.id, weights)

    def test_breakdown_matches_engine_score(self, company, weights):
        """Breakdown fit score should match FitScoreEngine result."""
        engine = FitScoreEngine(company, weights)

        for person in company.people:
            results = engine.evaluate_person(person.id)
            for fit in results:
                breakdown = compute_score_breakdown(
                    company,
                    person.id,
                    fit.role_id,
                    fit.department_id,
                    weights,
                )
                # Allow small float tolerance
                assert abs(breakdown.final_fit_score - fit.fit_score) < 0.02, (
                    f"{person.name} → {fit.role_title}: "
                    f"breakdown={breakdown.final_fit_score}, engine={fit.fit_score}"
                )

    def test_all_people_all_roles_no_crash(self, company, weights):
        """Ensure breakdown works for every person × role combination without error."""
        for person in company.people:
            for dept in company.departments:
                for role_id in dept.roles:  # dept.roles is list[UUID]
                    result = compute_score_breakdown(
                        company, person.id, role_id, dept.id, weights
                    )
                    assert isinstance(result, ScoreBreakdown)


class TestBreakdownComponents:
    """Tests for individual component tracing."""

    def test_skill_match_shows_skill_details(self, company, weights):
        """Skill match step should include per-skill breakdown."""
        person = company.people[0]  # Alice Chen
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        sm_step = result.steps[0]
        assert sm_step.component == "skill_match"
        assert "skill_details" in sm_step.inputs or "required_skills" in sm_step.inputs

    def test_historical_step_has_outcome_count(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        hp_step = result.steps[1]
        assert hp_step.component == "historical_performance"
        assert "outcome_count" in hp_step.inputs

    def test_burnout_step_has_tenure_info(self, company, weights):
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        br_step = result.steps[3]
        assert br_step.component == "burnout_risk"
        assert "years_in_role" in br_step.inputs or "has_assignments" in br_step.inputs

    def test_burnout_weighted_value_is_negative(self, company, weights):
        """Burnout is subtracted, so weighted_value should be <= 0."""
        person = company.people[0]
        role_id, dept_id = _first_role_id_and_dept(company)

        result = compute_score_breakdown(
            company, person.id, role_id, dept_id, weights
        )

        br_step = result.steps[3]
        assert br_step.weighted_value <= 0.0
