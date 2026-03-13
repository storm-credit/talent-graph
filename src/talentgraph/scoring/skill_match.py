from __future__ import annotations

from uuid import UUID

from talentgraph.ontology.models import Person, Role, Skill


def compute_skill_match(
    person: Person,
    role: Role,
    skill_lookup: dict[UUID, Skill],
) -> float:
    """Score how well a person's skills match a role's requirements.

    For each required skill:
      - If person has it: min(person_level / required_level, 1.0) * weight
      - If person lacks it: 0.0 * weight
    Final score = weighted_sum / max_possible_weighted_sum

    Returns float in [0.0, 1.0]. If role has no requirements, returns 1.0.
    """
    if not role.required_skills:
        return 1.0

    person_skills = {ps.skill_id: ps for ps in person.skills}

    weighted_sum = 0.0
    max_weighted_sum = 0.0

    for req in role.required_skills:
        max_weighted_sum += req.weight

        ps = person_skills.get(req.skill_id)
        if ps is None:
            continue

        match_ratio = min(ps.level.numeric / req.minimum_level.numeric, 1.0)
        weighted_sum += match_ratio * req.weight

    if max_weighted_sum == 0.0:
        return 1.0

    return weighted_sum / max_weighted_sum
