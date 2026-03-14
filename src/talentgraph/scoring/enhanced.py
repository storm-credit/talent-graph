"""Enhanced scoring engine with all v0.3 improvements.

Extends the base FitScoreEngine with:
1. Critical skill gates (hard cap if missing critical skills)
2. Asymmetric level penalties (over-promotion penalized more)
3. Role similarity for historical performance boost
4. Smooth sigmoid burnout curve (no step function)
5. Morale influence on predicted performance
6. Weight normalization enforcement
7. Multiplicative gate option (zero skills → low score regardless)
8. Headcount awareness
9. Team chemistry / culture fit subscores
"""

from __future__ import annotations

import math
from datetime import date
from uuid import UUID

from pydantic import BaseModel

from talentgraph.ontology.models import Company, Department, Person, Role
from talentgraph.scoring.engine import FitResult, FitScoreEngine
from talentgraph.scoring.history import compute_historical_performance
from talentgraph.scoring.skill_match import compute_skill_match
from talentgraph.scoring.weights import ScoringWeights


class EnhancedWeights(ScoringWeights):
    """Extended weights with new scoring dimensions."""

    morale: float = 0.05
    culture_fit: float = 0.05
    # Whether to use multiplicative gating for skill_match
    multiplicative_gate: bool = True


class EnhancedFitResult(FitResult):
    """Extended result with new sub-scores."""

    morale_score: float = 0.0
    culture_fit_score: float = 0.0
    critical_skill_met: bool = True
    headcount_available: bool = True
    role_similarity_boost: float = 0.0


# ── Enhanced sub-scorers ──


def compute_smooth_burnout_staleness(person: Person, ref: date | None = None) -> float:
    """Sigmoid-based staleness (replaces step function).

    Smooth curve centered at 3 years, with gradual ramp from 2-5 years.
    """
    ref = ref or date.today()
    if not person.assignments:
        return 0.1

    latest = max(person.assignments, key=lambda a: a.start_date)
    years = (ref - latest.start_date).days / 365.25

    # Sigmoid: 0 at 0 years, ~0.5 at 3 years, ~0.9 at 5+ years
    return 1.0 / (1.0 + math.exp(-1.5 * (years - 3.0)))


def compute_asymmetric_level_match(person: Person, role: Role, role_lookup: dict) -> float:
    """Asymmetric level penalties.

    Over-promotion (person level << role level): heavy penalty (0.3 per gap)
    Under-placement (person level >> role level): lighter penalty (0.15 per gap)
    """
    if not person.assignments:
        return 0.5

    latest = max(person.assignments, key=lambda a: a.start_date)
    person_level = getattr(latest, "_role_level", None)
    if person_level is None:
        # Try to look up from role_lookup
        role_obj = role_lookup.get(latest.role_id)
        person_level = role_obj.level if role_obj else None
    if person_level is None:
        return 0.5

    gap = role.level - person_level  # positive = promotion, negative = demotion

    if abs(gap) <= 1:
        return 1.0

    if gap > 1:
        # Over-promotion: steep penalty
        penalty = (gap - 1) * 0.3
    else:
        # Under-placement: lighter penalty
        penalty = (abs(gap) - 1) * 0.15

    return max(0.0, 1.0 - penalty)


def compute_role_similarity(role_a: Role, role_b: Role) -> float:
    """Compute similarity between two roles based on shared required skills.

    Returns 0.0-1.0. Roles sharing 80%+ skills are highly similar.
    """
    skills_a = {req.skill_id for req in role_a.required_skills}
    skills_b = {req.skill_id for req in role_b.required_skills}

    if not skills_a or not skills_b:
        return 0.0

    intersection = skills_a & skills_b
    union = skills_a | skills_b

    return len(intersection) / len(union) if union else 0.0


