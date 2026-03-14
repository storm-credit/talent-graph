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
BURNOUT_MORALE_DRAG = -0.03  # per 0.1 burnout above 0.3
PLACEMENT_BOOST = 0.10  # morale boost from a new role
STAGNATION_PENALTY = -0.02  # per quarter of high staleness


def process_morale(
    company: Company,
    quarter_date: date,
    recent_outcomes: dict[str, OutcomeRating] | None = None,
    recent_placements: set[str] | None = None,
    rng: random.Random | None = None,
) -> list[ChangeRecord]:
    """Update morale for all people. Mutates company in place.

    Args:
        recent_outcomes: {person_id_str: OutcomeRating} from this quarter
        recent_placements: set of person_id_str who got new roles this quarter
    """
    if rng is None:
        rng = random.Random()
    if recent_outcomes is None:
        recent_outcomes = {}
    if recent_placements is None:
        recent_placements = set()

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
            delta += OUTCOME_MORALE_DELTA.get(rating, 0.0)

        # 2. Placement boost
        if pid_str in recent_placements:
            delta += PLACEMENT_BOOST

        # 3. Burnout drag
        burnout = compute_burnout_risk(person, quarter_date)
        if burnout > 0.3:
            delta += BURNOUT_MORALE_DRAG * ((burnout - 0.3) / 0.1)

        # 4. Stagnation penalty (same role 3+ years)
        active = [a for a in person.assignments if a.end_date is None]
        if active:
            years_in_role = (quarter_date - active[0].start_date).days / 365.25
            if years_in_role > 3.0:
                delta += STAGNATION_PENALTY

        # 5. Mean reversion (pull toward 0.5)
        delta += (0.5 - person.morale) * MEAN_REVERSION_RATE

        # 6. Random jitter (small noise)
        delta += rng.gauss(0.0, 0.01)

        # Apply
        new_morale = max(0.0, min(1.0, person.morale + delta))
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
