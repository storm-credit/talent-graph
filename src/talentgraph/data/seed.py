"""Generate deterministic sample data for TalentGraph demos and testing.

v0.3: Added potential_level (CA/PA), collaboration_style traits,
      critical skills, max_headcount, culture_traits, morale/potential/learning_rate.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID, uuid5

from talentgraph.ontology.enums import (
    OutcomeRating,
    SkillCategory,
    SkillLevel,
    TraitType,
)
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

# Deterministic namespace for uuid5
NS = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def _id(key: str) -> UUID:
    return uuid5(NS, key)


def create_sample_company() -> Company:
    """Build Acme Corp with 8 skills, 6 roles, 4 departments, 5 people."""

    # ── Skills ──
    skills = [
        Skill(id=_id("skill:python"), name="Python", category=SkillCategory.TECHNICAL),
        Skill(id=_id("skill:sql"), name="SQL", category=SkillCategory.TECHNICAL),
        Skill(id=_id("skill:pm"), name="Project Management", category=SkillCategory.LEADERSHIP),
        Skill(
            id=_id("skill:data_analysis"),
            name="Data Analysis",
            category=SkillCategory.ANALYTICAL,
        ),
        Skill(
            id=_id("skill:communication"),
            name="Communication",
            category=SkillCategory.COMMUNICATION,
        ),
        Skill(id=_id("skill:ml"), name="Machine Learning", category=SkillCategory.TECHNICAL),
        Skill(
            id=_id("skill:finance"),
            name="Financial Modeling",
            category=SkillCategory.DOMAIN,
        ),
        Skill(
            id=_id("skill:leadership"),
            name="Team Leadership",
            category=SkillCategory.LEADERSHIP,
        ),
    ]
    sk = {s.name: s.id for s in skills}

    # ── Roles (v0.3: critical skills + max_headcount) ──
    roles = [
        Role(
            id=_id("role:sr_data_eng"),
            title="Senior Data Engineer",
            level=5,
            max_headcount=3,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Python"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=5.0,
                    critical=True,
                ),
                RoleSkillRequirement(
                    skill_id=sk["SQL"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=4.0,
                    critical=True,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Data Analysis"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=3.0,
                ),
            ],
        ),
        Role(
            id=_id("role:data_scientist"),
            title="Data Scientist",
            level=5,
            max_headcount=2,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Python"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=4.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Machine Learning"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=5.0,
                    critical=True,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Data Analysis"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=4.0,
                ),
            ],
        ),
        Role(
            id=_id("role:eng_manager"),
            title="Engineering Manager",
            level=7,
            max_headcount=1,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Team Leadership"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=5.0,
                    critical=True,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Project Management"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=4.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Communication"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=3.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Python"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=2.0,
                ),
            ],
        ),
        Role(
            id=_id("role:jr_data_eng"),
            title="Junior Data Engineer",
            level=3,
            max_headcount=5,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Python"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=4.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["SQL"],
                    minimum_level=SkillLevel.BEGINNER,
                    weight=3.0,
                ),
            ],
        ),
        Role(
            id=_id("role:financial_analyst"),
            title="Financial Analyst",
            level=4,
            max_headcount=2,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Financial Modeling"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=5.0,
                    critical=True,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Data Analysis"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=3.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["SQL"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=2.0,
                ),
            ],
        ),
        Role(
            id=_id("role:jr_data_scientist"),
            title="Junior Data Scientist",
            level=3,
            max_headcount=4,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Python"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=4.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Machine Learning"],
                    minimum_level=SkillLevel.BEGINNER,
                    weight=3.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Data Analysis"],
                    minimum_level=SkillLevel.BEGINNER,
                    weight=3.0,
                ),
            ],
        ),
    ]
    rl = {r.title: r.id for r in roles}

    # ── Departments (v0.3: culture_traits) ──
    departments = [
        Department(
            id=_id("dept:data_eng"),
            name="Data Engineering",
            roles=[rl["Senior Data Engineer"], rl["Junior Data Engineer"]],
            culture_traits=[
                Trait(
                    id=_id("culture:data_eng:collab"),
                    trait_type=TraitType.CULTURE,
                    name="Team Culture",
                    value="collaborative",
                ),
                Trait(
                    id=_id("culture:data_eng:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="deep_focus",
                ),
            ],
        ),
        Department(
            id=_id("dept:data_sci"),
            name="Data Science",
            roles=[rl["Data Scientist"], rl["Junior Data Scientist"]],
            culture_traits=[
                Trait(
                    id=_id("culture:data_sci:collab"),
                    trait_type=TraitType.CULTURE,
                    name="Team Culture",
                    value="innovative",
                ),
                Trait(
                    id=_id("culture:data_sci:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="experimental",
                ),
            ],
        ),
        Department(
            id=_id("dept:eng_mgmt"),
            name="Engineering Management",
            roles=[rl["Engineering Manager"]],
            culture_traits=[
                Trait(
                    id=_id("culture:eng_mgmt:collab"),
                    trait_type=TraitType.CULTURE,
                    name="Team Culture",
                    value="collaborative",
                ),
                Trait(
                    id=_id("culture:eng_mgmt:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="structured",
                ),
            ],
        ),
        Department(
            id=_id("dept:finance"),
            name="Finance",
            roles=[rl["Financial Analyst"]],
            culture_traits=[
                Trait(
                    id=_id("culture:finance:collab"),
                    trait_type=TraitType.CULTURE,
                    name="Team Culture",
                    value="analytical",
                ),
                Trait(
                    id=_id("culture:finance:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="structured",
                ),
            ],
        ),
    ]
    dp = {d.name: d.id for d in departments}

    # ── People (v0.3: potential_level, morale, potential, learning_rate, collaboration traits) ──
    people = [
        # Alice: Data engineer, strong technical skills, good performance trajectory
        # High potential — can grow to Expert in most technical skills
        Person(
            id=_id("person:alice"),
            name="Alice Chen",
            tenure_years=5.5,
            morale=0.75,
            potential=0.85,
            learning_rate=1.2,
            skills=[
                PersonSkill(
                    skill_id=sk["Python"],
                    level=SkillLevel.EXPERT,
                    years_experience=8.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["SQL"],
                    level=SkillLevel.ADVANCED,
                    years_experience=6.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"],
                    level=SkillLevel.ADVANCED,
                    years_experience=5.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["Machine Learning"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=2.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["Team Leadership"],
                    level=SkillLevel.BEGINNER,
                    years_experience=1.0,
                    potential_level=SkillLevel.INTERMEDIATE,
                ),
            ],
            traits=[
                Trait(
                    id=_id("trait:alice:collab"),
                    trait_type=TraitType.COLLABORATION_STYLE,
                    name="Collaboration",
                    value="independent",
                ),
                Trait(
                    id=_id("trait:alice:culture"),
                    trait_type=TraitType.CULTURE,
                    name="Culture",
                    value="collaborative",
                ),
                Trait(
                    id=_id("trait:alice:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="deep_focus",
                ),
            ],
            assignments=[
                Assignment(
                    id=_id("assign:alice:1"),
                    person_id=_id("person:alice"),
                    role_id=rl["Junior Data Engineer"],
                    department_id=dp["Data Engineering"],
                    start_date=date(2020, 1, 15),
                    end_date=date(2023, 6, 1),
                    outcomes=[
                        Outcome(rating=OutcomeRating.MEETS, evaluated_at=date(2020, 7, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2021, 1, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2021, 7, 1)),
                        Outcome(rating=OutcomeRating.EXCEPTIONAL, evaluated_at=date(2022, 1, 1)),
                    ],
                ),
            ],
        ),
        # Bob: Manager, leadership-oriented, moderate technical
        # Maxed potential in leadership, limited in tech growth
        Person(
            id=_id("person:bob"),
            name="Bob Park",
            tenure_years=8.0,
            morale=0.65,
            potential=0.70,
            learning_rate=0.8,
            skills=[
                PersonSkill(
                    skill_id=sk["Team Leadership"],
                    level=SkillLevel.EXPERT,
                    years_experience=7.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["Project Management"],
                    level=SkillLevel.ADVANCED,
                    years_experience=6.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["Communication"],
                    level=SkillLevel.EXPERT,
                    years_experience=8.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["Python"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=4.0,
                    potential_level=SkillLevel.INTERMEDIATE,
                ),
            ],
            traits=[
                Trait(
                    id=_id("trait:bob:collab"),
                    trait_type=TraitType.COLLABORATION_STYLE,
                    name="Collaboration",
                    value="coordinator",
                ),
                Trait(
                    id=_id("trait:bob:culture"),
                    trait_type=TraitType.CULTURE,
                    name="Culture",
                    value="collaborative",
                ),
                Trait(
                    id=_id("trait:bob:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="structured",
                ),
            ],
            assignments=[
                Assignment(
                    id=_id("assign:bob:1"),
                    person_id=_id("person:bob"),
                    role_id=rl["Engineering Manager"],
                    department_id=dp["Engineering Management"],
                    start_date=date(2019, 3, 1),
                    end_date=None,
                    outcomes=[
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2019, 9, 1)),
                        Outcome(rating=OutcomeRating.EXCEPTIONAL, evaluated_at=date(2020, 3, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2020, 9, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2021, 3, 1)),
                        Outcome(rating=OutcomeRating.EXCEPTIONAL, evaluated_at=date(2022, 3, 1)),
                    ],
                ),
            ],
        ),
        # Carol: Junior, analytical focus, fresh talent
        # Very high potential — fast learner, can reach Advanced in most skills
        Person(
            id=_id("person:carol"),
            name="Carol Kim",
            tenure_years=1.5,
            morale=0.85,
            potential=0.90,
            learning_rate=1.5,
            skills=[
                PersonSkill(
                    skill_id=sk["Python"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=2.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=1.5,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["Machine Learning"],
                    level=SkillLevel.BEGINNER,
                    years_experience=1.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["SQL"],
                    level=SkillLevel.BEGINNER,
                    years_experience=1.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
            ],
            traits=[
                Trait(
                    id=_id("trait:carol:collab"),
                    trait_type=TraitType.COLLABORATION_STYLE,
                    name="Collaboration",
                    value="pair_worker",
                ),
                Trait(
                    id=_id("trait:carol:culture"),
                    trait_type=TraitType.CULTURE,
                    name="Culture",
                    value="innovative",
                ),
                Trait(
                    id=_id("trait:carol:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="experimental",
                ),
            ],
            assignments=[
                Assignment(
                    id=_id("assign:carol:1"),
                    person_id=_id("person:carol"),
                    role_id=rl["Junior Data Scientist"],
                    department_id=dp["Data Science"],
                    start_date=date(2024, 6, 1),
                    end_date=None,
                    outcomes=[
                        Outcome(rating=OutcomeRating.MEETS, evaluated_at=date(2024, 12, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2025, 6, 1)),
                    ],
                ),
            ],
        ),
        # Dave: Finance domain, signs of burnout (declining perf, long tenure same role)
        # Reached ceiling — potential_level == level in main skills
        Person(
            id=_id("person:dave"),
            name="Dave Lee",
            tenure_years=7.0,
            morale=0.40,
            potential=0.55,
            learning_rate=0.7,
            skills=[
                PersonSkill(
                    skill_id=sk["Financial Modeling"],
                    level=SkillLevel.EXPERT,
                    years_experience=7.0,
                    potential_level=SkillLevel.EXPERT,
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"],
                    level=SkillLevel.ADVANCED,
                    years_experience=5.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["SQL"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=4.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["Communication"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                    potential_level=SkillLevel.INTERMEDIATE,
                ),
            ],
            traits=[
                Trait(
                    id=_id("trait:dave:mbti"),
                    trait_type=TraitType.MBTI,
                    name="MBTI",
                    value="ISTJ",
                ),
                Trait(
                    id=_id("trait:dave:collab"),
                    trait_type=TraitType.COLLABORATION_STYLE,
                    name="Collaboration",
                    value="independent",
                ),
                Trait(
                    id=_id("trait:dave:culture"),
                    trait_type=TraitType.CULTURE,
                    name="Culture",
                    value="analytical",
                ),
                Trait(
                    id=_id("trait:dave:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="structured",
                ),
            ],
            assignments=[
                Assignment(
                    id=_id("assign:dave:1"),
                    person_id=_id("person:dave"),
                    role_id=rl["Financial Analyst"],
                    department_id=dp["Finance"],
                    start_date=date(2019, 1, 10),
                    end_date=None,
                    outcomes=[
                        Outcome(rating=OutcomeRating.EXCEPTIONAL, evaluated_at=date(2019, 7, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2020, 1, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2020, 7, 1)),
                        Outcome(rating=OutcomeRating.MEETS, evaluated_at=date(2021, 7, 1)),
                        Outcome(rating=OutcomeRating.MEETS, evaluated_at=date(2022, 7, 1)),
                        Outcome(rating=OutcomeRating.BELOW, evaluated_at=date(2023, 7, 1)),
                    ],
                ),
            ],
        ),
        # Eve: All-rounder, moderate across the board, no clear #1
        # Moderate potential — can grow to Advanced in a few skills
        Person(
            id=_id("person:eve"),
            name="Eve Wang",
            tenure_years=4.0,
            morale=0.70,
            potential=0.65,
            learning_rate=1.0,
            skills=[
                PersonSkill(
                    skill_id=sk["Python"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["SQL"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=2.5,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["Communication"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                    potential_level=SkillLevel.ADVANCED,
                ),
                PersonSkill(
                    skill_id=sk["Project Management"],
                    level=SkillLevel.BEGINNER,
                    years_experience=1.0,
                    potential_level=SkillLevel.INTERMEDIATE,
                ),
                PersonSkill(
                    skill_id=sk["Machine Learning"],
                    level=SkillLevel.NOVICE,
                    years_experience=0.5,
                    potential_level=SkillLevel.BEGINNER,
                ),
            ],
            traits=[
                Trait(
                    id=_id("trait:eve:collab"),
                    trait_type=TraitType.COLLABORATION_STYLE,
                    name="Collaboration",
                    value="coordinator",
                ),
                Trait(
                    id=_id("trait:eve:culture"),
                    trait_type=TraitType.CULTURE,
                    name="Culture",
                    value="collaborative",
                ),
                Trait(
                    id=_id("trait:eve:work"),
                    trait_type=TraitType.WORK_PREFERENCE,
                    name="Work Style",
                    value="deep_focus",
                ),
            ],
            assignments=[
                Assignment(
                    id=_id("assign:eve:1"),
                    person_id=_id("person:eve"),
                    role_id=rl["Junior Data Engineer"],
                    department_id=dp["Data Engineering"],
                    start_date=date(2022, 3, 1),
                    end_date=None,
                    outcomes=[
                        Outcome(rating=OutcomeRating.MEETS, evaluated_at=date(2022, 9, 1)),
                        Outcome(rating=OutcomeRating.MEETS, evaluated_at=date(2023, 3, 1)),
                        Outcome(rating=OutcomeRating.EXCEEDS, evaluated_at=date(2023, 9, 1)),
                        Outcome(rating=OutcomeRating.MEETS, evaluated_at=date(2024, 3, 1)),
                    ],
                ),
            ],
        ),
    ]

    return Company(
        id=_id("company:acme"),
        name="Acme Corp",
        skills=skills,
        roles=roles,
        departments=departments,
        people=people,
    )
