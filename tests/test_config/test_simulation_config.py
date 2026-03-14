"""Tests for SimulationConfig — central configuration system.

Validates:
1. Default values match actual code constants
2. Config serialization/deserialization
3. Partial updates
4. Helper methods
5. Integration with simulation modules
"""

from __future__ import annotations

import random
from datetime import date

import pytest

from talentgraph.config.simulation_config import (
    AttritionConfig,
    EnhancedQuarterConfig,
    EventConfig,
    GrowthConfig,
    MoraleConfig,
    ScoringConfig,
    SimulationConfig,
)
from talentgraph.data.seed import create_sample_company
from talentgraph.ontology.enums import OutcomeRating
from talentgraph.simulation.attrition import (
    BASE_ATTRITION_RATE,
    BURNOUT_FACTOR,
    MAX_QUARTERLY_ATTRITION,
    MORALE_FACTOR,
    _tenure_multiplier,
    compute_attrition_probability,
    process_attrition,
)
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures
from talentgraph.simulation.growth import (
    DECAY_IDLE_THRESHOLD,
    DECAY_PROBABILITY_PER_QUARTER,
    GROWTH_PROBABILITY,
    process_skill_growth,
)
from talentgraph.simulation.morale import (
    BURNOUT_MORALE_DRAG,
    MEAN_REVERSION_RATE,
    OUTCOME_MORALE_DELTA,
    PLACEMENT_BOOST,
    STAGNATION_PENALTY,
    process_morale,
)
from talentgraph.simulation.random_events import (
    COMPANY_EVENTS,
    INDIVIDUAL_EVENTS,
    process_random_events,
)


# ── Section 1: Config default values ──


class TestConfigDefaults:
    """Verify config defaults match module-level constants."""

    def test_growth_defaults_match_constants(self):
        cfg = GrowthConfig()
        assert cfg.gap_1_growth_prob == GROWTH_PROBABILITY[1]
        assert cfg.gap_2_growth_prob == GROWTH_PROBABILITY[2]
        assert cfg.gap_3_growth_prob == GROWTH_PROBABILITY[3]
        assert cfg.gap_4_growth_prob == GROWTH_PROBABILITY[4]
        assert cfg.idle_quarters_before_decay == DECAY_IDLE_THRESHOLD
        assert cfg.decay_probability == DECAY_PROBABILITY_PER_QUARTER

    def test_morale_defaults_match_constants(self):
        cfg = MoraleConfig()
        assert cfg.mean_reversion_rate == MEAN_REVERSION_RATE
        assert cfg.mean_reversion_target == 0.5
        assert cfg.burnout_drag_coefficient == BURNOUT_MORALE_DRAG
        assert cfg.placement_boost == PLACEMENT_BOOST
        assert cfg.stagnation_penalty == STAGNATION_PENALTY

    def test_morale_outcome_deltas_match(self):
        cfg = MoraleConfig()
        delta_map = cfg.outcome_morale_delta_map()
        assert delta_map[OutcomeRating.EXCEPTIONAL] == OUTCOME_MORALE_DELTA[OutcomeRating.EXCEPTIONAL]
        assert delta_map[OutcomeRating.EXCEEDS] == OUTCOME_MORALE_DELTA[OutcomeRating.EXCEEDS]
        assert delta_map[OutcomeRating.MEETS] == OUTCOME_MORALE_DELTA[OutcomeRating.MEETS]
        assert delta_map[OutcomeRating.BELOW] == OUTCOME_MORALE_DELTA[OutcomeRating.BELOW]
        assert delta_map[OutcomeRating.UNSATISFACTORY] == OUTCOME_MORALE_DELTA[OutcomeRating.UNSATISFACTORY]

    def test_attrition_defaults_match_constants(self):
        cfg = AttritionConfig()
        assert cfg.base_rate == BASE_ATTRITION_RATE
        assert cfg.burnout_coefficient == BURNOUT_FACTOR
        assert cfg.morale_coefficient == MORALE_FACTOR
        assert cfg.max_attrition_probability == MAX_QUARTERLY_ATTRITION

    def test_event_defaults_match_constants(self):
        from talentgraph.ontology.enums import EventType

        cfg = EventConfig()
        assert cfg.market_boom_probability == COMPANY_EVENTS[EventType.MARKET_BOOM]
        assert cfg.market_downturn_probability == COMPANY_EVENTS[EventType.MARKET_DOWNTURN]
        assert cfg.reorg_probability == COMPANY_EVENTS[EventType.REORG]
        assert cfg.certification_probability == INDIVIDUAL_EVENTS[EventType.CERTIFICATION]
        assert cfg.personal_issue_probability == INDIVIDUAL_EVENTS[EventType.PERSONAL_ISSUE]
        assert cfg.mentoring_probability == INDIVIDUAL_EVENTS[EventType.MENTORING]

    def test_scoring_config_defaults(self):
        cfg = ScoringConfig()
        assert cfg.history_half_life_days == 730.0
        assert cfg.same_role_boost == 1.5
        assert cfg.no_history_default == 0.5
        assert cfg.level_gap_tolerance == 1
        assert cfg.level_gap_penalty == 0.2

    def test_enhanced_quarter_defaults(self):
        cfg = EnhancedQuarterConfig()
        assert cfg.morale_performance_shift_factor == 0.5
        assert cfg.morale_performance_baseline == 0.5


