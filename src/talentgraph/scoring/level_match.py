from __future__ import annotations

from talentgraph.ontology.models import Person, Role


def compute_level_match(person: Person, role: Role) -> float:
    """Score seniority fit between person and target role.

    Infers person's current level from their most recent assignment's role level.
    - Exact match or 1 level up → 1.0
    - Each additional level gap → -0.2 penalty (both over and under placement)
    - No assignment history → 0.5 (neutral)

    Returns float in [0.0, 1.0].
    """
    if not person.assignments:
        return 0.5

    latest = max(person.assignments, key=lambda a: a.start_date)
    person_level = _infer_level_from_assignment(latest)

    if person_level is None:
        return 0.5

    gap = abs(role.level - person_level)

    if gap <= 1:
        return 1.0

    penalty = (gap - 1) * 0.2
    return max(0.0, 1.0 - penalty)


def _infer_level_from_assignment(assignment) -> int | None:
    """Return the role level from an assignment. Requires the assignment to carry role context."""
    # In v0.1, we store the level lookup externally via the engine.
    # This function is a hook for the engine to inject level data.
    return getattr(assignment, "_role_level", None)
