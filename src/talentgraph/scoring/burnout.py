from __future__ import annotations

from datetime import date

from talentgraph.ontology.models import Person


def compute_burnout_risk(
    person: Person,
    reference_date: date | None = None,
) -> float:
    """Estimate burnout risk from observable signals.

    Factors:
    1. Role staleness: years in most recent role without change (> 3yr increases risk)
    2. Performance decline: if recent outcomes trend downward
    3. No history → low base risk (0.1)

    Returns float in [0.0, 1.0] where 1.0 = highest risk.
    """
    ref = reference_date or date.today()

    if not person.assignments:
        return 0.1

    staleness_risk = _compute_staleness(person, ref)
    decline_risk = _compute_performance_decline(person)

    combined = 0.6 * staleness_risk + 0.4 * decline_risk
    return min(1.0, max(0.0, combined))


def _compute_staleness(person: Person, ref: date) -> float:
    """Risk from being in the same role too long."""
    latest = max(person.assignments, key=lambda a: a.start_date)
    years_in_role = (ref - latest.start_date).days / 365.25

    if years_in_role <= 2.0:
        return 0.0
    elif years_in_role <= 3.0:
        return 0.2
    elif years_in_role <= 5.0:
        return 0.5
    else:
        return 0.8


def _compute_performance_decline(person: Person) -> float:
    """Risk from declining performance trend."""
    all_outcomes = []
    for assignment in person.assignments:
        for outcome in assignment.outcomes:
            all_outcomes.append(outcome)

    if len(all_outcomes) < 2:
        return 0.0

    sorted_outcomes = sorted(all_outcomes, key=lambda o: o.evaluated_at)

    mid = len(sorted_outcomes) // 2
    first_half_avg = sum(o.rating.numeric for o in sorted_outcomes[:mid]) / mid
    second_half_avg = sum(o.rating.numeric for o in sorted_outcomes[mid:]) / (
        len(sorted_outcomes) - mid
    )

    decline = first_half_avg - second_half_avg
    if decline <= 0:
        return 0.0

    return min(1.0, decline / 2.0)
