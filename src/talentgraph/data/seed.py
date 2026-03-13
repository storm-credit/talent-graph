"""Generate deterministic sample data for TalentGraph demos and testing."""

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

    # ── Roles ──
    roles = [
        Role(
            id=_id("role:sr_data_eng"),
            title="Senior Data Engineer",
            level=5,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Python"], minimum_level=SkillLevel.ADVANCED, weight=5.0
                ),
                RoleSkillRequirement(
                    skill_id=sk["SQL"], minimum_level=SkillLevel.ADVANCED, weight=4.0
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
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Python"], minimum_level=SkillLevel.ADVANCED, weight=4.0
                ),
                RoleSkillRequirement(
                    skill_id=sk["Machine Learning"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=5.0,
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
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Team Leadership"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=5.0,
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
                    skill_id=sk["Python"], minimum_level=SkillLevel.INTERMEDIATE, weight=2.0
                ),
            ],
        ),
        Role(
            id=_id("role:jr_data_eng"),
            title="Junior Data Engineer",
            level=3,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Python"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=4.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["SQL"], minimum_level=SkillLevel.BEGINNER, weight=3.0
                ),
            ],
        ),
        Role(
            id=_id("role:financial_analyst"),
            title="Financial Analyst",
            level=4,
            required_skills=[
                RoleSkillRequirement(
                    skill_id=sk["Financial Modeling"],
                    minimum_level=SkillLevel.ADVANCED,
                    weight=5.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["Data Analysis"],
                    minimum_level=SkillLevel.INTERMEDIATE,
                    weight=3.0,
                ),
                RoleSkillRequirement(
                    skill_id=sk["SQL"], minimum_level=SkillLevel.INTERMEDIATE, weight=2.0
                ),
            ],
        ),
        Role(
            id=_id("role:jr_data_scientist"),
            title="Junior Data Scientist",
            level=3,
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

    # ── Departments ──
    departments = [
        Department(
            id=_id("dept:data_eng"),
            name="Data Engineering",
            roles=[rl["Senior Data Engineer"], rl["Junior Data Engineer"]],
        ),
        Department(
            id=_id("dept:data_sci"),
            name="Data Science",
            roles=[rl["Data Scientist"], rl["Junior Data Scientist"]],
        ),
        Department(
            id=_id("dept:eng_mgmt"),
            name="Engineering Management",
            roles=[rl["Engineering Manager"]],
        ),
        Department(
            id=_id("dept:finance"),
            name="Finance",
            roles=[rl["Financial Analyst"]],
        ),
    ]
    dp = {d.name: d.id for d in departments}

    # ── People ──
    people = [
        # Alice: Data engineer, strong technical skills, good performance trajectory
        Person(
            id=_id("person:alice"),
            name="Alice Chen",
            tenure_years=5.5,
            skills=[
                PersonSkill(
                    skill_id=sk["Python"], level=SkillLevel.EXPERT, years_experience=8.0
                ),
                PersonSkill(
                    skill_id=sk["SQL"], level=SkillLevel.ADVANCED, years_experience=6.0
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"], level=SkillLevel.ADVANCED, years_experience=5.0
                ),
                PersonSkill(
                    skill_id=sk["Machine Learning"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=2.0,
                ),
                PersonSkill(
                    skill_id=sk["Team Leadership"],
                    level=SkillLevel.BEGINNER,
                    years_experience=1.0,
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
        Person(
            id=_id("person:bob"),
            name="Bob Park",
            tenure_years=8.0,
            skills=[
                PersonSkill(
                    skill_id=sk["Team Leadership"],
                    level=SkillLevel.EXPERT,
                    years_experience=7.0,
                ),
                PersonSkill(
                    skill_id=sk["Project Management"],
                    level=SkillLevel.ADVANCED,
                    years_experience=6.0,
                ),
                PersonSkill(
                    skill_id=sk["Communication"],
                    level=SkillLevel.EXPERT,
                    years_experience=8.0,
                ),
                PersonSkill(
                    skill_id=sk["Python"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=4.0,
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
        Person(
            id=_id("person:carol"),
            name="Carol Kim",
            tenure_years=1.5,
            skills=[
                PersonSkill(
                    skill_id=sk["Python"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=2.0,
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=1.5,
                ),
                PersonSkill(
                    skill_id=sk["Machine Learning"],
                    level=SkillLevel.BEGINNER,
                    years_experience=1.0,
                ),
                PersonSkill(
                    skill_id=sk["SQL"], level=SkillLevel.BEGINNER, years_experience=1.0
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
        Person(
            id=_id("person:dave"),
            name="Dave Lee",
            tenure_years=7.0,
            skills=[
                PersonSkill(
                    skill_id=sk["Financial Modeling"],
                    level=SkillLevel.EXPERT,
                    years_experience=7.0,
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"],
                    level=SkillLevel.ADVANCED,
                    years_experience=5.0,
                ),
                PersonSkill(
                    skill_id=sk["SQL"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=4.0,
                ),
                PersonSkill(
                    skill_id=sk["Communication"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                ),
            ],
            traits=[
                Trait(
                    id=_id("trait:dave:mbti"),
                    trait_type=TraitType.MBTI,
                    name="MBTI",
                    value="ISTJ",
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
        Person(
            id=_id("person:eve"),
            name="Eve Wang",
            tenure_years=4.0,
            skills=[
                PersonSkill(
                    skill_id=sk["Python"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                ),
                PersonSkill(
                    skill_id=sk["SQL"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                ),
                PersonSkill(
                    skill_id=sk["Data Analysis"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=2.5,
                ),
                PersonSkill(
                    skill_id=sk["Communication"],
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=3.0,
                ),
                PersonSkill(
                    skill_id=sk["Project Management"],
                    level=SkillLevel.BEGINNER,
                    years_experience=1.0,
                ),
                PersonSkill(
                    skill_id=sk["Machine Learning"],
                    level=SkillLevel.NOVICE,
                    years_experience=0.5,
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
