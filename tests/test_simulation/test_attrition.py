"""Tests for attrition model (v0.3)."""

from __future__ import annotations

import random
from datetime import date

import pytest

from talentgraph.data.seed import _id, create_sample_company
from talentgraph.simulation.attrition import (
    BASE_ATTRITION_RATE,
    BURNOUT_FACTOR,
    MAX_QUARTERLY_ATTRITION,
    MORALE_FACTOR,
    _tenure_multiplier,
    compute_attrition_probability,
    process_attrition,
)


@pytest.fixture()
def company():
    return create_sample_company()


class TestTenureMultiplier:
    def test_new_hire_higher_risk(self):
        assert _tenure_multiplier(0.5) == 1.5

    def test_stable_tenure(self):
        assert _tenure_multiplier(3.0) == 1.0

    def test_mid_range_stable(self):
        assert _tenure_multiplier(5.0) == 1.0

    def test_long_tenure_ramps(self):
        m = _tenure_multiplier(7.0)
        assert 1.0 < m < 1.5

    def test_very_long_tenure_high_risk(self):
        assert _tenure_multiplier(10.0) == 1.5


class TestAttritionProbability:
    def test_healthy_person_low_risk(self, company):
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.morale = 0.8
        prob = compute_attrition_probability(carol, date(2025, 4, 1))
        # High morale, short tenure → mostly base rate with new-hire multiplier
        assert prob < 0.05

    def test_burnout_increases_risk(self, company):
        dave = next(p for p in company.people if p.name == "Dave Lee")
        dave.morale = 0.3  # Low morale
        prob = compute_attrition_probability(dave, date(2025, 4, 1))
        # Dave: long tenure + low morale + high burnout
        assert prob > BASE_ATTRITION_RATE

    def test_departed_returns_zero(self, company):
        dave = next(p for p in company.people if p.name == "Dave Lee")
        dave.departed = True
        prob = compute_attrition_probability(dave, date(2025, 4, 1))
        assert prob == 0.0

    def test_max_cap(self, company):
        """Probability should never exceed MAX_QUARTERLY_ATTRITION."""
        dave = next(p for p in company.people if p.name == "Dave Lee")
        dave.morale = 0.0  # Worst case
        prob = compute_attrition_probability(dave, date(2025, 4, 1))
        assert prob <= MAX_QUARTERLY_ATTRITION

    def test_low_morale_adds_risk(self, company):
        carol = next(p for p in company.people if p.name == "Carol Kim")
        prob_high = compute_attrition_probability(carol, date(2025, 4, 1))
        carol.morale = 0.2
        prob_low = compute_attrition_probability(carol, date(2025, 4, 1))
        assert prob_low > prob_high


class TestProcessAttrition:
    def test_some_departures_with_bad_conditions(self, company):
        """With very low morale, departures should happen over many trials."""
        rng = random.Random(42)
        for p in company.people:
            p.morale = 0.1  # Very low morale → high attrition risk

        departures = 0
        for _ in range(50):
            c = company.model_copy(deep=True)
            changes = process_attrition(c, date(2025, 4, 1), rng)
            departures += len([ch for ch in changes if ch.change_type == "departure"])

        assert departures > 0

    def test_departed_person_marked(self, company):
        """Departed person should have departed=True and end_date set."""
        rng = random.Random(42)
        for p in company.people:
            p.morale = 0.05  # Force high attrition

        found_departure = False
        for _ in range(100):
            c = company.model_copy(deep=True)
            changes = process_attrition(c, date(2025, 4, 1), rng)
            for ch in changes:
                if ch.change_type == "departure":
                    found_departure = True
                    person = next(p for p in c.people if p.id == ch.person_id)
                    assert person.departed is True
                    for a in person.assignments:
                        if a.end_date is not None:
                            assert a.end_date == date(2025, 4, 1)
                    break
            if found_departure:
                break

        assert found_departure

    def test_already_departed_not_processed(self, company):
        """Already-departed people should not be processed again."""
        rng = random.Random(42)
        for p in company.people:
            p.departed = True

        changes = process_attrition(company, date(2025, 4, 1), rng)
        assert len(changes) == 0

    def test_change_records_have_correct_type(self, company):
        """Departure change records should have type 'departure'."""
        rng = random.Random(42)
        for p in company.people:
            p.morale = 0.05

        for _ in range(100):
            c = company.model_copy(deep=True)
            changes = process_attrition(c, date(2025, 4, 1), rng)
            for ch in changes:
                assert ch.change_type == "departure"
                assert "departed" in ch.description
            if changes:
                break
