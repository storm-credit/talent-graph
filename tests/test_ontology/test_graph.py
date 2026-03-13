from talentgraph.ontology.enums import SkillLevel
from talentgraph.ontology.graph import OntologyGraph
from talentgraph.data.seed import _id


def test_graph_node_counts(sample_company):
    g = OntologyGraph(sample_company)
    nodes = g.graph.nodes(data=True)

    type_counts = {}
    for _, data in nodes:
        t = data["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    assert type_counts["skill"] == 8
    assert type_counts["role"] == 6
    assert type_counts["department"] == 4
    assert type_counts["person"] == 5


def test_get_skills_for_role(sample_company):
    g = OntologyGraph(sample_company)
    role_id = _id("role:sr_data_eng")
    skills = g.get_skills_for_role(role_id)
    assert len(skills) == 3
    skill_ids = {s["skill_id"] for s in skills}
    assert _id("skill:python") in skill_ids


def test_get_roles_in_department(sample_company):
    g = OntologyGraph(sample_company)
    dept_id = _id("dept:data_eng")
    roles = g.get_roles_in_department(dept_id)
    assert len(roles) == 2


def test_get_person_skills(sample_company):
    g = OntologyGraph(sample_company)
    person_id = _id("person:alice")
    skills = g.get_person_skills(person_id)
    assert _id("skill:python") in skills
    assert skills[_id("skill:python")]["level"] == SkillLevel.EXPERT


def test_find_people_with_skill(sample_company):
    g = OntologyGraph(sample_company)
    python_id = _id("skill:python")
    people = g.find_people_with_skill(python_id)
    assert len(people) >= 3  # Alice, Carol, Eve all have Python

    experts = g.find_people_with_skill(python_id, min_level=SkillLevel.EXPERT)
    assert _id("person:alice") in experts
