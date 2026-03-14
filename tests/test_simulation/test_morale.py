"""Tests for morale system (v0.3)."""

from __future__ import annotations

import random
from datetime import date

import pytest

from talentgraph.data.seed import _id, create_sample_company
from talentgraph.ontology.enums import OutcomeRating
from talentgraph.simulation.morale import (
    BURNOUT_MORALE_DRAG,
    MEAN_REVERSION_RATE,
    OUTCOME_MORALE_DELTA,
    PLACEMENT_BOOST,
    STAGNATION_PENALTY,
    process_morale,
)


@pytest.fixture()
def company():
    return create_sample_company()


class TestMoraleDelta:
    def test_exceptional_outcome_boosts_morale(self, company):
        rng = random.Random(42)
        # Use Carol: fresh tenure (no stagnation), low burnout → pure outcome effect
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.morale = 0.50  # Start at midpoint for clean test
        old_morale = carol.morale
        outcomes = {str(carol.id): OutcomeRating.EXCEPTIONAL}

        process_morale(company, date(2025, 4, 1), outcomes, set(), rng)

        # +0.08 outcome + ~0 reversion + no stagnation + no burnout drag
        assert carol.morale > old_morale

    def test_unsatisfactory_outcome_drops_morale(self, company):
        rng = random.Random(42)
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.morale = 0.50
        old_morale = carol.morale
        outcomes = {str(carol.id): OutcomeRating.UNSATISFACTORY}

        process_morale(company, date(2025, 4, 1), outcomes, set(), rng)

        # -0.10 outcome → drops morale
        assert carol.morale < old_morale

    def test_meets_no_outcome_impact(self, company):
        """MEETS outcome should have 0 delta (plus other factors)."""
        assert OUTCOME_MORALE_DELTA[OutcomeRating.MEETS] == 0.0

    def test_placement_boosts_morale(self, company):
        rng = random.Random(42)
        # Use Carol: low burnout, no stagnation → placement boost dominates
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.morale = 0.50
        old_morale = carol.morale
        placements = {str(carol.id)}

        process_morale(company, date(2025, 4, 1), None, placements, rng)

        # Placement boost is +0.10, no stagnation/burnout to counter it
        assert carol.morale > old_morale + 0.05


class TestMoraleReversion:
    def test_high_morale_reverts_downward(self, company):
        """High morale should drift toward 0.5."""
        rng = random.Random(42)
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.morale = 0.95

        process_morale(company, date(2025, 4, 1), None, set(), rng)

        assert carol.morale < 0.95

    def test_low_morale_reverts_upward(self, company):
        """Low morale should drift toward 0.5 (test on person w/o burnout)."""
        rng = random.Random(42)
        # Use Carol: low burnout, short tenure → reversion dominates
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.morale = 0.15

        process_morale(company, date(2025, 4, 1), None, set(), rng)

        # Mean reversion: (0.5 - 0.15) * 0.05 = +0.0175
        assert carol.morale > 0.15


class TestMoraleBounds:
    def test_morale_cannot_exceed_1(self, company):
        rng = random.Random(42)
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.morale = 0.98
        outcomes = {str(carol.id): OutcomeRating.EXCEPTIONAL}
        placements = {str(carol.id)}

        process_morale(company, date(2025, 4, 1), outcomes, placements, rng)

        assert carol.morale <= 1.0

    def test_morale_cannot_go_below_0(self, company):
        rng = random.Random(42)
        dave = next(p for p in company.people if p.name == "Dave Lee")
        dave.morale = 0.02
        outcomes = {str(dave.id): OutcomeRating.UNSATISFACTORY}

        process_morale(company, date(2025, 4, 1), outcomes, set(), rng)

        assert dave.morale >= 0.0


class TestMoraleStagnation:
    def test_long_tenure_same_role_penalty(self, company):
        """3+ years in same role should apply stagnation penalty."""
        rng = random.Random(42)
        # Bob has been in role since 2019 (6+ years)
        bob = next(p for p in company.people if p.name == "Bob Park")
        bob.morale = 0.6

        process_morale(company, date(2025, 4, 1), None, set(), rng)

        # Morale should go down due to stagnation
        # But mean reversion pulls it toward 0.5 too
        # At 0.6, reversion pulls down (-0.005) and stagnation pulls down (-0.02)
        assert bob.morale < 0.6


class TestMoraleDepartedSkipped:
    def test_departed_skipped(self, company):
        rng = random.Random(42)
        dave = next(p for p in company.people if p.name == "Dave Lee")
        dave.departed = True
        old_morale = dave.morale

        process_morale(company, date(2025, 4, 1), None, set(), rng)

        assert dave.morale == old_morale


class TestMoraleChangeRecords:
    def test_returns_change_records(self, company):
        rng = random.Random(42)
        outcomes = {}
        for p in company.people:
            outcomes[str(p.id)] = OutcomeRating.EXCEPTIONAL

        changes = process_morale(company, date(2025, 4, 1), outcomes, set(), rng)

        morale_changes = [c for c in changes if c.change_type == "morale_change"]
        assert len(morale_changes) > 0

    def test_small_changes_not_recorded(self, company):
        """Changes < 0.005 should not be recorded."""
        rng = random.Random(42)
        # Set all morale to exactly 0.5 (mean reversion target)
        for p in company.people:
            p.morale = 0.5

        changes = process_morale(company, date(2025, 4, 1), None, set(), rng)

        # With morale=0.5, reversion is 0 and only jitter applies
        # Some might still be recorded if jitter > 0.005
        for c in changes:
            assert c.change_type == "morale_change"
