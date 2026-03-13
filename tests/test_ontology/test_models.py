import json

import pytest
from pydantic import ValidationError

from talentgraph.ontology.enums import SkillCategory, SkillLevel
from talentgraph.ontology.models import Company, Person, Role, Skill


def test_skill_creation():
    s = Skill(name="Python", category=SkillCategory.TECHNICAL)
    assert s.name == "Python"
    assert s.id is not None


def test_skill_level_numeric():
    assert SkillLevel.NOVICE.numeric == 1
    assert SkillLevel.EXPERT.numeric == 5


def test_role_level_validation():
    with pytest.raises(ValidationError):
        Role(title="Invalid", level=0)
    with pytest.raises(ValidationError):
        Role(title="Invalid", level=11)


def test_person_default_empty_lists():
    p = Person(name="Test")
    assert p.skills == []
    assert p.traits == []
    assert p.assignments == []


def test_company_serialization_roundtrip(sample_company):
    json_str = sample_company.model_dump_json()
    restored = Company.model_validate_json(json_str)
    assert restored.name == sample_company.name
    assert len(restored.people) == len(sample_company.people)
    assert len(restored.skills) == len(sample_company.skills)
    assert len(restored.roles) == len(sample_company.roles)
    assert len(restored.departments) == len(sample_company.departments)


def test_deterministic_uuids(sample_company):
    """Same seed data should produce same UUIDs."""
    from talentgraph.data.seed import create_sample_company

    company2 = create_sample_company()
    for p1, p2 in zip(sample_company.people, company2.people):
        assert p1.id == p2.id
