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

from talentgraph.ontology.models import Company, Person
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.state import ChangeRecord

BASE_ATTRITION_RATE = 0.02
BURNOUT_FACTOR = 0.15
MORALE_FACTOR = 0.12
MAX_QUARTERLY_ATTRITION = 0.30


def _tenure_multiplier(tenure_years: float) -> float:
    """U-shaped: new hires and long-tenured employees leave more.

    < 1 year: 1.5x (didn't fit)
    1-5 years: 1.0x (stable)
    5-8 years: 1.2x (looking for growth)
    8+ years: 1.5x (burned out / maxed out)
    """
    if tenure_years < 1.0:
        return 1.5
    elif tenure_years <= 5.0:
        return 1.0
    elif tenure_years <= 8.0:
        return 1.0 + (tenure_years - 5.0) * 0.067  # ramps to ~1.2
    else:
        return 1.5


def compute_attrition_probability(
    person: Person,
    reference_date: date | None = None,
) -> float:
    """Compute probability of departure this quarter."""
    if person.departed:
        return 0.0

    ref = reference_date or date.today()
    burnout = compute_burnout_risk(person, ref)

    risk = BASE_ATTRITION_RATE
    risk += BURNOUT_FACTOR * max(0.0, burnout - 0.3)
    risk += MORALE_FACTOR * max(0.0, 0.5 - person.morale)
    risk *= _tenure_multiplier(person.tenure_years)

    return min(MAX_QUARTERLY_ATTRITION, max(0.0, risk))


def process_attrition(
    company: Company,
    quarter_date: date,
    rng: random.Random,
) -> list[ChangeRecord]:
    """Process potential departures. Mutates company in place.

    Returns list of departure change records.
    """
    changes: list[ChangeRecord] = []

    for person in company.people:
        if person.departed:
            continue

        prob = compute_attrition_probability(person, quarter_date)
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