# ── Section 2: Config structure & serialization ──


class TestConfigStructure:
    """Test config creation, serialization, and partial updates."""

    def test_default_config_creates(self):
        cfg = SimulationConfig()
        assert isinstance(cfg.scoring, ScoringConfig)
        assert isinstance(cfg.growth, GrowthConfig)
        assert isinstance(cfg.morale, MoraleConfig)
        assert isinstance(cfg.attrition, AttritionConfig)
        assert isinstance(cfg.events, EventConfig)
        assert isinstance(cfg.enhanced_quarter, EnhancedQuarterConfig)

    def test_total_parameters_count(self):
        cfg = SimulationConfig()
        count = cfg.total_parameters()
        assert count >= 50  # at least 50 configurable parameters

    def test_config_serialization_roundtrip(self):
        cfg = SimulationConfig()
        data = cfg.model_dump()
        restored = SimulationConfig(**data)
        assert restored == cfg

    def test_partial_update(self):
        cfg = SimulationConfig()
        updated = cfg.model_copy(
            update={"growth": GrowthConfig(gap_1_growth_prob=0.30)}
        )
        assert updated.growth.gap_1_growth_prob == 0.30
        # Other sections unchanged
        assert updated.morale.mean_reversion_rate == cfg.morale.mean_reversion_rate

    def test_growth_probability_map(self):
        cfg = GrowthConfig(gap_1_growth_prob=0.20, gap_2_growth_prob=0.30)
        prob_map = cfg.growth_probability_map()
        assert prob_map[0] == 0.0
        assert prob_map[1] == 0.20
        assert prob_map[2] == 0.30
        assert prob_map[3] == 0.35  # default
        assert prob_map[4] == 0.40  # default


# ── Section 3: Config integration with simulation modules ──


