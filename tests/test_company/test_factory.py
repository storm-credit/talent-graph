"""Tests for company factory — template → Company generation."""

from __future__ import annotations

import pytest

from talentgraph.company.factory import (
    build_config_for_profile,
    create_company_from_template,
)
from talentgraph.company.profile import (
    CompanyProfile,
    CultureType,
    GrowthStage,
    IndustryType,
)
from talentgraph.config.simulation_config import SimulationConfig
from talentgraph.ontology.models import Company
from talentgraph.scoring.engine import FitScoreEngine
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures


class TestCompanyFactory:
    """Test company generation from templates."""

    @pytest.fixture(params=list(IndustryType))
    def profile(self, request) -> CompanyProfile:
        return CompanyProfile(
            industry=request.param,
            name=f"Test {request.param.value}",
            num_people=10,
            growth_stage=GrowthStage.GROWTH,
        )

    def test_creates_valid_company(self, profile):
        company = create_company_from_template(profile)
        assert isinstance(company, Company)
        assert company.name == profile.name

    def test_correct_people_count(self, profile):
        company = create_company_from_template(profile)
        assert len(company.people) == profile.num_people

    def test_has_departments(self, profile):
        company = create_company_from_template(profile)
        assert len(company.departments) >= 2

    def test_has_roles(self, profile):
        company = create_company_from_template(profile)
        assert len(company.roles) >= 3

    def test_has_skills(self, profile):
        company = create_company_from_template(profile)
        assert len(company.skills) >= 5

    def test_people_have_skills(self, profile):
        company = create_company_from_template(profile)
        for person in company.people:
            assert len(person.skills) >= 4

    def test_people_have_valid_morale(self, profile):
        company = create_company_from_template(profile)
        for person in company.people:
            assert 0.0 <= person.morale <= 1.0

    def test_people_have_assignments(self, profile):
        company = create_company_from_template(profile)
        assigned = [p for p in company.people if len(p.assignments) > 0]
        assert len(assigned) > 0  # at least some people are assigned

    def test_deterministic_generation(self, profile):
        """Same seed produces identical companies."""
        c1 = create_company_from_template(profile, seed=42)
        c2 = create_company_from_template(profile, seed=42)
        assert len(c1.people) == len(c2.people)
        assert [p.name for p in c1.people] == [p.name for p in c2.people]

    def test_different_seeds_produce_different_companies(self, profile):
        """Different seeds produce different people (names may vary)."""
        c1 = create_company_from_template(profile, seed=42)
        c2 = create_company_from_template(profile, seed=99)
        # At least some names should differ
        names1 = {p.name for p in c1.people}
        names2 = {p.name for p in c2.people}
        assert names1 != names2


class TestCompanyFactoryScaling:
    """Test different company sizes."""

    def test_small_company(self):
        profile = CompanyProfile(
            industry=IndustryType.TECH_STARTUP,
            name="Tiny Startup",
            num_people=3,
            growth_stage=GrowthStage.EARLY,
        )
        company = create_company_from_template(profile)
        assert len(company.people) == 3

    def test_medium_company(self):
        profile = CompanyProfile(
            industry=IndustryType.ENTERPRISE_IT,
            name="Mid Corp",
            num_people=30,
            growth_stage=GrowthStage.MATURE,
        )
        company = create_company_from_template(profile)
        assert len(company.people) == 30

    def test_large_company(self):
        profile = CompanyProfile(
            industry=IndustryType.MANUFACTURING,
            name="Big Factory",
            num_people=50,
            growth_stage=GrowthStage.ENTERPRISE,
        )
        company = create_company_from_template(profile)
        assert len(company.people) == 50


class TestCompanyFactoryIntegration:
    """Test that generated companies work with scoring and simulation."""

    def test_scoring_engine_works(self):
        profile = CompanyProfile(
            industry=IndustryType.TECH_STARTUP,
            name="Score Test Co",
            num_people=8,
        )
        company = create_company_from_template(profile)
        engine = FitScoreEngine(company)
        # At least one person should be evaluable
        for person in company.people:
            if person.assignments:
                results = engine.evaluate_person(person.id)
                assert len(results) > 0
                break

    def test_simulation_engine_works(self):
        profile = CompanyProfile(
            industry=IndustryType.CONSULTING,
            name="Sim Test Firm",
            num_people=8,
        )
        company = create_company_from_template(profile)
        engine = SimulationEngine(
            company,
            seed=42,
            features=SimulationFeatures(enhanced=True),
        )
        quarter, changes = engine.advance()
        assert quarter is not None

    def test_simulation_with_industry_config(self):
        profile = CompanyProfile(
            industry=IndustryType.HEALTHCARE,
            name="Hospital Sim",
            num_people=10,
        )
        company = create_company_from_template(profile)
        config = build_config_for_profile(profile)

        engine = SimulationEngine(
            company,
            seed=42,
            features=SimulationFeatures(enhanced=True),
            config=config,
        )
        quarter, changes = engine.advance()
        assert quarter is not None
        # Healthcare config should have lower attrition
        assert config.attrition.base_rate == 0.015


class TestBuildConfigForProfile:
    """Test industry-specific config overrides."""

    def test_tech_startup_has_higher_attrition(self):
        profile = CompanyProfile(industry=IndustryType.TECH_STARTUP, name="T")
        config = build_config_for_profile(profile)
        assert config.attrition.base_rate == 0.03

    def test_manufacturing_has_slower_growth(self):
        profile = CompanyProfile(industry=IndustryType.MANUFACTURING, name="M")
        config = build_config_for_profile(profile)
        assert config.growth.gap_1_growth_prob == 0.10

    def test_consulting_has_higher_stagnation_penalty(self):
        profile = CompanyProfile(industry=IndustryType.CONSULTING, name="C")
        config = build_config_for_profile(profile)
        assert config.morale.stagnation_penalty == -0.03

    def test_healthcare_has_rare_reorgs(self):
        profile = CompanyProfile(industry=IndustryType.HEALTHCARE, name="H")
        config = build_config_for_profile(profile)
        assert config.events.reorg_probability == 0.01

    def test_default_values_preserved(self):
        """Non-overridden values should keep defaults."""
        profile = CompanyProfile(industry=IndustryType.TECH_STARTUP, name="T")
        config = build_config_for_profile(profile)
        default = SimulationConfig()
        assert config.morale.mean_reversion_rate == default.morale.mean_reversion_rate
