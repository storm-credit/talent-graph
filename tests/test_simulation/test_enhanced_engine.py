"""Tests for SimulationEngine enhanced mode (v0.3)."""

from __future__ import annotations

import random

import pytest

from talentgraph.data.seed import create_sample_company
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures
from talentgraph.simulation.state import QuarterLabel


@pytest.fixture()
def company():
    return create_sample_company()


class TestSimulationFeatures:
    def test_default_features_basic_mode(self):
        f = SimulationFeatures()
        assert f.enhanced is False
        assert f.growth is True
        assert f.morale is True

    def test_enhanced_mode(self):
        f = SimulationFeatures(enhanced=True)
        assert f.enhanced is True


class TestEnhancedEngine:
    def test_basic_mode_works(self, company):
        """Default (basic) mode should still work."""
        engine = SimulationEngine(company, seed=42)
        quarter, changes = engine.advance()
        assert str(quarter) == "2025-Q1"
        assert len(changes) > 0

    def test_enhanced_mode_advance(self, company):
        """Enhanced mode should produce more change types."""
        features = SimulationFeatures(enhanced=True)
        engine = SimulationEngine(company, seed=42, features=features)
        quarter, changes = engine.advance()
        assert str(quarter) == "2025-Q1"
        assert len(changes) > 0

        change_types = {c.change_type for c in changes}
        # Should have outcomes at minimum
        assert "outcome" in change_types

    def test_enhanced_more_changes_than_basic(self, company):
        """Enhanced mode should generally produce more changes."""
        basic_engine = SimulationEngine(company.model_copy(deep=True), seed=42)
        _, basic_changes = basic_engine.advance()

        enhanced_engine = SimulationEngine(
            company.model_copy(deep=True),
            seed=42,
            features=SimulationFeatures(enhanced=True),
        )
        _, enhanced_changes = enhanced_engine.advance()

        # Enhanced should have more change types (morale, growth, etc.)
        basic_types = {c.change_type for c in basic_changes}
        enhanced_types = {c.change_type for c in enhanced_changes}
        assert len(enhanced_types) >= len(basic_types)

    def test_features_property(self, company):
        engine = SimulationEngine(company, seed=42)
        assert engine.features.enhanced is False

        engine.features = SimulationFeatures(enhanced=True)
        assert engine.features.enhanced is True

    def test_multiple_quarters_enhanced(self, company):
        """Multiple enhanced quarters should accumulate changes."""
        features = SimulationFeatures(enhanced=True)
        engine = SimulationEngine(company, seed=42, features=features)

        all_changes = []
        for _ in range(4):
            _, changes = engine.advance()
            all_changes.extend(changes)

        assert len(all_changes) > 0
        assert len(engine.history) == 4

    def test_rollback_works_in_enhanced(self, company):
        features = SimulationFeatures(enhanced=True)
        engine = SimulationEngine(company, seed=42, features=features)

        engine.advance()
        engine.advance()
        assert len(engine.history) == 2

        engine.rollback(1)
        assert len(engine.history) == 1
        assert str(engine.current_quarter) == "2025-Q2"

    def test_reset_works_in_enhanced(self, company):
        features = SimulationFeatures(enhanced=True)
        engine = SimulationEngine(company, seed=42, features=features)

        engine.advance()
        engine.advance()
        engine.reset()

        assert len(engine.history) == 0
        assert str(engine.current_quarter) == "2025-Q1"

    def test_selective_feature_flags(self, company):
        """Can disable specific features while keeping enhanced mode."""
        features = SimulationFeatures(
            enhanced=True,
            growth=False,
            events=False,
        )
        engine = SimulationEngine(company, seed=42, features=features)
        _, changes = engine.advance()

        change_types = {c.change_type for c in changes}
        assert "skill_growth" not in change_types
        assert "event" not in change_types


class TestConvenienceMethods:
    def test_get_active_people(self, company):
        engine = SimulationEngine(company, seed=42)
        active = engine.get_active_people()
        assert len(active) == 5  # All 5 people active

    def test_get_departed_people(self, company):
        engine = SimulationEngine(company, seed=42)
        departed = engine.get_departed_people()
        assert len(departed) == 0

    def test_get_person(self, company):
        from talentgraph.data.seed import _id

        engine = SimulationEngine(company, seed=42)
        bob = engine.get_person(_id("person:bob"))
        assert bob is not None
        assert bob.name == "Bob Park"

    def test_get_person_not_found(self, company):
        from uuid import uuid4

        engine = SimulationEngine(company, seed=42)
        assert engine.get_person(uuid4()) is None

    def test_get_stats(self, company):
        engine = SimulationEngine(company, seed=42)
        stats = engine.get_stats()

        assert stats["total_people"] == 5
        assert stats["active_people"] == 5
        assert stats["departed_people"] == 0
        assert stats["quarters_simulated"] == 0
        assert stats["current_quarter"] == "2025-Q1"
        assert stats["enhanced_mode"] is False
        assert 0.0 <= stats["average_morale"] <= 1.0

    def test_get_stats_after_advance(self, company):
        engine = SimulationEngine(company, seed=42)
        engine.advance()
        stats = engine.get_stats()
        assert stats["quarters_simulated"] == 1
        assert stats["current_quarter"] == "2025-Q2"
