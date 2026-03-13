from __future__ import annotations

import math
from datetime import date

from talentgraph.ontology.models import Outcome, Person, Role


def compute_historical_performance(
    person: Person,
    role: Role | None = None,
    reference_date: date | None = None,
) -> float:
    """Score based on historical outcomes with time-weighted decay.

    Recent evaluations carry more weight (exponential decay, half-life = 2 years).
    If role is provided, outcomes from assignments with the same role_id get 1.5x boost.
    No history → 0.5 (neutral prior).

    Returns float in [0.0, 1.0].
    """
    ref = reference_date or date.today()
    half_life_days = 730.0  # ~2 years

    all_outcomes: list[tuple[Outcome, bool]] = []
    for assignment in person.assignments:
        is_same_role = role is not None and assignment.role_id == role.id
        for outcome in assignment.outcomes:
            all_outcomes.append((outcome, is_same_role))

    if not all_outcomes:
        return 0.5

    weighted_sum = 0.0
    weight_total = 0.0

    for outcome, is_same_role in all_outcomes:
        days_ago = (ref - outcome.evaluated_at).days
        decay = math.exp(-0.693 * days_ago / half_life_days)  # ln(2) ≈ 0.693

        role_boost = 1.5 if is_same_role else 1.0
        w = decay * role_boost

        normalized_rating = (outcome.rating.numeric - 1) / 4.0  # map 1-5 → 0-1
        weighted_sum += normalized_rating * w
        weight_total += w

    if weight_total == 0.0:
        return 0.5

    return weighted_sum / weight_total
