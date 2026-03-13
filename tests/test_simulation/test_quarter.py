"""Tests for quarter advancement and placement logic."""

import random

from talentgraph.data.seed import _id, create_sample_company
from talentgraph.simulation.quarter import (
    advance_quarter,
    place_person,
    _performance_bucket,
    _sample_outcome,
)
from talentgraph.simulation.state import QuarterLabel


class TestPerformanceBucket:
    def test_low_maps_to_1(self):
        assert _performance_bucket(1.0) == 1
        assert _performance_bucket(1.4) == 1

    def test_mid_maps_to_3(self):
        assert _performance_bucket(3.0) == 3

    def test_high_maps_to_5(self):
        assert _performance_bucket(4.6) == 5
        assert _performance_bucket(5.0) == 5

    def test_clamps_below(self):
        assert _performance_bucket(0.5) == 1

    def test_clamps_above(self):
        assert _performance_bucket(6.0) == 5


class TestSampleOutcome:
    def test_bucket_5_favors_high_ratings(self):
        rng = random.Random(42)
        ratings = [_sample_outcome(5, rng) for _ in range(100)]
        high = sum(1 for r in ratings if r.numeric >= 4)
        assert high > 50

    def test_bucket_1_favors_low_ratings(self):
        rng = random.Random(42)
        ratings = [_sample_outcome(1, rng) for _ in range(100)]
        low = sum(1 for r in ratings if r.numeric <= 2)
        assert low > 50

    def test_deterministic_with_seed(self):
        r1 = [_sample_outcome(3, random.Random(99)) for _ in range(10)]
        r2 = [_sample_outcome(3, random.Random(99)) for _ in range(10)]
        assert r1 == r2


class TestAdvanceQuarter:
    def test_generates_outcomes(self):
        company = create_sample_company()
        q = QuarterLabel(year=2025, quarter=1)
        updated, changes = advance_quarter(company, q, rng=random.Random(42))

        outcome_changes = [c for c in changes if c.change_type == "outcome"]
        assert len(outcome_changes) > 0

    def test_increments_tenure(self):
        company = create_sample_company()
        # Bob has an active assignment (end_date=None)
        bob = next(p for p in company.people if p.name == "Bob Park")
        old_tenure = bob.tenure_years

        q = QuarterLabel(year=2025, quarter=1)
        updated, _ = advance_quarter(company, q, rng=random.Random(42))

        bob_updated = next(p for p in updated.people if p.name == "Bob Park")
        assert bob_updated.tenure_years == old_tenure + 0.25

    def test_does_not_mutate_original(self):
        company = create_sample_company()
        alice_original_tenure = next(
            p for p in company.people if p.name == "Alice Chen"
        ).tenure_years

        q = QuarterLabel(year=2025, quarter=1)
        advance_quarter(company, q, rng=random.Random(42))

        alice_after = next(p for p in company.people if p.name == "Alice Chen")
        assert alice_after.tenure_years == alice_original_tenure

    def test_deterministic_with_same_seed(self):
        company = create_sample_company()
        q = QuarterLabel(year=2025, quarter=1)

        _, changes1 = advance_quarter(company, q, rng=random.Random(42))
        _, changes2 = advance_quarter(company, q, rng=random.Random(42))

        descs1 = [c.description for c in changes1 if c.change_type == "outcome"]
        descs2 = [c.description for c in changes2 if c.change_type == "outcome"]
        assert descs1 == descs2

    def test_multiple_quarters_accumulate_outcomes(self):
        company = create_sample_company()
        rng = random.Random(42)

        updated1, _ = advance_quarter(company, QuarterLabel(year=2025, quarter=1), rng=rng)
        updated2, _ = advance_quarter(updated1, QuarterLabel(year=2025, quarter=2), rng=rng)

        alice = next(p for p in updated2.people if p.name == "Alice Chen")
        active = [a for a in alice.assignments if a.end_date is None]
        for a in active:
            assert len(a.outcomes) == 2


class TestPlacePerson:
    def test_place_person_creates_assignment(self):
        company = create_sample_company()
        q = QuarterLabel(year=2025, quarter=1)

        bob_id = _id("person:bob")
        new_role_id = _id("role:sr_data_eng")
        new_dept_id = _id("dept:data_eng")

        updated, event = place_person(company, bob_id, new_role_id, new_dept_id, q)

        assert event.person_name == "Bob Park"
        assert event.role_title == "Senior Data Engineer"

        bob = next(p for p in updated.people if p.id == bob_id)
        active = [a for a in bob.assignments if a.end_date is None]
        assert len(active) == 1
        assert active[0].role_id == new_role_id

    def test_place_person_ends_old_assignment(self):
        company = create_sample_company()
        q = QuarterLabel(year=2025, quarter=1)

        bob_id = _id("person:bob")
        new_role_id = _id("role:sr_data_eng")
        new_dept_id = _id("dept:data_eng")

        updated, event = place_person(company, bob_id, new_role_id, new_dept_id, q)

        assert event.previous_role_title == "Engineering Manager"

        bob = next(p for p in updated.people if p.id == bob_id)
        ended = [a for a in bob.assignments if a.end_date is not None]
        assert len(ended) >= 1

    def test_place_nonexistent_person_raises(self):
        from uuid import uuid4
        import pytest

        company = create_sample_company()
        q = QuarterLabel(year=2025, quarter=1)

        with pytest.raises(ValueError, match="Person not found"):
            place_person(company, uuid4(), _id("role:eng_manager"), _id("dept:eng_mgmt"), q)
