"""Tests for enhanced scoring engine (v0.3)."""

from __future__ import annotations

import math
from datetime import date
from uuid import UUID

import pytest

from talentgraph.data.seed import _id, create_sample_company
from talentgraph.ontology.enums import SkillLevel, TraitType
from talentgraph.ontology.models import Person, PersonSkill, Role, RoleSkillRequirement, Trait
from talentgraph.scoring.enhanced import (
    EnhancedWeights,
    check_critical_skills,
    check_headcount,
    compute_asymmetric_level_match,
    compute_culture_fit,
    compute_enhanced_history,
    compute_role_similarity,
    compute_smooth_burnout_staleness,
    compute_team_chemistry,
    normalize_weights,
)


@pytest.fixture()
def company():
    return create_sample_company()


class TestSmoothBurnoutStaleness:
    def test_fresh_assignment_low_staleness(self, company):
        carol = next(p for p in company.people if p.name == "Carol Kim")
        ref = date(2025, 4, 1)
        staleness = compute_smooth_burnout_staleness(carol, ref)
        # Carol started 2024-06-01, ~10 months → low staleness
        assert staleness < 0.3

    def test_old_assignment_high_staleness(self, company):
        dave = next(p for p in company.people if p.name == "Dave Lee")
        ref = date(2025, 4, 1)
        staleness = compute_smooth_burnout_staleness(dave, ref)
        # Dave started 2019-01-10, 6+ years → high staleness
        assert staleness > 0.7

    def test_sigmoid_shape(self, company):
        """3 years should be ~0.5 (center of sigmoid)."""
        bob = next(p for p in company.people if p.name == "Bob Park")
        # Bob started 2019-03-01; let's check at exactly 3 years
        ref = date(2022, 3, 1)
        staleness = compute_smooth_burnout_staleness(bob, ref)
        assert 0.3 < staleness < 0.7  # roughly centered

    def test_no_assignments_returns_low(self):
        p = Person(id=_id("person:empty"), name="No Assignments")
        staleness = compute_smooth_burnout_staleness(p, date(2025, 4, 1))
        assert staleness == pytest.approx(0.1)


class TestAsymmetricLevelMatch:
    def test_same_level_perfect_match(self, company):
        roles = {r.id: r for r in company.roles}
        # Find a person/role at similar level
        carol = next(p for p in company.people if p.name == "Carol Kim")
        jr_ds = next(r for r in company.roles if r.title == "Junior Data Scientist")
        match = compute_asymmetric_level_match(carol, jr_ds, roles)
        # Carol is at level ~3 role, jr data scientist is level 3 → good match
        assert match >= 0.8

    def test_over_promotion_heavier_penalty(self, company):
        roles = {r.id: r for r in company.roles}
        # Carol (Jr level 3) trying for Eng Manager (level 7) → over-promotion
        carol = next(p for p in company.people if p.name == "Carol Kim")
        eng_mgr = next(r for r in company.roles if r.title == "Engineering Manager")
        match = compute_asymmetric_level_match(carol, eng_mgr, roles)
        assert match < 0.5  # Heavy penalty for 4-level gap

    def test_under_placement_lighter_penalty(self, company):
        roles = {r.id: r for r in company.roles}
        # Bob (Eng Manager level 7) trying Jr Data Eng (level 3) → under-placement
        bob = next(p for p in company.people if p.name == "Bob Park")
        jr_de = next(r for r in company.roles if r.title == "Junior Data Engineer")
        match = compute_asymmetric_level_match(bob, jr_de, roles)
        # Under-placement has lighter penalty (0.15/gap vs 0.3/gap)
        assert match > 0.3  # Lighter penalty than over-promotion


class TestRoleSimilarity:
    def test_identical_roles(self, company):
        sr_de = next(r for r in company.roles if r.title == "Senior Data Engineer")
        sim = compute_role_similarity(sr_de, sr_de)
        assert sim == 1.0

    def test_similar_roles_high_similarity(self, company):
        sr_de = next(r for r in company.roles if r.title == "Senior Data Engineer")
        jr_de = next(r for r in company.roles if r.title == "Junior Data Engineer")
        sim = compute_role_similarity(sr_de, jr_de)
        # Both need Python and SQL; jr has 2 skills, sr has 3 → Jaccard should be decent
        assert sim > 0.3

    def test_different_roles_low_similarity(self, company):
        eng_mgr = next(r for r in company.roles if r.title == "Engineering Manager")
        fin_analyst = next(r for r in company.roles if r.title == "Financial Analyst")
        sim = compute_role_similarity(eng_mgr, fin_analyst)
        # Very different skill sets
        assert sim < 0.2

    def test_no_skills_zero(self):
        r1 = Role(id=_id("role:empty1"), title="Empty1", level=1)
        r2 = Role(id=_id("role:empty2"), title="Empty2", level=1)
        assert compute_role_similarity(r1, r2) == 0.0


