from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from talentgraph.ontology.enums import (
    OutcomeRating,
    SkillCategory,
    SkillLevel,
    TraitType,
)


class Skill(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: SkillCategory
    description: str = ""


class PersonSkill(BaseModel):
    skill_id: UUID
    level: SkillLevel
    years_experience: float = 0.0
    # v0.3: CA/PA system
    potential_level: SkillLevel | None = None  # max growth ceiling (None = same as level)
    quarters_active: int = 0  # quarters this skill was exercised
    quarters_idle: int = 0  # quarters since last used


class RoleSkillRequirement(BaseModel):
    skill_id: UUID
    minimum_level: SkillLevel
    weight: float = Field(default=1.0, ge=0.0, le=5.0)
    critical: bool = False  # if True, missing this skill hard-caps fit score


class Trait(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    trait_type: TraitType
    name: str
    value: str


class Role(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    level: int = Field(ge=1, le=10)
    required_skills: list[RoleSkillRequirement] = []
    description: str = ""
    max_headcount: int = 0  # 0 = unlimited


class Department(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    roles: list[UUID] = Field(default_factory=list)
    description: str = ""
    culture_traits: list[Trait] = Field(default_factory=list)


class Outcome(BaseModel):
    rating: OutcomeRating
    evaluated_at: date
    notes: str = ""


class Assignment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    person_id: UUID = Field(default_factory=uuid4)
    role_id: UUID
    department_id: UUID
    start_date: date
    end_date: date | None = None
    outcomes: list[Outcome] = []


class Person(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    skills: list[PersonSkill] = []
    traits: list[Trait] = []
    assignments: list[Assignment] = []
    tenure_years: float = 0.0
    # v0.3: dynamics
    morale: float = Field(default=0.7, ge=0.0, le=1.0)
    potential: float = Field(default=0.7, ge=0.0, le=1.0)  # overall growth ceiling
    learning_rate: float = Field(default=1.0, ge=0.0, le=3.0)  # skill growth speed
    departed: bool = False  # attrition flag


class Company(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    departments: list[Department] = []
    roles: list[Role] = []
    skills: list[Skill] = []
    people: list[Person] = []
