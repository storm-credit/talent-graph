"""Attrition / retention model.

Each quarter, compute departure probability per person.
High burnout + low morale + long tenure = higher chance of leaving.

Attrition probability formula:
  base_risk = 0.02 (2% base quarterly turnover)
  risk += burnout_factor * max(0, burnout - 0.3)
  risk += morale_factor * max(0, 0.5 - morale)
  risk *= tenure_multiplier (U-shaped: high for <1y and >8y)
  risk = clamp(0, 0.30)  # max 30% per quarter
"""

from __future__ import annotations

import random
from datetime import date

from talentgraph.config.simulation_config import AttritionConfig
from talentgraph.ontology.models import Company, Person
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.state import ChangeRecord

BASE_ATTRITION_RATE = 0.02
BURNOUT_FACTOR = 0.15
BURNOUT_THRESHOLD = 0.3
MORALE_FACTOR = 0.12
MORALE_THRESHOLD = 0.5
MAX_QUARTERLY_ATTRITION = 0.30


def _tenure_multiplier(
    tenure_years: float,
    config: AttritionConfig | None = None,
) -> float:
    """U-shaped: new hires and long-tenured employees leave more.

    < 1 year: 1.5x (didn't fit)
    1-5 years: 1.0x (stable)
    5-8 years: 1.2x (looking for growth)
    8+ years: 1.5x (burned out / maxed out)
    """
    early_yrs = config.early_tenure_years if config else 1.0
    early_mult = config.early_tenure_multiplier if config else 1.5
    mid_end = config.mid_tenure_years[1] if config else 5.0
    mid_mult = config.mid_tenure_multiplier if config else 1.0
    ramp_end = config.late_ramp_years[1] if config else 8.0
    ramp_rate = config.late_ramp_rate if config else 0.067
    max_mult = config.max_tenure_multiplier if config else 1.5

    if tenure_years < early_yrs:
        return early_mult
    elif tenure_years <= mid_end:
        return mid_mult
    elif tenure_years <= ramp_end:
        return mid_mult + (tenure_years - mid_end) * ramp_rate  # ramps to ~1.2
    else:
        return max_mult


def compute_attrition_probability(
    person: Person,
    reference_date: date | None = None,
    config: AttritionConfig | None = None,
) -> float:
    """Compute probability of departure this quarter."""
    if person.departed:
        return 0.0

    base = config.base_rate if config else BASE_ATTRITION_RATE
    b_factor = config.burnout_coefficient if config else BURNOUT_FACTOR
    b_thresh = config.burnout_threshold if config else BURNOUT_THRESHOLD
    m_factor = config.morale_coefficient if config else MORALE_FACTOR
    m_thresh = config.morale_threshold if config else MORALE_THRESHOLD
    max_prob = config.max_attrition_probability if config else MAX_QUARTERLY_ATTRITION

    ref = reference_date or date.today()
    burnout = compute_burnout_risk(person, ref)

    risk = base
    risk += b_factor * max(0.0, burnout - b_thresh)
    risk += m_factor * max(0.0, m_thresh - person.morale)
    risk *= _tenure_multiplier(person.tenure_years, config)

    return min(max_prob, max(0.0, risk))


def process_attrition(
    company: Company,
    quarter_date: date,
    rng: random.Random,
    config: AttritionConfig | None = None,
) -> list[ChangeRecord]:
    """Process potential departures. Mutates company in place.

    Returns list of departure change records.
    """
    changes: list[ChangeRecord] = []

    for person in company.people:
        if person.departed:
            continue

        prob = compute_attrition_probability(person, quarter_date, config)
        if rng.random() < prob:
            person.departed = True
            # End all active assignments
            for a in person.assignments:
                if a.end_date is None:
                    a.end_date = quarter_date

            changes.append(
                ChangeRecord(
                    person_id=person.id,
                    person_name=person.name,
                    change_type="departure",
                    description=(
                        f"{person.name} departed (prob={prob:.1%}, "
                        f"morale={person.morale:.2f}, tenure={person.tenure_years:.1f}y)"
                    ),
                    old_value="active",
                    new_value="departed",
                )
            )

    return changes