class TestEnhancedHistory:
    def test_role_similarity_boost(self, company):
        """Performance in similar roles should score higher."""
        dave = next(p for p in company.people if p.name == "Dave Lee")
        roles = {r.id: r for r in company.roles}
        fin_analyst = next(r for r in company.roles if r.title == "Financial Analyst")
        eng_mgr = next(r for r in company.roles if r.title == "Engineering Manager")

        score_fin, sim_fin = compute_enhanced_history(dave, fin_analyst, roles)
        score_eng, sim_eng = compute_enhanced_history(dave, eng_mgr, roles)

        # Dave has outcomes in Financial Analyst → similarity boost for same role
        assert sim_fin >= sim_eng

    def test_no_outcomes_returns_baseline(self):
        p = Person(id=_id("person:no_hist"), name="No History")
        r = Role(id=_id("role:test"), title="Test Role", level=3)
        score, sim = compute_enhanced_history(p, r, {})
        assert score == 0.5
        assert sim == 0.0


class TestCriticalSkills:
    def test_has_all_critical(self, company):
        bob = next(p for p in company.people if p.name == "Bob Park")
        eng_mgr = next(r for r in company.roles if r.title == "Engineering Manager")
        assert check_critical_skills(bob, eng_mgr) is True

    def test_missing_critical_skill(self, company):
        carol = next(p for p in company.people if p.name == "Carol Kim")
        eng_mgr = next(r for r in company.roles if r.title == "Engineering Manager")
        # Carol doesn't have Team Leadership (critical for Eng Manager)
        assert check_critical_skills(carol, eng_mgr) is False

    def test_no_critical_requirements_always_passes(self, company):
        carol = next(p for p in company.people if p.name == "Carol Kim")
        jr_de = next(r for r in company.roles if r.title == "Junior Data Engineer")
        # Jr Data Engineer has no critical skills
        assert check_critical_skills(carol, jr_de) is True


class TestCultureFit:
    def test_matching_culture(self, company):
        # Alice has culture=collaborative, work_pref=deep_focus
        # Data Engineering dept has culture=collaborative, work=deep_focus
        alice = next(p for p in company.people if p.name == "Alice Chen")
        de_dept = next(d for d in company.departments if d.name == "Data Engineering")
        score = compute_culture_fit(alice, de_dept)
        assert score > 0.5

    def test_no_department_traits_neutral(self, company):
        alice = next(p for p in company.people if p.name == "Alice Chen")
        from talentgraph.ontology.models import Department
        empty_dept = Department(
            id=_id("dept:empty"),
            name="Empty Dept",
            roles=[],
        )
        score = compute_culture_fit(alice, empty_dept)
        assert score == 0.5

    def test_mismatched_culture(self, company):
        # Carol: culture=innovative, work=experimental
        # Finance dept: culture=analytical, work=structured
        carol = next(p for p in company.people if p.name == "Carol Kim")
        fin_dept = next(d for d in company.departments if d.name == "Finance")
        score = compute_culture_fit(carol, fin_dept)
        assert score < 0.5


class TestHeadcount:
    def test_unlimited_always_available(self, company):
        role = Role(id=_id("role:unlim"), title="Unlimited", level=3, max_headcount=0)
        dept = company.departments[0]
        assert check_headcount(role, dept, company) is True

    def test_within_headcount(self, company):
        jr_ds = next(r for r in company.roles if r.title == "Junior Data Scientist")
        ds_dept = next(d for d in company.departments if d.name == "Data Science")
        # max_headcount=4, only Carol is assigned → available
        assert check_headcount(jr_ds, ds_dept, company) is True

    def test_at_capacity(self, company):
        eng_mgr = next(r for r in company.roles if r.title == "Engineering Manager")
        mgmt_dept = next(d for d in company.departments if d.name == "Engineering Management")
        # max_headcount=1, Bob is assigned → at capacity
        assert check_headcount(eng_mgr, mgmt_dept, company) is False


class TestWeightNormalization:
    def test_normalizes_to_one(self):
        w = EnhancedWeights(
            skill_match=0.4,
            historical_performance=0.3,
            level_match=0.15,
            burnout_risk=0.15,
            morale=0.05,
            culture_fit=0.05,
        )
        normalized = normalize_weights(w)
        total = sum(normalized.values())
        assert total == pytest.approx(1.0)

    def test_zero_weights_equal_distribution(self):
        w = EnhancedWeights(
            skill_match=0.0,
            historical_performance=0.0,
            level_match=0.0,
            burnout_risk=0.0,
            morale=0.0,
            culture_fit=0.0,
        )
        normalized = normalize_weights(w)
        for v in normalized.values():
            assert v == pytest.approx(1.0 / 6)
