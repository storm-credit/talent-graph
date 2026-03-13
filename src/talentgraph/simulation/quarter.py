"""Core quarter simulation logic: advance and placement."""

from __future__ import annotations

import random
from datetime import date
from uuid import UUID

from talentgraph.ontology.enums import OutcomeRating
from talentgraph.ontology.models import Assignment, Company, Outcome
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.scoring.engine import FitScoreEngine
from talentgraph.scoring.weights import ScoringWeights
from talentgraph.simulation.events import OutcomeEvent, PlacementEvent
from talentgraph.simulation.state import ChangeRecord, OutcomeRecord, QuarterLabel

# Probability distributions for outcome ratings based on predicted performance bucket.
# Index 0 = unsatisfactory, index 4 = exceptional
OUTCOME_DISTRIBUTIONS: dict[int, list[float]] = {
    1: [0.40, 0.35, 0.20, 0.05, 0.00],
    2: [0.15, 0.35, 0.35, 0.10, 0.05],
    3: [0.05, 0.15, 0.50, 0.25, 0.05],
    4: [0.02, 0.08, 0.25, 0.40, 0.25],
    5: [0.00, 0.05, 0.15, 0.35, 0.45],
}

RATINGS = [
    OutcomeRating.UNSATISFACTORY,
    OutcomeRating.BELOW,
    OutcomeRating.MEETS,
    OutcomeRating.EXCEEDS,
    OutcomeRating.EXCEPTIONAL,
]


def _performance_bucket(predicted: float) -> int:
    """Map predicted performance [1.0, 5.0] to bucket 1-5."""
    return max(1, min(5, round(predicted)))


def _sample_outcome(bucket: int, rng: random.Random) -> OutcomeRating:
    """Sample an outcome rating from the probability distribution for a bucket."""
    probs = OUTCOME_DISTRIBUTIONS[bucket]
    return rng.choices(RATINGS, weights=probs, k=1)[0]


def _quarter_to_date(q: QuarterLabel) -> date:
    """Convert quarter to the last day of that quarter."""
    month = q.quarter * 3
    if month == 12:
        return date(q.year, 12, 31)
    return date(q.year, month + 1, 1).replace(day=1) - __import__("datetime").timedelta(days=1)


def advance_quarter(
    company: Company,
    quarter: QuarterLabel,
    weights: ScoringWeights | None = None,
    rng: random.Random | None = None,
) -> tuple[Company, list[ChangeRecord]]:
    """
    Advance the company state by one quarter.

    For each person with an active assignment:
    1. Compute predicted performance via FitScoreEngine
    2. Sample an outcome rating from probability distribution
    3. Add outcome to assignment, increment tenure

    Returns (updated_company, list_of_changes).
    """
    if rng is None:
        rng = random.Random()

    company = company.model_copy(deep=True)
    engine = FitScoreEngine(company, weights)
    quarter_date = _quarter_to_date(quarter)
    changes: list[ChangeRecord] = []

    role_lookup = {r.id: r for r in company.roles}
    dept_lookup = {d.id: d for d in company.departments}

    for person in company.people:
        old_burnout = compute_burnout_risk(person)

        active_assignments = [a for a in person.assignments if a.end_date is None]
        if not active_assignments:
            continue

        results = engine.evaluate_person(person.id)
        result_lookup = {(r.role_id, r.department_id): r for r in results}

        for assignment in active_assignments:
            result = result_lookup.get((assignment.role_id, assignment.department_id))
            if result is None:
                continue

            bucket = _performance_bucket(result.predicted_performance)
            rating = _sample_outcome(bucket, rng)

            outcome = Outcome(rating=rating, evaluated_at=quarter_date)
            assignment.outcomes.append(outcome)

            role = role_lookup.get(assignment.role_id)
            dept = dept_lookup.get(assignment.department_id)
            role_title = role.title if role else "Unknown"
            dept_name = dept.name if dept else "Unknown"

            changes.append(
                OutcomeRecord(
                    person_id=person.id,
                    person_name=person.name,
                    change_type="outcome",
                    description=f"{person.name}: {rating.value} in {role_title} (predicted {result.predicted_performance:.1f})",
                    old_value=None,
                    new_value=rating.value,
                    role_title=role_title,
                    department_name=dept_name,
                    rating=rating,
                    predicted_performance=result.predicted_performance,
                )
            )

        # Increment tenure
        person.tenure_years += 0.25

        # Track burnout change
        new_burnout = compute_burnout_risk(person, quarter_date)
        if abs(new_burnout - old_burnout) > 0.01:
            changes.append(
                ChangeRecord(
                    person_id=person.id,
                    person_name=person.name,
                    change_type="burnout_change",
                    description=f"{person.name}: burnout risk {old_burnout:.2f} → {new_burnout:.2f}",
                    old_value=f"{old_burnout:.3f}",
                    new_value=f"{new_burnout:.3f}",
                )
            )

    return company, changes


def place_person(
    company: Company,
    person_id: UUID,
    role_id: UUID,
    department_id: UUID,
    quarter: QuarterLabel,
) -> tuple[Company, PlacementEvent]:
    """
    Place a person in a new role/department. Ends their current active assignment.

    Returns (updated_company, placement_event).
    """
    company = company.model_copy(deep=True)
    person = next((p for p in company.people if p.id == person_id), None)
    if person is None:
        raise ValueError(f"Person not found: {person_id}")

    role = next((r for r in company.roles if r.id == role_id), None)
    if role is None:
        raise ValueError(f"Role not found: {role_id}")

    dept = next((d for d in company.departments if d.id == department_id), None)
    if dept is None:
        raise ValueError(f"Department not found: {department_id}")

    start_date = _quarter_to_date(quarter)
    prev_role_id = None
    prev_role_title = None

    # End current active assignments
    for a in person.assignments:
        if a.end_date is None:
            a.end_date = start_date
            prev_role = next((r for r in company.roles if r.id == a.role_id), None)
            prev_role_id = a.role_id
            prev_role_title = prev_role.title if prev_role else None

    # Create new assignment
    new_assignment = Assignment(
        person_id=person_id,
        role_id=role_id,
        department_id=department_id,
        start_date=start_date,
    )
    person.assignments.append(new_assignment)

    event = PlacementEvent(
        person_id=person_id,
        person_name=person.name,
        role_id=role_id,
        role_title=role.title,
        department_id=department_id,
        department_name=dept.name,
        previous_role_id=prev_role_id,
        previous_role_title=prev_role_title,
    )

    return company, event
