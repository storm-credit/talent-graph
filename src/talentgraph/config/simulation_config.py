"""SimulationConfig: central configuration for all simulation parameters.

Replaces 50+ hardcoded magic numbers across scoring/ and simulation/ modules.
All parameters have academic references or design rationale documented.

Default values match the actual code in simulation/ modules so that behavior
is identical whether or not a config is passed.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from talentgraph.ontology.enums import OutcomeRating


class ScoringConfig(BaseModel):
    """Parameters for the scoring engine (read-only reference).

    These document the constants used in scoring/ modules.
    scoring/ is read-only, so these values cannot be injected at runtime,
    but they serve as the canonical reference for algorithm documentation.
    """

    # Historical performance
    history_half_life_days: float = Field(
        default=730.0,
        description="Exponential decay half-life in days for historical outcomes. "
        "Murphy & Cleveland (1995): recent performance is more predictive.",
    )
    same_role_boost: float = Field(
        default=1.5,
        description="Multiplier for outcomes from the same role. "
        "Same-role experience is more predictive of future performance.",
    )
    no_history_default: float = Field(
        default=0.5,
        description="Default score when no historical outcomes exist (neutral prior).",
    )

    # Level match
    level_gap_tolerance: int = Field(
        default=1,
        description="Gap within which no penalty is applied. "
        "Benson et al. (2019): 1-level promotions are productive.",
    )
    level_gap_penalty: float = Field(
        default=0.2,
        description="Penalty per level beyond tolerance. "
        "Peter Principle: over-promotion leads to incompetence.",
    )
    no_level_default: float = Field(
        default=0.5,
        description="Default level match score when person level is unknown.",
    )

    # Burnout
    burnout_staleness_weight: float = Field(
        default=0.6,
        description="Weight of staleness risk in burnout calculation. "
        "Maslach & Leiter (2016): tenure stagnation is primary burnout driver.",
    )
    burnout_decline_weight: float = Field(
        default=0.4,
        description="Weight of performance decline in burnout calculation.",
    )
    burnout_no_assignment_default: float = Field(
        default=0.1,
        description="Default burnout risk with no assignment history.",
    )
    staleness_thresholds: list[tuple[float, float]] = Field(
        default=[(2.0, 0.0), (3.0, 0.2), (5.0, 0.5)],
        description="(years_threshold, risk_value) pairs for staleness risk. "
        "Values above the last threshold use staleness_max_risk.",
    )
    staleness_max_risk: float = Field(
        default=0.8,
        description="Maximum staleness risk for very long tenure.",
    )
    decline_normalizer: float = Field(
        default=2.0,
        description="Divides raw performance decline to get risk. "
        "A 2-point rating drop = max risk (1.0).",
    )

    # Predicted performance
    predicted_perf_base: float = Field(
        default=1.0,
        description="Base value for predicted performance mapping.",
    )
    predicted_perf_multiplier: float = Field(
        default=4.0,
        description="Scales fit score to performance range.",
    )
    predicted_perf_history_adj: float = Field(
        default=0.5,
        description="Historical performance adjustment factor.",
    )


class GrowthConfig(BaseModel):
    """Parameters for skill growth/decay system."""

    # Growth probabilities by gap (PA - CA levels)
    gap_1_growth_prob: float = Field(
        default=0.15,
        description="Growth probability when PA is 1 level above CA. "
        "Dreyfus model: small gaps = slow growth.",
    )
    gap_2_growth_prob: float = Field(
        default=0.25,
        description="Growth probability when PA is 2 levels above CA. "
        "Optimal challenge zone (Vygotsky ZPD).",
    )
    gap_3_growth_prob: float = Field(
        default=0.35,
        description="Growth probability when PA is 3 levels above CA.",
    )
    gap_4_growth_prob: float = Field(
        default=0.40,
        description="Growth probability when PA is 4 levels above CA. "
        "High potential = fast growth.",
    )

    # Morale-based growth modifier (in _compute_growth_modifier)
    morale_threshold: float = Field(
        default=0.5,
        description="Morale baseline for growth modifier calculation.",
    )
    morale_growth_scale: float = Field(
        default=0.6,
        description="Scale factor for morale-based growth modifier. "
        "morale_mod = 1.0 + max(0, (morale - threshold)) * scale.",
    )

    # Tenure diminishing returns
    tenure_slowdown_years: float = Field(
        default=5.0,
        description="Years of tenure after which growth rate starts declining.",
    )
    tenure_slowdown_rate: float = Field(
        default=0.05,
        description="Growth reduction per year beyond tenure_slowdown_years.",
    )
    tenure_min_modifier: float = Field(
        default=0.5,
        description="Minimum tenure-based growth modifier (floor).",
    )

    # Max growth probability cap
    max_growth_probability: float = Field(
        default=0.95,
        description="Hard cap on per-quarter growth probability after modifiers.",
    )

    # Decay
    idle_quarters_before_decay: int = Field(
        default=4,
        description="Quarters of inactivity before skill decay begins. "
        "Ebbinghaus (1885): forgetting curve onset.",
    )
    decay_probability: float = Field(
        default=0.10,
        description="Probability of losing one skill level per quarter after idle threshold.",
    )
    min_skill_level: int = Field(
        default=1,
        description="Minimum skill level (NOVICE = 1). Cannot decay below this.",
    )

    def growth_probability_map(self) -> dict[int, float]:
        """Build the gap → probability lookup from individual fields."""
        return {
            0: 0.00,
            1: self.gap_1_growth_prob,
            2: self.gap_2_growth_prob,
            3: self.gap_3_growth_prob,
            4: self.gap_4_growth_prob,
        }


class MoraleConfig(BaseModel):
    """Parameters for morale system."""

    # Outcome morale deltas
    outcome_exceptional_delta: float = Field(
        default=0.08,
        description="Morale boost from EXCEPTIONAL outcome.",
    )
    outcome_exceeds_delta: float = Field(
        default=0.04,
        description="Morale boost from EXCEEDS outcome.",
    )
    outcome_meets_delta: float = Field(
        default=0.00,
        description="Morale change from MEETS outcome (neutral).",
    )
    outcome_below_delta: float = Field(
        default=-0.05,
        description="Morale penalty from BELOW outcome.",
    )
    outcome_unsatisfactory_delta: float = Field(
        default=-0.10,
        description="Morale penalty from UNSATISFACTORY outcome.",
    )

    # Mean reversion
    mean_reversion_rate: float = Field(
        default=0.05,
        description="Rate of morale regression toward baseline. "
        "Hedonic adaptation: morale tends toward equilibrium.",
    )
    mean_reversion_target: float = Field(
        default=0.5,
        description="Baseline morale target for mean reversion.",
    )

    # Burnout drag
    burnout_drag_coefficient: float = Field(
        default=-0.03,
        description="Morale penalty per 0.1 burnout above threshold. "
        "Maslach: burnout directly drags down job satisfaction.",
    )
    burnout_drag_threshold: float = Field(
        default=0.3,
        description="Burnout level above which morale drag kicks in.",
    )
    burnout_drag_divisor: float = Field(
        default=0.1,
        description="Divides (burnout - threshold) to get drag multiplier.",
    )

    # Placement
    placement_boost: float = Field(
        default=0.10,
        description="Morale boost from receiving a new role assignment.",
    )

    # Stagnation
    stagnation_penalty: float = Field(
        default=-0.02,
        description="Morale penalty when in same role beyond stagnation threshold.",
    )
    stagnation_years_threshold: float = Field(
        default=3.0,
        description="Years in same role before stagnation penalty applies.",
    )

    # Noise
    random_noise_stddev: float = Field(
        default=0.01,
        description="Standard deviation for random morale jitter (Gaussian).",
    )

    # Bounds
    morale_min: float = Field(default=0.0, description="Minimum morale value.")
    morale_max: float = Field(default=1.0, description="Maximum morale value.")

    def outcome_morale_delta_map(self) -> dict[OutcomeRating, float]:
        """Build OutcomeRating → delta lookup from individual fields."""
        return {
            OutcomeRating.EXCEPTIONAL: self.outcome_exceptional_delta,
            OutcomeRating.EXCEEDS: self.outcome_exceeds_delta,
            OutcomeRating.MEETS: self.outcome_meets_delta,
            OutcomeRating.BELOW: self.outcome_below_delta,
            OutcomeRating.UNSATISFACTORY: self.outcome_unsatisfactory_delta,
        }


class AttritionConfig(BaseModel):
    """Parameters for attrition model."""

    base_rate: float = Field(
        default=0.02,
        description="Base quarterly attrition rate (2%). "
        "March & Simon (1958): organizational equilibrium theory.",
    )
    burnout_coefficient: float = Field(
        default=0.15,
        description="Risk added per unit of burnout above burnout_threshold.",
    )
    burnout_threshold: float = Field(
        default=0.3,
        description="Burnout level above which attrition risk increases.",
    )
    morale_coefficient: float = Field(
        default=0.12,
        description="Risk added per unit of morale below morale_threshold.",
    )
    morale_threshold: float = Field(
        default=0.5,
        description="Morale level below which attrition risk increases.",
    )

    # U-shaped tenure curve
    early_tenure_years: float = Field(
        default=1.0,
        description="Years defining early tenure (high turnover).",
    )
    early_tenure_multiplier: float = Field(
        default=1.5,
        description="Attrition multiplier for early-career employees (<1 year).",
    )
    mid_tenure_years: tuple[float, float] = Field(
        default=(1.0, 5.0),
        description="Year range defining stable mid-career (low turnover).",
    )
    mid_tenure_multiplier: float = Field(
        default=1.0,
        description="Attrition multiplier for mid-career stability (1-5 years).",
    )
    late_ramp_years: tuple[float, float] = Field(
        default=(5.0, 8.0),
        description="Year range where attrition ramps from mid to late multiplier.",
    )
    late_ramp_rate: float = Field(
        default=0.067,
        description="Annual ramp rate for late-career attrition multiplier.",
    )
    max_tenure_multiplier: float = Field(
        default=1.5,
        description="Attrition multiplier for very long tenure (8+ years).",
    )
    max_attrition_probability: float = Field(
        default=0.30,
        description="Hard cap on per-quarter attrition probability.",
    )


class EventConfig(BaseModel):
    """Parameters for random event generation."""

    # Company-wide event probabilities (per event type per quarter)
    market_boom_probability: float = Field(
        default=0.05,
        description="Probability of market boom event per quarter.",
    )
    market_downturn_probability: float = Field(
        default=0.05,
        description="Probability of market downturn event per quarter.",
    )
    reorg_probability: float = Field(
        default=0.03,
        description="Probability of reorganization event per quarter.",
    )

    # Individual event probabilities (per person per quarter)
    certification_probability: float = Field(
        default=0.08,
        description="Probability of certification event per person per quarter.",
    )
    personal_issue_probability: float = Field(
        default=0.05,
        description="Probability of personal issue event per person per quarter.",
    )
    mentoring_probability: float = Field(
        default=0.06,
        description="Probability of mentoring event per person per quarter.",
    )

    # Event effects
    market_boom_morale_range: tuple[float, float] = Field(
        default=(0.02, 0.06),
        description="Morale boost range (uniform) from market boom event.",
    )
    market_downturn_morale_range: tuple[float, float] = Field(
        default=(0.03, 0.08),
        description="Morale penalty range (uniform) from market downturn event.",
    )
    reorg_morale_range: tuple[float, float] = Field(
        default=(0.02, 0.05),
        description="Morale penalty range (uniform) from reorganization event.",
    )
    personal_issue_morale_range: tuple[float, float] = Field(
        default=(0.05, 0.15),
        description="Morale penalty range (uniform) from personal issue event.",
    )
    mentoring_morale_boost: float = Field(
        default=0.05,
        description="Fixed morale boost from mentoring event.",
    )
    mentoring_learning_acceleration: int = Field(
        default=2,
        description="Extra quarters_active added to a random skill from mentoring.",
    )


class EnhancedQuarterConfig(BaseModel):
    """Parameters for enhanced quarter outcome adjustment."""

    morale_performance_shift_factor: float = Field(
        default=0.5,
        description="How much morale deviation from 0.5 shifts predicted performance. "
        "morale_shift = (morale - 0.5) * factor.",
    )
    morale_performance_baseline: float = Field(
        default=0.5,
        description="Morale baseline for outcome distribution adjustment.",
    )


class SimulationConfig(BaseModel):
    """Master configuration for the entire simulation.

    Groups all tunable parameters that were previously hardcoded
    across the scoring/ and simulation/ modules.

    Default values are set to match the actual code behavior exactly,
    so the simulation produces identical results with or without config.
    """

    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    growth: GrowthConfig = Field(default_factory=GrowthConfig)
    morale: MoraleConfig = Field(default_factory=MoraleConfig)
    attrition: AttritionConfig = Field(default_factory=AttritionConfig)
    events: EventConfig = Field(default_factory=EventConfig)
    enhanced_quarter: EnhancedQuarterConfig = Field(
        default_factory=EnhancedQuarterConfig
    )

    def total_parameters(self) -> int:
        """Count the total number of configurable parameters."""
        count = 0
        for section_cls in [
            ScoringConfig,
            GrowthConfig,
            MoraleConfig,
            AttritionConfig,
            EventConfig,
            EnhancedQuarterConfig,
        ]:
            count += len(section_cls.model_fields)
        return count
