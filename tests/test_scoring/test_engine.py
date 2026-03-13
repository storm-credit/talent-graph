from talentgraph.scoring.engine import FitScoreEngine
from talentgraph.data.seed import _id


def test_alice_top1_is_data_engineering(sample_company):
    """Alice's best fit should be in Data Engineering."""
    engine = FitScoreEngine(sample_company)
    results = engine.evaluate_person(_id("person:alice"))
    top = engine.top_n(results, 3)

    assert len(top) == 3
    assert top[0].department_name == "Data Engineering"


def test_bob_top1_is_eng_management(sample_company):
    """Bob's best fit should be Engineering Management."""
    engine = FitScoreEngine(sample_company)
    results = engine.evaluate_person(_id("person:bob"))
    top = engine.top_n(results, 1)

    assert top[0].department_name == "Engineering Management"


def test_dave_has_high_burnout(sample_company):
    """Dave should show elevated burnout risk."""
    engine = FitScoreEngine(sample_company)
    results = engine.evaluate_person(_id("person:dave"))
    # All results for Dave should show the same burnout risk
    assert all(r.burnout_risk_score >= 0.3 for r in results)


def test_breakdown_sums_to_fit(sample_company):
    """Breakdown components should approximately sum to fit_score."""
    engine = FitScoreEngine(sample_company)
    results = engine.evaluate_person(_id("person:alice"))

    for r in results:
        breakdown_sum = sum(r.breakdown.values())
        # Due to clamping, fit_score may differ from raw sum
        assert abs(r.fit_score - max(0, min(1, breakdown_sum))) < 0.01


def test_predicted_performance_range(sample_company):
    """Predicted performance should be in [1.0, 5.0]."""
    engine = FitScoreEngine(sample_company)
    for person in sample_company.people:
        results = engine.evaluate_person(person.id)
        for r in results:
            assert 1.0 <= r.predicted_performance <= 5.0


def test_evaluate_by_name(sample_company):
    """evaluate_person_by_name should work with case-insensitive name."""
    engine = FitScoreEngine(sample_company)
    results = engine.evaluate_person_by_name("alice chen")
    assert len(results) > 0
    assert results[0].person_name == "Alice Chen"


def test_evaluate_nonexistent_person(sample_company):
    """Should raise ValueError for unknown person."""
    engine = FitScoreEngine(sample_company)
    import pytest

    with pytest.raises(ValueError, match="not found"):
        engine.evaluate_person_by_name("Nobody")
