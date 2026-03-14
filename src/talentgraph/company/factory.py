"""Company factory — generates a full Company from an industry template.

Uses deterministic uuid5 generation for reproducible seeded output.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from uuid import UUID, uuid5

from talentgraph.company.profile import CompanyProfile, GrowthStage, IndustryType
from talentgraph.company.templates import (
    IndustryTemplate,
    get_template,
)
from talentgraph.config.simulation_config import (
    AttritionConfig,
    EventConfig,
    GrowthConfig,
    MoraleConfig,
    SimulationConfig,
)
from talentgraph.ontology.enums import OutcomeRating, SkillCategory, SkillLevel, TraitType
from talentgraph.ontology.models import (
    Assignment,
    Company,
    Department,
    Outcome,
    Person,
    PersonSkill,
    Role,
    RoleSkillRequirement,
    Skill,
    Trait,
)

# Namespace for deterministic UUID generation
_NS = UUID("b4e3f1a2-7c8d-4e5f-9a0b-1c2d3e4f5a6b")

# Numeric → SkillLevel mapping (ontology is read-only, so we map here)
_NUMERIC_TO_LEVEL = {
    1: SkillLevel.NOVICE,
    2: SkillLevel.BEGINNER,
    3: SkillLevel.INTERMEDIATE,
    4: SkillLevel.ADVANCED,
    5: SkillLevel.EXPERT,
}

# Skill level distribution weights by growth stage
_SKILL_LEVEL_WEIGHTS: dict[GrowthStage, list[tuple[SkillLevel, float]]] = {
    GrowthStage.EARLY: [
        (SkillLevel.NOVICE, 0.15),
        (SkillLevel.BEGINNER, 0.35),
        (SkillLevel.INTERMEDIATE, 0.30),
        (SkillLevel.ADVANCED, 0.15),
        (SkillLevel.EXPERT, 0.05),
    ],
    GrowthStage.GROWTH: [
        (SkillLevel.NOVICE, 0.10),
        (SkillLevel.BEGINNER, 0.25),
        (SkillLevel.INTERMEDIATE, 0.35),
        (SkillLevel.ADVANCED, 0.20),
        (SkillLevel.EXPERT, 0.10),
    ],
    GrowthStage.MATURE: [
        (SkillLevel.NOVICE, 0.05),
        (SkillLevel.BEGINNER, 0.15),
        (SkillLevel.INTERMEDIATE, 0.30),
        (SkillLevel.ADVANCED, 0.30),
        (SkillLevel.EXPERT, 0.20),
    ],
    GrowthStage.ENTERPRISE: [
        (SkillLevel.NOVICE, 0.05),
        (SkillLevel.BEGINNER, 0.10),
        (SkillLevel.INTERMEDIATE, 0.25),
        (SkillLevel.ADVANCED, 0.35),
        (SkillLevel.EXPERT, 0.25),
    ],
}

# Outcome rating distribution weights by skill level
_OUTCOME_WEIGHTS: dict[str, list[tuple[OutcomeRating, float]]] = {
    "high": [
        (OutcomeRating.EXCEPTIONAL, 0.20),
        (OutcomeRating.EXCEEDS, 0.40),
        (OutcomeRating.MEETS, 0.30),
        (OutcomeRating.BELOW, 0.08),
        (OutcomeRating.UNSATISFACTORY, 0.02),
    ],
    "mid": [
        (OutcomeRating.EXCEPTIONAL, 0.05),
        (OutcomeRating.EXCEEDS, 0.25),
        (OutcomeRating.MEETS, 0.45),
        (OutcomeRating.BELOW, 0.20),
        (OutcomeRating.UNSATISFACTORY, 0.05),
    ],
    "low": [
        (OutcomeRating.EXCEPTIONAL, 0.02),
        (OutcomeRating.EXCEEDS, 0.08),
        (OutcomeRating.MEETS, 0.30),
        (OutcomeRating.BELOW, 0.40),
        (OutcomeRating.UNSATISFACTORY, 0.20),
    ],
}


def _weighted_choice(rng: random.Random, items: list[tuple], key=None):
    """Weighted random choice."""
    values = [item[0] for item in items]
    weights = [item[1] for item in items]
    return rng.choices(values, weights=weights, k=1)[0]


def create_company_from_template(
    profile: CompanyProfile,
    seed: int = 42,
) -> Company:
    """Generate a complete Company from a CompanyProfile.

    Uses deterministic random generation for reproducibility.
    """
    rng = random.Random(seed)
    template = get_template(profile.industry)

    # 1. Create skills
    skill_map: dict[str, Skill] = {}
    skills: list[Skill] = []
    for st in template.skills:
        skill_id = uuid5(_NS, f"{profile.name}:skill:{st.name}")
        skill = Skill(
            id=skill_id,
            name=st.name,
            category=st.category,
            description=st.description,
        )
        skills.append(skill)
        skill_map[st.name] = skill

    # 2. Create roles
    role_map: dict[str, Role] = {}
    all_roles: list[Role] = []
    for rt in template.roles:
        role_id = uuid5(_NS, f"{profile.name}:role:{rt.title}")
        req_skills = []
        for rsr in rt.required_skills:
            if rsr.skill_name in skill_map:
                req_skills.append(
                    RoleSkillRequirement(
                        skill_id=skill_map[rsr.skill_name].id,
                        minimum_level=_NUMERIC_TO_LEVEL[rsr.min_level],
                        weight=rsr.weight,
                        critical=rsr.critical,
                    )
                )
        role = Role(
            id=role_id,
            title=rt.title,
            level=rt.level,
            required_skills=req_skills,
            max_headcount=rt.max_headcount,
        )
        all_roles.append(role)
        role_map[rt.title] = role

    # 3. Create departments
    departments: list[Department] = []
    dept_roles: dict[str, list[UUID]] = {}  # dept_name → role_ids
    for dt in template.departments:
        dept_id = uuid5(_NS, f"{profile.name}:dept:{dt.name}")
        role_ids = [role_map[rt].id for rt in dt.role_titles if rt in role_map]
        traits = [
            Trait(
                id=uuid5(_NS, f"{profile.name}:trait:{dt.name}:{t}"),
                trait_type=TraitType.CULTURE,
                name=t,
                value=t,
            )
            for t in dt.culture_traits
        ]
        dept = Department(
            id=dept_id,
            name=dt.name,
            roles=role_ids,
            culture_traits=traits,
        )
        departments.append(dept)
        dept_roles[dt.name] = role_ids

    # 4. Create people
    people = _generate_people(
        template=template,
        profile=profile,
        skill_map=skill_map,
        role_map=role_map,
        departments=departments,
        dept_roles=dept_roles,
        rng=rng,
    )

    return Company(
        name=profile.name,
        departments=departments,
        roles=all_roles,
        skills=skills,
        people=people,
    )


def _generate_people(
    template: IndustryTemplate,
    profile: CompanyProfile,
    skill_map: dict[str, Skill],
    role_map: dict[str, Role],
    departments: list[Department],
    dept_roles: dict[str, list[UUID]],
    rng: random.Random,
) -> list[Person]:
    """Generate N people with diverse profiles and assignments."""
    num = profile.num_people
    first_names = template.first_names or ["Person"]
    last_names = template.last_names or ["Unknown"]

    # Build (dept, role_id) assignment pool
    assignment_pool: list[tuple[Department, Role]] = []
    for dept in departments:
        for role_id in dept.roles:
            role = next((r for r in role_map.values() if r.id == role_id), None)
            if role:
                for _ in range(role.max_headcount):
                    assignment_pool.append((dept, role))
    rng.shuffle(assignment_pool)

    people: list[Person] = []
    used_names: set[str] = set()

    for i in range(num):
        # Generate unique name
        for _ in range(100):
            fn = rng.choice(first_names)
            ln = rng.choice(last_names)
            name = f"{fn} {ln}"
            if name not in used_names:
                used_names.add(name)
                break
        else:
            name = f"Person {i + 1}"

        person_id = uuid5(_NS, f"{profile.name}:person:{name}:{i}")

        # Tenure varies by growth stage
        if profile.growth_stage == GrowthStage.EARLY:
            tenure = round(rng.uniform(0.25, 3.0), 1)
        elif profile.growth_stage == GrowthStage.GROWTH:
            tenure = round(rng.uniform(0.5, 5.0), 1)
        elif profile.growth_stage == GrowthStage.MATURE:
            tenure = round(rng.uniform(1.0, 10.0), 1)
        else:
            tenure = round(rng.uniform(1.0, 15.0), 1)

        # Morale, potential, learning_rate
        morale = round(rng.uniform(0.4, 0.9), 2)
        potential = round(rng.uniform(0.4, 0.95), 2)
        learning_rate = round(rng.uniform(0.6, 1.5), 2)

        # Generate skills (give each person 4-7 skills from the template)
        num_skills = min(len(template.skills), rng.randint(4, 7))
        selected_skills = rng.sample(template.skills, num_skills)
        person_skills: list[PersonSkill] = []
        level_weights = _SKILL_LEVEL_WEIGHTS.get(
            profile.growth_stage, _SKILL_LEVEL_WEIGHTS[GrowthStage.GROWTH]
        )

        for st in selected_skills:
            skill = skill_map[st.name]
            level = _weighted_choice(rng, level_weights)
            # Potential is level or higher
            potential_lvl = level
            for _ in range(rng.randint(0, 2)):
                nxt = potential_lvl.next_level()
                if nxt:
                    potential_lvl = nxt

            years_exp = round(level.numeric * rng.uniform(0.5, 1.5), 1)
            person_skills.append(
                PersonSkill(
                    skill_id=skill.id,
                    level=level,
                    years_experience=years_exp,
                    potential_level=potential_lvl,
                    quarters_active=int(years_exp * 4),
                    quarters_idle=0,
                )
            )

        # Generate assignment (if pool available)
        assignments: list[Assignment] = []
        if i < len(assignment_pool):
            dept, role = assignment_pool[i]
            start = date.today() - timedelta(days=int(tenure * 365))
            assignment = Assignment(
                person_id=person_id,
                role_id=role.id,
                department_id=dept.id,
                start_date=start,
                end_date=None,
                outcomes=_generate_outcomes(rng, tenure, person_skills),
            )
            assignments.append(assignment)

        person = Person(
            id=person_id,
            name=name,
            skills=person_skills,
            traits=[],
            assignments=assignments,
            tenure_years=tenure,
            morale=morale,
            potential=potential,
            learning_rate=learning_rate,
        )
        people.append(person)

    return people


def _generate_outcomes(
    rng: random.Random,
    tenure: float,
    skills: list[PersonSkill],
) -> list[Outcome]:
    """Generate plausible historical outcomes based on tenure and skill levels."""
    num_quarters = max(1, int(tenure * 4) - 1)
    num_quarters = min(num_quarters, 8)  # cap at 2 years of history

    # Determine outcome quality based on average skill level
    avg_level = sum(ps.level.numeric for ps in skills) / max(len(skills), 1)
    if avg_level >= 3.5:
        bucket = "high"
    elif avg_level >= 2.5:
        bucket = "mid"
    else:
        bucket = "low"

    weights = _OUTCOME_WEIGHTS[bucket]
    outcomes: list[Outcome] = []
    base_date = date.today() - timedelta(days=int(tenure * 365))

    for q in range(num_quarters):
        eval_date = base_date + timedelta(days=(q + 1) * 90)
        rating = _weighted_choice(rng, weights)
        outcomes.append(Outcome(rating=rating, evaluated_at=eval_date))

    return outcomes


def build_config_for_profile(profile: CompanyProfile) -> SimulationConfig:
    """Build a SimulationConfig with industry-specific overrides."""
    template = get_template(profile.industry)
    overrides = template.config_overrides

    growth_kwargs = {}
    morale_kwargs = {}
    attrition_kwargs = {}
    event_kwargs = {}

    if overrides.attrition_base_rate is not None:
        attrition_kwargs["base_rate"] = overrides.attrition_base_rate
    if overrides.growth_gap_1_prob is not None:
        growth_kwargs["gap_1_growth_prob"] = overrides.growth_gap_1_prob
    if overrides.morale_mean_reversion_target is not None:
        morale_kwargs["mean_reversion_target"] = overrides.morale_mean_reversion_target
    if overrides.morale_stagnation_penalty is not None:
        morale_kwargs["stagnation_penalty"] = overrides.morale_stagnation_penalty
    if overrides.event_reorg_probability is not None:
        event_kwargs["reorg_probability"] = overrides.event_reorg_probability

    return SimulationConfig(
        growth=GrowthConfig(**growth_kwargs) if growth_kwargs else GrowthConfig(),
        morale=MoraleConfig(**morale_kwargs) if morale_kwargs else MoraleConfig(),
        attrition=AttritionConfig(**attrition_kwargs) if attrition_kwargs else AttritionConfig(),
        events=EventConfig(**event_kwargs) if event_kwargs else EventConfig(),
    )
