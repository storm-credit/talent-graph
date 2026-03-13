"""Tests for SimulationEngine orchestrator."""

import pytest

from talentgraph.data.seed import _id, create_sample_company
from talentgraph.simulation.engine import SimulationEngine
from talentgraph.simulation.state import QuarterLabel


@pytest.fixture
def sim():
    return SimulationEngine(create_sample_company(), seed=42)


class TestSimulationAdvance:
    def test_advance_returns_quarter_and_changes(self, sim):
        quarter, changes = sim.advance()
        assert str(quarter) == "2025-Q1"
        assert len(changes) > 0

    def test_advance_increments_quarter(self, sim):
        sim.advance()
        assert str(sim.current_quarter) == "2025-Q2"
        sim.advance()
        assert str(sim.current_quarter) == "2025-Q3"

    def test_advance_builds_history(self, sim):
        sim.advance()
        sim.advance()
        assert len(sim.history) == 2

    def test_advance_4_quarters_wraps_year(self, sim):
        for _ in range(4):
            sim.advance()
        assert str(sim.current_quarter) == "2026-Q1"


class TestSimulationPlacement:
    def test_place_person(self, sim):
        event = sim.place(
            _id("person:bob"),
            _id("role:sr_data_eng"),
            _id("dept:data_eng"),
        )
        assert event.person_name == "Bob Park"
        assert event.role_title == "Senior Data Engineer"

    def test_preview_placement(self, sim):
        result = sim.preview_placement(
            _id("person:alice"),
            _id("role:eng_manager"),
            _id("dept:eng_mgmt"),
        )
        assert result.role_title == "Engineering Manager"
        assert 0 <= result.fit_score <= 1


class TestSimulationRollback:
    def test_rollback_one_step(self, sim):
        sim.advance()
        sim.advance()
        q = sim.rollback(1)
        assert str(q) == "2025-Q2"
        assert len(sim.history) == 1

    def test_rollback_restores_company(self, sim):
        alice_tenure_before = next(
            p for p in sim.company.people if p.name == "Alice Chen"
        ).tenure_years

        sim.advance()
        sim.rollback(1)

        alice_tenure_after = next(
            p for p in sim.company.people if p.name == "Alice Chen"
        ).tenure_years
        assert alice_tenure_after == alice_tenure_before

    def test_rollback_too_many_raises(self, sim):
        sim.advance()
        with pytest.raises(ValueError, match="Cannot rollback"):
            sim.rollback(5)

    def test_rollback_zero_raises(self, sim):
        with pytest.raises(ValueError):
            sim.rollback(0)


class TestSimulationReset:
    def test_reset_clears_history(self, sim):
        sim.advance()
        sim.advance()
        sim.reset()
        assert len(sim.history) == 0
        assert str(sim.current_quarter) == "2025-Q1"

    def test_reset_restores_initial_company(self, sim):
        original_names = sorted(p.name for p in sim.company.people)
        sim.advance()
        sim.advance()
        sim.reset()
        reset_names = sorted(p.name for p in sim.company.people)
        assert original_names == reset_names


class TestQuarterLabel:
    def test_str_format(self):
        q = QuarterLabel(year=2025, quarter=3)
        assert str(q) == "2025-Q3"

    def test_next_wraps(self):
        q = QuarterLabel(year=2025, quarter=4)
        n = q.next()
        assert n.year == 2026
        assert n.quarter == 1

    def test_next_increments(self):
        q = QuarterLabel(year=2025, quarter=2)
        n = q.next()
        assert n.year == 2025
        assert n.quarter == 3
