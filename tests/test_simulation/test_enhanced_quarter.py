"""Tests for enhanced quarter advancement (v0.3)."""

from __future__ import annotations

import random
from datetime import date

import pytest

from talentgraph.data.seed import _id, create_sample_company
from talentgraph.simulation.enhanced_quarter import advance_quarter_enhanced
from talentgraph.simulation.state import QuarterLabel


@pytest.fixture()
def company():
    return create_sample_company()


@pytest.fixture()
def quarter():
    return QuarterLabel(year=2025, quarter=1)


class TestEnhancedQuarterBasics:
    def test_returns_updated_company_and_changes(self, company, quarter):
        rng = random.Random(42)
        updated, changes = advance_quarter_enhanced(company, quarter, rng=rng)
        assert updated is not company
        assert len(changes) > 0

    def test_does_not_mutate_original(self, company, quarter):
        rng = random.Random(42)
        original_names = [p.name for p in company.people]
        advance_quarter_enhanced(company, quarter, rng=rng)
        assert [p.name for p in company.people] == original_names

    def test_generates_outcomes(self, company, quarter):
        rng = random.Random(42)
        _, changes = advance_quarter_enhanced(company, quarter, rng=rng)
        outcome_changes = [c for c in changes if c.change_type == "outcome"]
        # Bob, Carol, Dave, Eve have active assignments
        assert len(outcome_changes) >= 3

    def test_deterministic_with_same_seed(self, company, quarter):
        c1 = company.model_copy(deep=True)
        c2 = company.model_copy(deep=True)
        _, changes1 = advance_quarter_enhanced(c1, quarter, rng=random.Random(99))
        _, changes2 = advance_quarter_enhanced(c2, quarter, rng=random.Random(99))
        assert len(changes1) == len(changes2)
        for c1_r, c2_r in zip(changes1, changes2):
            assert c1_r.change_type == c2_r.change_type
            assert c1_r.person_name == c2_r.person_name


class TestFeatureFlags:
    def test_disable_growth(self, company, quarter):
        rng = random.Random(42)
        _, changes = advance_quarter_enhanced(
            company, quarter, rng=rng, enable_growth=False
        )
        growth_changes = [c for c in changes if c.change_type == "skill_growth"]
        assert len(growth_changes) == 0

    def test_disable_morale(self, company, quarter):
        rng = random.Random(42)
        _, changes = advance_quarter_enhanced(
            company, quarter, rng=rng, enable_morale=False
        )
        morale_changes = [c for c in changes if c.change_type == "morale_change"]
        assert len(morale_changes) == 0

    def test_disable_attrition(self, company, quarter):
        rng = random.Random(42)
        _, changes = advance_quarter_enhanced(
            company, quarter, rng=rng, enable_attrition=False
        )
        departure_changes = [c for c in changes if c.change_type == "departure"]
        assert len(departure_changes) == 0

    def test_disable_events(self, company, quarter):
        rng = random.Random(42)
        _, changes = advance_quarter_enhanced(
            company, quarter, rng=rng, enable_events=False
        )
        event_changes = [c for c in changes if c.change_type == "event"]
        assert len(event_changes) == 0

    def test_all_disabled_still_generates_outcomes(self, company, quarter):
        rng = random.Random(42)
        _, changes = advance_quarter_enhanced(
            company, quarter, rng=rng,
            enable_growth=False,
            enable_morale=False,
            enable_attrition=False,
            enable_events=False,
        )
        outcome_changes = [c for c in changes if c.change_type == "outcome"]
        assert len(outcome_changes) >= 3


class TestMoraleAffectsOutcomes:
    def test_high_morale_better_outcomes(self, company, quarter):
        """High morale should shift outcomes slightly higher."""
        # Run many simulations and compare average ratings
        high_ratings = []
        low_ratings = []

        for seed in range(50):
            c_high = company.model_copy(deep=True)
            c_low = company.model_copy(deep=True)

            for p in c_high.people:
                p.morale = 0.95
            for p in c_low.people:
                p.morale = 0.15

            _, ch_high = advance_quarter_enhanced(
                c_high, quarter, rng=random.Random(seed),
                enable_growth=False, enable_morale=False,
                enable_attrition=False, enable_events=False,
            )
            _, ch_low = advance_quarter_enhanced(
                c_low, quarter, rng=random.Random(seed),
                enable_growth=False, enable_morale=False,
                enable_attrition=False, enable_events=False,
            )

            for c in ch_high:
                if c.change_type == "outcome" and hasattr(c, "rating"):
                    high_ratings.append(c.rating.numeric)
            for c in ch_low:
                if c.change_type == "outcome" and hasattr(c, "rating"):
                    low_ratings.append(c.rating.numeric)

        if high_ratings and low_ratings:
            avg_high = sum(high_ratings) / len(high_ratings)
            avg_low = sum(low_ratings) / len(low_ratings)
            # High morale should produce better average outcomes
            assert avg_high >= avg_low


class TestTenureIncrements:
    def test_tenure_increments(self, company, quarter):
        rng = random.Random(42)
        bob = next(p for p in company.people if p.name == "Bob Park")
        old_tenure = bob.tenure_years

        updated, _ = advance_quarter_enhanced(company, quarter, rng=rng)
        new_bob = next(p for p in updated.people if p.name == "Bob Park")

        if not new_bob.departed:
            assert new_bob.tenure_years == old_tenure + 0.25


class TestMultipleQuarters:
    def test_multiple_quarters_accumulate_changes(self, company, quarter):
        """Running multiple quarters should accumulate outcomes and changes."""
        rng = random.Random(42)
        c = company.model_copy(deep=True)
        all_changes = []

        for i in range(4):
            q = QuarterLabel(year=2025, quarter=i + 1)
            c, changes = advance_quarter_enhanced(c, q, rng=rng)
            all_changes.extend(changes)

        assert len(all_changes) > 0
        # Should have outcomes for each quarter
        outcome_changes = [c for c in all_changes if c.change_type == "outcome"]
        assert len(outcome_changes) >= 4  # At least 1 per quarter