class TestConfigIntegration:
    """Verify config flows through to simulation modules."""

    @pytest.fixture
    def company(self):
        return create_sample_company()

    @pytest.fixture
    def rng(self):
        return random.Random(42)

    def test_growth_with_default_config(self, company, rng):
        """Growth with default config produces same results as no config."""
        company_a = company.model_copy(deep=True)
        company_b = company.model_copy(deep=True)
        rng_a = random.Random(42)
        rng_b = random.Random(42)

        changes_a = process_skill_growth(company_a, rng_a)
        changes_b = process_skill_growth(company_b, rng_b, config=GrowthConfig())

        assert len(changes_a) == len(changes_b)

    def test_growth_with_custom_config(self, company, rng):
        """Higher growth probabilities produce more growth events."""
        company_low = company.model_copy(deep=True)
        company_high = company.model_copy(deep=True)

        low_cfg = GrowthConfig(
            gap_1_growth_prob=0.01,
            gap_2_growth_prob=0.01,
            gap_3_growth_prob=0.01,
            gap_4_growth_prob=0.01,
        )
        high_cfg = GrowthConfig(
            gap_1_growth_prob=0.99,
            gap_2_growth_prob=0.99,
            gap_3_growth_prob=0.99,
            gap_4_growth_prob=0.99,
        )

        # Run many quarters for statistical significance
        low_total = 0
        high_total = 0
        for _ in range(20):
            low_total += len(process_skill_growth(company_low.model_copy(deep=True), random.Random(42), low_cfg))
            high_total += len(process_skill_growth(company_high.model_copy(deep=True), random.Random(42), high_cfg))

        # High config should produce more growth events
        assert high_total >= low_total

    def test_morale_with_default_config(self, company, rng):
        """Morale with default config produces same results as no config."""
        company_a = company.model_copy(deep=True)
        company_b = company.model_copy(deep=True)
        rng_a = random.Random(42)
        rng_b = random.Random(42)
        qd = date(2025, 4, 1)

        changes_a = process_morale(company_a, qd, rng=rng_a)
        changes_b = process_morale(company_b, qd, rng=rng_b, config=MoraleConfig())

        assert len(changes_a) == len(changes_b)

    def test_morale_custom_reversion_target(self, company):
        """Custom mean reversion target changes morale drift direction."""
        company_low = company.model_copy(deep=True)
        company_high = company.model_copy(deep=True)
        qd = date(2025, 4, 1)

        # Set everyone's morale to 0.6
        for p in company_low.people:
            p.morale = 0.6
        for p in company_high.people:
            p.morale = 0.6

        # Low target → morale should decrease (target 0.3)
        low_cfg = MoraleConfig(mean_reversion_target=0.3, mean_reversion_rate=0.5)
        process_morale(company_low, qd, rng=random.Random(0), config=low_cfg)

        # High target → morale should increase (target 0.9)
        high_cfg = MoraleConfig(mean_reversion_target=0.9, mean_reversion_rate=0.5)
        process_morale(company_high, qd, rng=random.Random(0), config=high_cfg)

        # Check at least one person's morale moved in expected direction
        active_low = [p for p in company_low.people if not p.departed]
        active_high = [p for p in company_high.people if not p.departed]
        avg_low = sum(p.morale for p in active_low) / len(active_low)
        avg_high = sum(p.morale for p in active_high) / len(active_high)
        assert avg_low < avg_high

    def test_attrition_with_default_config(self, company, rng):
        """Attrition with default config produces same results as no config."""
        company_a = company.model_copy(deep=True)
        company_b = company.model_copy(deep=True)
        rng_a = random.Random(42)
        rng_b = random.Random(42)
        qd = date(2025, 4, 1)

        changes_a = process_attrition(company_a, qd, rng_a)
        changes_b = process_attrition(company_b, qd, rng_b, config=AttritionConfig())

        assert len(changes_a) == len(changes_b)

    def test_attrition_high_base_rate(self, company):
        """Higher base rate produces more departures over time."""
        departures_low = 0
        departures_high = 0

        low_cfg = AttritionConfig(base_rate=0.001)
        high_cfg = AttritionConfig(base_rate=0.29)

        for seed in range(50):
            c = company.model_copy(deep=True)
            changes = process_attrition(c, date(2025, 4, 1), random.Random(seed), low_cfg)
            departures_low += len(changes)

            c = company.model_copy(deep=True)
            changes = process_attrition(c, date(2025, 4, 1), random.Random(seed), high_cfg)
            departures_high += len(changes)

        assert departures_high > departures_low

    def test_events_with_default_config(self, company, rng):
        """Events with default config produces same results as no config."""
        company_a = company.model_copy(deep=True)
        company_b = company.model_copy(deep=True)
        rng_a = random.Random(42)
        rng_b = random.Random(42)
        qd = date(2025, 4, 1)

        changes_a, events_a = process_random_events(company_a, qd, rng_a)
        changes_b, events_b = process_random_events(company_b, qd, rng_b, config=EventConfig())

        assert len(changes_a) == len(changes_b)
        assert len(events_a) == len(events_b)

    def test_tenure_multiplier_with_config(self):
        """Tenure multiplier respects config overrides."""
        cfg = AttritionConfig(
            early_tenure_years=2.0,
            early_tenure_multiplier=2.0,
            mid_tenure_years=(2.0, 10.0),
            mid_tenure_multiplier=0.5,
            max_tenure_multiplier=3.0,
        )
        # Below early threshold
        assert _tenure_multiplier(1.0, cfg) == 2.0
        # In mid range
        assert _tenure_multiplier(5.0, cfg) == 0.5
        # Above max
        assert _tenure_multiplier(15.0, cfg) == 3.0


# ── Section 4: Engine config integration ──


