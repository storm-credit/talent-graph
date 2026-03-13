import pytest

from talentgraph.data.seed import create_sample_company, _id
from talentgraph.ontology.models import Company


@pytest.fixture
def sample_company() -> Company:
    return create_sample_company()


@pytest.fixture
def alice(sample_company):
    return next(p for p in sample_company.people if p.name == "Alice Chen")


@pytest.fixture
def bob(sample_company):
    return next(p for p in sample_company.people if p.name == "Bob Park")


@pytest.fixture
def carol(sample_company):
    return next(p for p in sample_company.people if p.name == "Carol Kim")


@pytest.fixture
def dave(sample_company):
    return next(p for p in sample_company.people if p.name == "Dave Lee")


@pytest.fixture
def eve(sample_company):
    return next(p for p in sample_company.people if p.name == "Eve Wang")


@pytest.fixture
def sr_data_eng_role(sample_company):
    return next(r for r in sample_company.roles if r.title == "Senior Data Engineer")


@pytest.fixture
def eng_manager_role(sample_company):
    return next(r for r in sample_company.roles if r.title == "Engineering Manager")


@pytest.fixture
def financial_analyst_role(sample_company):
    return next(r for r in sample_company.roles if r.title == "Financial Analyst")


@pytest.fixture
def skill_lookup(sample_company):
    return {s.id: s for s in sample_company.skills}
