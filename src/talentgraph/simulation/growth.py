"""Skill growth and decay system (FM-style player development).

Each quarter:
- Skills USED in current role grow toward potential_level
- Skills NOT USED decay slowly (idle_quarters > 4 → risk of level loss)
- Growth rate depends on: person.learning_rate, tenure, morale
- Growth has diminishing returns near the ceiling
"""

from __future__ import annotations

import random
from uuid import UUID

from talentgraph.config.simulation_config import GrowthConfig
from talentgraph.ontology.enums import SkillLevel
from talentgraph.ontology.models import Company, Person, PersonSkill, Role
from talentgraph.simulation.state import ChangeRecord

# Growth probability per quarter when skill is actively used
# Maps (gap_to_potential) -> base probability of leveling up
GROWTH_PROBABILITY: dict[int, float] = {
    0: 0.00,  # at potential ceiling, no growth
    1: 0.15,  # 1 level below potential: 15% per quarter
    2: 0.25,  # 2 levels below: 25%
    3: 0.35,  # 3 levels below: 35%
    4: 0.40,  # 4 levels below: 40%
}

# Decay: after this many idle quarters, risk of losing a level
DECAY_IDLE_THRESHOLD = 4
DECAY_PROBABILITY_PER_QUARTER = 0.10  # 10% chance per quarter after threshold


def _get_effective_potential(ps: PersonSkill) -> SkillLevel:
    """Return the effective potential level (defaults to current if not set)."""
    if ps.potential_level is not None:
        return ps.potential_level
    return ps.level


def _get_role_skill_ids(person: Person, role_lookup: dict[UUID, Role]) -> set[UUID]:
    """Get skill IDs required by the person's current active role."""
    active = [a for a in person.assignments if a.end_date is None]
    if not active:
        return set()
    role = role_lookup.get(active[0].role_id)
    if role is None:
        return set()
    return {req.skill_id for req in role.required_skills}


def _compute_growth_modifier(
    person: Person,
    config: GrowthConfig | None = None,
) -> float:
    """Modifier based on learning_rate, morale, and tenure.

    Young + high morale → faster growth.
    """
    base = person.learning_rate

    morale_threshold = config.morale_threshold if config else 0.5
    morale_scale = config.morale_growth_scale if config else 0.6
    tenure_slowdown = config.tenure_slowdown_years if config else 5.0
    tenure_rate = config.tenure_slowdown_rate if config else 0.05
    tenure_floor = config.tenure_min_modifier if config else 0.5

    # Morale boost: high morale (0.8+) adds up to 30%
    morale_mod = 1.0 + max(0.0, (person.morale - morale_threshold)) * morale_scale

    # Tenure diminishing returns: growth slows after 5 years
    tenure_mod = 1.0
    if person.tenure_years > tenure_slowdown:
        tenure_mod = max(
            tenure_floor,
            1.0 - (person.tenure_years - tenure_slowdown) * tenure_rate,
        )

    return base * morale_mod * tenure_mod


def process_skill_growth(
    company: Company,
    rng: random.Random,
    config: GrowthConfig | None = None,
) -> list[ChangeRecord]:
    """Process skill growth/decay for all people in the company.

    Mutates company in place. Returns change records.
    """
    # Use config or fall back to module-level constants
    growth_probs = config.growth_probability_map() if config else GROWTH_PROBABILITY
    decay_threshold = (
        config.idle_quarters_before_decay if config else DECAY_IDLE_THRESHOLD
    )
    decay_prob = config.decay_probability if config else DECAY_PROBABILITY_PER_QUARTER
    max_prob = config.max_growth_probability if config else 0.95

    role_lookup = {r.id: r for r in company.roles}
    changes: list[ChangeRecord] = []

    for person in company.people:
        if person.departed:
            continue

        active_skill_ids = _get_role_skill_ids(person, role_lookup)
        growth_mod = _compute_growth_modifier(person, config)

        for ps in person.skills:
            is_active = ps.skill_id in active_skill_ids

            if is_active:
                ps.quarters_active += 1
                ps.quarters_idle = 0
                ps.years_experience += 0.25

                # Try to grow
                potential = _get_effective_potential(ps)
                gap = potential.numeric - ps.level.numeric
                if gap > 0:
                    base_prob = growth_probs.get(gap, 0.40)
                    prob = min(max_prob, base_prob * growth_mod)
                    if rng.random() < prob:
                        old_level = ps.level
                        new_level = ps.level.next_level()
                        if new_level is not None:
                            ps.level = new_level
                            changes.append(
                                ChangeRecord(
                                    person_id=person.id,
                                    person_name=person.name,
                                    change_type="skill_growth",
                                    description=(
                                        f"{person.name}: {_skill_name(ps.skill_id, company)} "
                                        f"{old_level.value} → {new_level.value}"
                                    ),
                                    old_value=old_level.value,
                                    new_value=new_level.value,
                                )
                            )
            else:
                ps.quarters_idle += 1

                # Decay check
                if (
                    ps.quarters_idle >= decay_threshold
                    and ps.level != SkillLevel.NOVICE
                ):
                    if rng.random() < decay_prob:
                        old_level = ps.level
                        new_level = ps.level.prev_level()
                        if new_level is not None:
                            ps.level = new_level
                            changes.append(
                                ChangeRecord(
                                    person_id=person.id,
                                    person_name=person.name,
                                    change_type="skill_decay",
                                    description=(
                                        f"{person.name}: {_skill_name(ps.skill_id, company)} "
                                        f"{old_level.value} → {new_level.value} (idle)"
                                    ),
                                    old_value=old_level.value,
                                    new_value=new_level.value,
                                )
                            )

    return changes


def _skill_name(skill_id: UUID, company: Company) -> str:
    for s in company.skills:
        if s.id == skill_id:
            return s.name
    return "Unknown"