def compute_enhanced_history(
    person: Person,
    target_role: Role,
    all_roles: dict[UUID, Role],
    reference_date: date | None = None,
) -> tuple[float, float]:
    """Historical performance with role-similarity boost.

    Returns (score, similarity_boost_applied).
    """
    ref = reference_date or date.today()
    half_life_days = 730.0

    all_outcomes: list[tuple] = []
    for assignment in person.assignments:
        assignment_role = all_roles.get(assignment.role_id)
        if assignment_role:
            similarity = compute_role_similarity(target_role, assignment_role)
        else:
            similarity = 0.0
        for outcome in assignment.outcomes:
            all_outcomes.append((outcome, similarity))

    if not all_outcomes:
        return 0.5, 0.0

    weighted_sum = 0.0
    weight_total = 0.0
    max_similarity = 0.0

    for outcome, similarity in all_outcomes:
        days_ago = (ref - outcome.evaluated_at).days
        decay = math.exp(-0.693 * days_ago / half_life_days)

        # Role similarity boost: 1.0 (no match) to 1.5 (exact match)
        role_boost = 1.0 + similarity * 0.5
        max_similarity = max(max_similarity, similarity)

        w = decay * role_boost
        normalized_rating = (outcome.rating.numeric - 1) / 4.0
        weighted_sum += normalized_rating * w
        weight_total += w

    if weight_total == 0.0:
        return 0.5, 0.0

    return weighted_sum / weight_total, max_similarity


def check_critical_skills(person: Person, role: Role) -> bool:
    """Check if person has all critical skills for a role."""
    person_skills = {ps.skill_id for ps in person.skills}
    for req in role.required_skills:
        if req.critical and req.skill_id not in person_skills:
            return False
    return True


def compute_culture_fit(person: Person, department: Department) -> float:
    """Score how well a person's traits match department culture.

    Looks for matching trait values between person and department culture_traits.
    Returns 0.0-1.0. No department traits → neutral 0.5.
    """
    if not department.culture_traits:
        return 0.5

    person_trait_values = {(t.trait_type, t.value) for t in person.traits}
    dept_trait_values = {(t.trait_type, t.value) for t in department.culture_traits}

    if not dept_trait_values:
        return 0.5

    matches = person_trait_values & dept_trait_values
    return len(matches) / len(dept_trait_values)


def compute_team_chemistry(
    person: Person, department: Department, company: Company
) -> float:
    """Score team compatibility based on trait diversity.

    Prefers balanced teams. If a department is all one type, adding diversity helps.
    Returns 0.0-1.0. No trait data → neutral 0.5.
    """
    # Find current team members in this department
    team = []
    for p in company.people:
        if p.departed or p.id == person.id:
            continue
        for a in p.assignments:
            if a.end_date is None and a.department_id == department.id:
                team.append(p)
                break

    if not team or not person.traits:
        return 0.5

    # Count collaboration style diversity
    collab_styles: dict[str, int] = {}
    for p in team:
        for t in p.traits:
            if t.trait_type.value == "collaboration_style":
                collab_styles[t.value] = collab_styles.get(t.value, 0) + 1

    if not collab_styles:
        return 0.5

    # Adding a style that's underrepresented scores higher
    person_collab = next(
        (t.value for t in person.traits if t.trait_type.value == "collaboration_style"),
        None,
    )
    if person_collab is None:
        return 0.5

    count = collab_styles.get(person_collab, 0)
    total = sum(collab_styles.values())

    # If this style is rare, good for diversity
    proportion = count / total if total > 0 else 0.0
    return max(0.2, 1.0 - proportion)


def check_headcount(
    role: Role, department: Department, company: Company, exclude_person_id: UUID | None = None
) -> bool:
    """Check if a role has available headcount in a department."""
    if role.max_headcount <= 0:
        return True  # unlimited

    current_count = 0
    for p in company.people:
        if p.departed:
            continue
        if exclude_person_id and p.id == exclude_person_id:
            continue
        for a in p.assignments:
            if (
                a.end_date is None
                and a.role_id == role.id
                and a.department_id == department.id
            ):
                current_count += 1

    return current_count < role.max_headcount


def normalize_weights(weights: EnhancedWeights) -> dict[str, float]:
    """Normalize weights to sum to 1.0."""
    raw = {
        "skill_match": weights.skill_match,
        "historical_performance": weights.historical_performance,
        "level_match": weights.level_match,
        "burnout_risk": weights.burnout_risk,
        "morale": weights.morale,
        "culture_fit": weights.culture_fit,
    }
    total = sum(raw.values())
    if total == 0:
        return {k: 1.0 / len(raw) for k in raw}
    return {k: v / total for k, v in raw.items()}
