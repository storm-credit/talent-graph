"""Enhanced quarter advancement that integrates all v0.3 systems.

Order of operations per quarter:
1. Compute outcomes (original logic)
2. Process skill growth/decay
3. Update morale based on outcomes + context
4. Process random events
5. Process attrition checks
6. Update tenure
7. Track all changes
"""

from __future__ import annotations

import random
from datetime import date
from uuid import UUID

from talentgraph.ontology.enums import OutcomeRating
from talentgraph.ontology.models import Assignment, Company, Outcome
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.scoring.engine import FitScoreEngine
from talentgraph.scoring.weights import ScoringWeights
from talentgraph.simulation.attrition import process_attrition
from talentgraph.simulation.growth import process_skill_growth
from talentgraph.simulation.morale import process_morale
from talentgraph.simulation.quarter import (
    OUTCOME_DISTRIBUTIONS,
    RATINGS,
    _performance_bucket,
    _quarter_to_date,
    _sample_outcome,
)
from talentgraph.simulation.random_events import process_random_events
from talentgraph.simulation.state import ChangeRecord, OutcomeRecord, QuarterLabel


def advance_quarter_enhanced(
    company: Company,
    quarter: QuarterLabel,
    weights: ScoringWeights | None = None,
    rng: random.Random | None = None,
    enable_growth: bool = True,
    enable_morale: bool = True,
    enable_attrition: bool = True,
    enable_events: bool = True,
) -> tuple[Company, list[ChangeRecord]]:
    """Enhanced quarter advance with all v0.3 systems.

    Feature flags allow toggling individual systems.
    """
    if rng is None:
        rng = random.Random()

    company = company.model_copy(deep=True)
    engine = FitScoreEngine(company, weights)
    quarter_date = _quarter_to_date(quarter)
    changes: list[ChangeRecord] = []

    role_lookup = {r.id: r for r in company.roles}
    dept_lookup = {d.id: d for d in company.departments}

    # Track outcomes for morale system
    recent_outcomes: dict[str, OutcomeRating] = {}

    # ── Step 1: Generate outcomes (same as v0.2) ──
    for person in company.people:
        if person.departed:
            continue

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

            # Morale affects outcome distribution: shift bucket
            morale_shift = (person.morale - 0.5) * 0.5  # -0.25 to +0.25
            adjusted_perf = result.predicted_performance + morale_shift
            bucket = _performance_bucket(adjusted_perf)
            rating = _sample_outcome(bucket, rng)

            outcome = Outcome(rating=rating, evaluated_at=quarter_date)
            assignment.outcomes.append(outcome)

            role = role_lookup.get(assignment.role_id)
            dept = dept_lookup.get(assignment.department_id)
            role_title = role.title if role else "Unknown"
            dept_name = dept.name if dept else "Unknown"

            recent_outcomes[str(person.id)] = rating

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

    # ── Step 2: Skill growth/decay ──
    if enable_growth:
        growth_changes = process_skill_growth(company, rng)
        changes.extend(growth_changes)

    # ── Step 3: Morale updates ──
    if enable_morale:
        morale_changes = process_morale(
            company, quarter_date, recent_outcomes, set(), rng
        )
        changes.extend(morale_changes)

    # ── Step 4: Random events ──
    if enable_events:
        event_changes, events = process_random_events(company, quarter_date, rng)
        changes.extend(event_changes)

    # ── Step 5: Attrition ──
    if enable_attrition:
        attrition_changes = process_attrition(company, quarter_date, rng)
        changes.extend(attrition_changes)

    # ── Step 6: Increment tenure ──
    for person in company.people:
        if not person.departed:
            active = [a for a in person.assignments if a.end_date is None]
            if active:
                person.tenure_years += 0.25

    return company, changes
