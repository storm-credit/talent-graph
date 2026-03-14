"""Tests for skill growth/decay system (v0.3)."""

from __future__ import annotations

import random
from datetime import date
from uuid import UUID, uuid5

import pytest

from talentgraph.data.seed import NS, _id, create_sample_company
from talentgraph.ontology.enums import SkillLevel
from talentgraph.ontology.models import (
    Assignment,
    Company,
    Person,
    PersonSkill,
    Role,
    RoleSkillRequirement,
    Skill,
)
from talentgraph.simulation.growth import (
    DECAY_IDLE_THRESHOLD,
    DECAY_PROBABILITY_PER_QUARTER,
    GROWTH_PROBABILITY,
    _compute_growth_modifier,
    _get_effective_potential,
    _get_role_skill_ids,
    process_skill_growth,
)


@pytest.fixture()
def company():
    return create_sample_company()


class TestEffectivePotential:
    def test_returns_potential_when_set(self):
        ps = PersonSkill(
            skill_id=_id("skill:python"),
            level=SkillLevel.INTERMEDIATE,
            potential_level=SkillLevel.EXPERT,
        )
        assert _get_effective_potential(ps) == SkillLevel.EXPERT

    def test_returns_current_when_no_potential(self):
        ps = PersonSkill(
            skill_id=_id("skill:python"),
            level=SkillLevel.INTERMEDIATE,
        )
        assert _get_effective_potential(ps) == SkillLevel.INTERMEDIATE

    def test_at_ceiling_means_no_growth(self):
        ps = PersonSkill(
            skill_id=_id("skill:python"),
            level=SkillLevel.EXPERT,
            potential_level=SkillLevel.EXPERT,
        )
        gap = _get_effective_potential(ps).numeric - ps.level.numeric
        assert gap == 0
        assert GROWTH_PROBABILITY[0] == 0.0


class TestGrowthModifier:
    def test_high_morale_boosts_modifier(self):
        p = Person(
            id=_id("person:test"),
            name="High Morale",
            morale=0.9,
            learning_rate=1.0,
            tenure_years=2.0,
        )
        mod = _compute_growth_modifier(p)
        assert mod > 1.0

    def test_low_morale_no_extra_boost(self):
        p = Person(
            id=_id("person:test"),
            name="Low Morale",
            morale=0.3,
            learning_rate=1.0,
            tenure_years=2.0,
        )
        mod = _compute_growth_modifier(p)
        # morale < 0.5 → no boost (clamped to 0)
        assert mod == pytest.approx(1.0, abs=0.01)

    def test_high_learning_rate_scales(self):
        p = Person(
            id=_id("person:test"),
            name="Fast Learner",
            morale=0.5,
            learning_rate=2.0,
            tenure_years=2.0,
        )
        mod = _compute_growth_modifier(p)
        assert mod == pytest.approx(2.0, abs=0.01)

    def test_long_tenure_diminishes(self):
        p = Person(
            id=_id("person:test"),
            name="Veteran",
            morale=0.5,
            learning_rate=1.0,
            tenure_years=10.0,
        )
        mod = _compute_growth_modifier(p)
        # 10 years: tenure_mod = max(0.5, 1.0 - (10-5)*0.05) = 0.75
        assert mod < 1.0


class TestGetRoleSkillIds:
    def test_returns_skill_ids_for_active_role(self, company):
        bob = next(p for p in company.people if p.name == "Bob Park")
        role_lookup = {r.id: r for r in company.roles}
        skill_ids = _get_role_skill_ids(bob, role_lookup)
        assert len(skill_ids) > 0

    def test_returns_empty_for_no_assignment(self, company):
        alice = next(p for p in company.people if p.name == "Alice Chen")
        # Alice has ended assignment (end_date set)
        role_lookup = {r.id: r for r in company.roles}
        skill_ids = _get_role_skill_ids(alice, role_lookup)
        assert skill_ids == set()


class TestProcessSkillGrowth:
    def test_active_skills_can_grow(self, company):
        """Skills used in current role should have a chance to grow."""
        rng = random.Random(42)
        # Carol (Jr Data Scientist) has room to grow in Python, ML, Data Analysis
        carol = next(p for p in company.people if p.name == "Carol Kim")
        original_levels = {ps.skill_id: ps.level for ps in carol.skills}

        # Run many iterations to ensure growth happens
        for _ in range(20):
            process_skill_growth(company, rng)

        grew = any(
            ps.level.numeric > original_levels[ps.skill_id].numeric
            for ps in carol.skills
        )
        # With 20 iterations and high learning_rate=1.5, growth is very likely
        assert grew, "Expected at least one skill to grow after 20 quarters"

    def test_at_ceiling_no_growth(self, company):
        """Skills at potential_level should not grow."""
        rng = random.Random(42)
        dave = next(p for p in company.people if p.name == "Dave Lee")
        # Dave's Financial Modeling: Expert with PA=Expert
        fin_skill = next(
            ps for ps in dave.skills
            if ps.skill_id == _id("skill:finance")
        )
        assert fin_skill.level == SkillLevel.EXPERT
        assert fin_skill.potential_level == SkillLevel.EXPERT

        for _ in range(50):
            process_skill_growth(company, rng)

        assert fin_skill.level == SkillLevel.EXPERT

    def test_idle_skills_can_decay(self, company):
        """Skills not used and idle for 4+ quarters should have decay risk."""
        rng = random.Random(99)
        # Eve is Jr Data Engineer — role requires Python + SQL.
        # Machine Learning is NOT required → idle skill.
        eve = next(p for p in company.people if p.name == "Eve Wang")
        ml_skill = next(
            ps for ps in eve.skills
            if ps.skill_id == _id("skill:ml")
        )
        # Raise level so decay is possible (NOVICE can't decay)
        ml_skill.level = SkillLevel.INTERMEDIATE
        # Set idle quarters above threshold
        ml_skill.quarters_idle = DECAY_IDLE_THRESHOLD + 1

        original = ml_skill.level
        decayed = False
        for _ in range(100):
            changes = process_skill_growth(company, rng)
            if ml_skill.level.numeric < original.numeric:
                decayed = True
                break

        assert decayed, "Expected decay after prolonged idle"

    def test_departed_people_skipped(self, company):
        """Departed people should not have skill growth processed."""
        rng = random.Random(42)
        carol = next(p for p in company.people if p.name == "Carol Kim")
        carol.departed = True
        levels_before = {ps.skill_id: ps.level for ps in carol.skills}

        for _ in range(20):
            process_skill_growth(company, rng)

        for ps in carol.skills:
            assert ps.level == levels_before[ps.skill_id]

    def test_growth_returns_change_records(self, company):
        """Growth should produce ChangeRecord with skill_growth type."""
        rng = random.Random(42)
        all_changes = []
        for _ in range(20):
            changes = process_skill_growth(company, rng)
            all_changes.extend(changes)

        growth_changes = [c for c in all_changes if c.change_type == "skill_growth"]
        # With 20 iterations, expect at least some growth
        assert len(growth_changes) > 0

    def test_quarters_active_increments(self, company):
        """Active skills should have quarters_active incremented."""
        rng = random.Random(42)
        carol = next(p for p in company.people if p.name == "Carol Kim")
        py_skill = next(
            ps for ps in carol.skills
            if ps.skill_id == _id("skill:python")
        )
        initial = py_skill.quarters_active

        process_skill_growth(company, rng)

        # Python is required for Jr Data Scientist, so it's active
        assert py_skill.quarters_active == initial + 1