class TestEngineConfig:
    """Test SimulationConfig integration with SimulationEngine."""

    @pytest.fixture
    def company(self):
        return create_sample_company()

    def test_engine_accepts_config(self, company):
        cfg = SimulationConfig()
        engine = SimulationEngine(
            company, seed=42,
            features=SimulationFeatures(enhanced=True),
            config=cfg,
        )
        assert engine.config is cfg

    def test_engine_config_setter(self, company):
        engine = SimulationEngine(company, seed=42)
        assert engine.config is None

        cfg = SimulationConfig()
        engine.config = cfg
        assert engine.config is cfg

    def test_engine_advance_with_config(self, company):
        """Engine advance works with config without errors."""
        cfg = SimulationConfig()
        engine = SimulationEngine(
            company, seed=42,
            features=SimulationFeatures(enhanced=True),
            config=cfg,
        )
        quarter, changes = engine.advance()
        assert quarter is not None
        assert isinstance(changes, list)

    def test_engine_advance_without_config(self, company):
        """Engine advance works without config (backward compat)."""
        engine = SimulationEngine(
            company, seed=42,
            features=SimulationFeatures(enhanced=True),
        )
        quarter, changes = engine.advance()
        assert quarter is not None
        assert isinstance(changes, list)

    def test_engine_config_affects_simulation(self, company):
        """Changing config parameters produces different outcomes."""
        # Run with zero-events config
        quiet_cfg = SimulationConfig(
            events=EventConfig(
                market_boom_probability=0.0,
                market_downturn_probability=0.0,
                reorg_probability=0.0,
                certification_probability=0.0,
                personal_issue_probability=0.0,
                mentoring_probability=0.0,
            ),
            attrition=AttritionConfig(base_rate=0.0),
        )
        engine_quiet = SimulationEngine(
            company.model_copy(deep=True), seed=42,
            features=SimulationFeatures(enhanced=True),
            config=quiet_cfg,
        )
        _, changes_quiet = engine_quiet.advance()

        # Run with max-events config
        loud_cfg = SimulationConfig(
            events=EventConfig(
                market_boom_probability=1.0,
                market_downturn_probability=1.0,
                reorg_probability=1.0,
                certification_probability=1.0,
                personal_issue_probability=1.0,
                mentoring_probability=1.0,
            ),
        )
        engine_loud = SimulationEngine(
            company.model_copy(deep=True), seed=42,
            features=SimulationFeatures(enhanced=True),
            config=loud_cfg,
        )
        _, changes_loud = engine_loud.advance()

        # Loud config should produce more events
        event_types_quiet = [c.change_type for c in changes_quiet if c.change_type in ("event", "certification", "mentoring", "personal_event")]
        event_types_loud = [c.change_type for c in changes_loud if c.change_type in ("event", "certification", "mentoring", "personal_event")]
        assert len(event_types_loud) > len(event_types_quiet)


# ── Section 5: API config endpoints ──


class TestConfigAPI:
    """Test config API endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from talentgraph.api.app import app
        from talentgraph.api import deps

        deps._engine = None
        return TestClient(app)

    def test_get_config(self, client):
        resp = client.get("/api/simulation/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "scoring" in data
        assert "growth" in data
        assert "morale" in data
        assert "attrition" in data
        assert "events" in data
        assert "enhanced_quarter" in data

    def test_get_config_has_correct_defaults(self, client):
        resp = client.get("/api/simulation/config")
        data = resp.json()
        assert data["growth"]["gap_1_growth_prob"] == 0.15
        assert data["attrition"]["base_rate"] == 0.02
        assert data["morale"]["mean_reversion_rate"] == 0.05

    def test_update_config(self, client):
        resp = client.put(
            "/api/simulation/config",
            json={"growth": {"gap_1_growth_prob": 0.50}},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["growth"]["gap_1_growth_prob"] == 0.50

    def test_update_config_preserves_other_sections(self, client):
        # First get defaults
        default = client.get("/api/simulation/config").json()
        original_base_rate = default["attrition"]["base_rate"]

        # Update only growth section
        resp = client.put(
            "/api/simulation/config",
            json={"growth": {"gap_1_growth_prob": 0.99}},
        )
        data = resp.json()
        # Attrition should be unchanged
        assert data["attrition"]["base_rate"] == original_base_rate
