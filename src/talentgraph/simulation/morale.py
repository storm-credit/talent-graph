"""Morale / engagement system.

Morale is [0.0, 1.0] and drifts each quarter based on:
- Positive outcomes → morale up
- Negative outcomes → morale down
- Promotion/role change → morale boost
- Burnout risk → morale drag
- Stagnation (same role 3+ years, no growth) → morale down
- Natural regression toward 0.5 over time (mean reversion)
"""

from __future__ import annotations

import random
from datetime import date

from talentgraph.config.simulation_config import MoraleConfig
from talentgraph.ontology.enums import OutcomeRating
from talentgraph.ontology.models import Company, Person
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.state import ChangeRecord

# Morale deltas per outcome rating
OUTCOME_MORALE_DELTA: dict[OutcomeRating, float] = {
    OutcomeRating.EXCEPTIONAL: +0.08,
    OutcomeRating.EXCEEDS: +0.04,
    OutcomeRating.MEETS: +0.00,
    OutcomeRating.BELOW: -0.05,
    OutcomeRating.UNSATISFACTORY: -0.10,
}

MEAN_REVERSION_RATE = 0.05  # how fast morale drifts toward 0.5
MEAN_REVERSION_TARGET = 0.5  # target for mean reversion
BURNOUT_MORALE_DRAG = -0.03  # per 0.1 burnout above 0.3
BURNOUT_DRAG_THRESHOLD = 0.3  # burnout threshold for drag
BURNOUT_DRAG_DIVISOR = 0.1  # divisor for drag multiplier
PLACEMENT_BOOST = 0.10  # morale boost from a new role
STAGNATION_PENALTY = -0.02  # per quarter of high staleness
STAGNATION_YEARS = 3.0  # years in same role before penalty
NOISE_STDDEV = 0.01  # standard deviation of random morale jitter


def process_morale(
    company: Company,
    quarter_date: date,
    recent_outcomes: dict[str, OutcomeRating] | None = None,
    recent_placements: set[str] | None = None,
    rng: random.Random | None = None,
    config: MoraleConfig | None = None,
) -> list[ChangeRecord]:
    """Update morale for all people. Mutates company in place.

    Args:
        recent_outcomes: {person_id_str: OutcomeRating} from this quarter
        recent_placements: set of person_id_str who got new roles this quarter
        config: optional MoraleConfig to override module-level constants
    """
    if rng is None:
        rng = random.Random()
    if recent_outcomes is None:
        recent_outcomes = {}
    if recent_placements is None:
        recent_placements = set()

    # Resolve config or use module-level constants
    outcome_deltas = config.outcome_morale_delta_map() if config else OUTCOME_MORALE_DELTA
    mean_rate = config.mean_reversion_rate if config else MEAN_REVERSION_RATE
    mean_target = config.mean_reversion_target if config else MEAN_REVERSION_TARGET
    burnout_drag = config.burnout_drag_coefficient if config else BURNOUT_MORALE_DRAG
    burnout_thresh = config.burnout_drag_threshold if config else BURNOUT_DRAG_THRESHOLD
    burnout_div = config.burnout_drag_divisor if config else BURNOUT_DRAG_DIVISOR
    placement = config.placement_boost if config else PLACEMENT_BOOST
    stag_penalty = config.stagnation_penalty if config else STAGNATION_PENALTY
    stag_years = config.stagnation_years_threshold if config else STAGNATION_YEARS
    noise_std = config.random_noise_stddev if config else NOISE_STDDEV
    m_min = config.morale_min if config else 0.0
    m_max = config.morale_max if config else 1.0

    changes: list[ChangeRecord] = []

    for person in company.people:
        if person.departed:
            continue

        old_morale = person.morale
        delta = 0.0

        # 1. Outcome impact
        pid_str = str(person.id)
        if pid_str in recent_outcomes:
            rating = recent_outcomes[pid_str]
            delta += outcome_deltas.get(rating, 0.0)

        # 2. Placement boost
        if pid_str in recent_placements:
            delta += placement

        # 3. Burnout drag
        burnout = compute_burnout_risk(person, quarter_date)
        if burnout > burnout_thresh:
            delta += burnout_drag * ((burnout - burnout_thresh) / burnout_div)

        # 4. Stagnation penalty (same role N+ years)
        active = [a for a in person.assignments if a.end_date is None]
        if active:
            years_in_role = (quarter_date - active[0].start_date).days / 365.25
            if years_in_role > stag_years:
                delta += stag_penalty

        # 5. Mean reversion (pull toward target)
        delta += (mean_target - person.morale) * mean_rate

        # 6. Random jitter (small noise)
        delta += rng.gauss(0.0, noise_std)

        # Apply
        new_morale = max(m_min, min(m_max, person.morale + delta))
        person.morale = round(new_morale, 3)

        if abs(person.morale - old_morale) > 0.005:
            changes.append(
                ChangeRecord(
                    person_id=person.id,
                    person_name=person.name,
                    change_type="morale_change",
                    description=(
                        f"{person.name}: morale {old_morale:.2f} → {person.morale:.2f}"
                    ),
                    old_value=f"{old_morale:.3f}",
                    new_value=f"{person.morale:.3f}",
                )
            )

    return changes
