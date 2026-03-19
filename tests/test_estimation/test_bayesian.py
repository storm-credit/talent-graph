"""Tests for the Bayesian skill estimation engine."""

import math

from talentgraph.estimation.bayesian import (
    bayesian_update,
    compute_confidence,
    compute_trend,
    observation_noise,
    outcome_to_signal,
    update_estimate,
)
from talentgraph.estimation.enums import (
    ProjectDifficulty,
    ProjectResult,
    ProjectRole,
    SkillTrend,
)
from talentgraph.estimation.models import EstimateSnapshot, SkillEstimate
from talentgraph.estimation.prior import SIGMA_INITIAL

from uuid import uuid4


class TestOutcomeToSignal:
    def test_failure_low_signal(self):
        signal = outcome_to_signal(ProjectResult.FAILURE, ProjectDifficulty.MODERATE)
        assert signal < 2.0

    def test_success_matches_difficulty(self):
        signal = outcome_to_signal(ProjectResult.SUCCESS, ProjectDifficulty.HARD)
        assert signal == 4.0

    def test_excellent_exceeds_difficulty(self):
        signal = outcome_to_signal(ProjectResult.EXCELLENT, ProjectDifficulty.HARD)
        assert signal > 4.0

    def test_signal_clamped_to_range(self):
        signal = outcome_to_signal(ProjectResult.EXCELLENT, ProjectDifficulty.EXTREME)
        assert 1.0 <= signal <= 5.0

    def test_failure_on_trivial(self):
        signal = outcome_to_signal(ProjectResult.FAILURE, ProjectDifficulty.TRIVIAL)
        assert signal == 1.0  # clamped to min


class TestObservationNoise:
    def test_lead_less_noisy_than_reviewer(self):
        lead_noise = observation_noise(ProjectDifficulty.MODERATE, ProjectRole.LEAD)
        reviewer_noise = observation_noise(ProjectDifficulty.MODERATE, ProjectRole.REVIEWER)
        assert lead_noise < reviewer_noise

    def test_hard_project_less_noisy(self):
        hard = observation_noise(ProjectDifficulty.HARD, ProjectRole.CONTRIBUTOR)
        easy = observation_noise(ProjectDifficulty.EASY, ProjectRole.CONTRIBUTOR)
        assert hard < easy


class TestBayesianUpdate:
    def test_moves_toward_observation(self):
        mu_post, sigma_post = bayesian_update(3.0, 1.5, 4.5, 0.8)
        assert mu_post > 3.0
        assert mu_post < 4.5

    def test_sigma_always_decreases(self):
        _, sigma_post = bayesian_update(3.0, 1.5, 4.0, 0.8)
        assert sigma_post < 1.5

    def test_precise_observation_dominates(self):
        # Very certain observation (low sigma) should pull mu strongly
        mu_post, _ = bayesian_update(3.0, 1.5, 5.0, 0.3)
        assert mu_post > 4.0

    def test_uncertain_observation_weak_effect(self):
        # Very uncertain observation (high sigma) should barely move mu
        mu_post, _ = bayesian_update(3.0, 1.5, 5.0, 5.0)
        assert mu_post < 3.5

    def test_result_clamped(self):
        mu_post, _ = bayesian_update(1.0, 0.3, 0.5, 0.3)
        assert mu_post >= 1.0
        mu_post2, _ = bayesian_update(5.0, 0.3, 6.0, 0.3)
        assert mu_post2 <= 5.0


class TestComputeTrend:
    def test_stable_with_no_history(self):
        assert compute_trend([]) == SkillTrend.STABLE

    def test_rising_trend(self):
        from datetime import datetime
        history = [
            EstimateSnapshot(mu=2.0 + i * 0.3, sigma=1.0, timestamp=datetime.now())
            for i in range(5)
        ]
        assert compute_trend(history) == SkillTrend.RISING

    def test_declining_trend(self):
        from datetime import datetime
        history = [
            EstimateSnapshot(mu=4.0 - i * 0.3, sigma=1.0, timestamp=datetime.now())
            for i in range(5)
        ]
        assert compute_trend(history) == SkillTrend.DECLINING

    def test_stable_flat(self):
        from datetime import datetime
        history = [
            EstimateSnapshot(mu=3.0, sigma=1.0, timestamp=datetime.now())
            for _ in range(5)
        ]
        assert compute_trend(history) == SkillTrend.STABLE


class TestComputeConfidence:
    def test_zero_at_initial(self):
        assert compute_confidence(SIGMA_INITIAL) == 0.0

    def test_high_when_sigma_low(self):
        c = compute_confidence(0.3)
        assert c > 0.7

    def test_clamped(self):
        assert compute_confidence(0.0) == 1.0
        assert compute_confidence(2.0) == 0.0


class TestUpdateEstimate:
    def test_updates_all_fields(self):
        est = SkillEstimate(person_id=uuid4(), skill_id=uuid4(), mu=3.0, sigma=1.5)
        updated = update_estimate(est, ProjectResult.SUCCESS, ProjectDifficulty.HARD, ProjectRole.LEAD)
        assert updated.mu != est.mu
        assert updated.sigma < est.sigma
        assert updated.update_count == 1
        assert len(updated.history) == 1
        assert updated.confidence > 0

    def test_multiple_updates_converge(self):
        est = SkillEstimate(person_id=uuid4(), skill_id=uuid4(), mu=3.0, sigma=1.5)
        # 5 successful hard projects should push toward Expert
        for _ in range(5):
            est = update_estimate(est, ProjectResult.SUCCESS, ProjectDifficulty.HARD, ProjectRole.LEAD)
        assert est.mu > 3.5
        assert est.sigma < 0.5
        assert est.confidence > 0.6

    def test_contradictory_evidence_keeps_high_sigma(self):
        est = SkillEstimate(person_id=uuid4(), skill_id=uuid4(), mu=3.0, sigma=1.5)
        # Alternating success and failure
        for i in range(6):
            result = ProjectResult.SUCCESS if i % 2 == 0 else ProjectResult.FAILURE
            est = update_estimate(est, result, ProjectDifficulty.MODERATE, ProjectRole.CONTRIBUTOR)
        # Sigma should still be moderate (not converging tightly)
        assert est.sigma > 0.3

    def test_newbie_grows_fast(self):
        """Simulates a new hire who performs well — skills should rise quickly."""
        est = SkillEstimate(person_id=uuid4(), skill_id=uuid4(), mu=2.0, sigma=1.5)
        for _ in range(3):
            est = update_estimate(est, ProjectResult.EXCELLENT, ProjectDifficulty.MODERATE, ProjectRole.CONTRIBUTOR)
        assert est.mu > 3.0  # Should have grown significantly
        assert est.trend == SkillTrend.RISING
