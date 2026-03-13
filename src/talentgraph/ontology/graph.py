from __future__ import annotations

from uuid import UUID

import networkx as nx

from talentgraph.ontology.enums import SkillLevel
from talentgraph.ontology.models import Company


class OntologyGraph:
    """Heterogeneous directed graph built from a Company model.

    Node types: person, role, department, skill
    Edge types: HAS_SKILL, REQUIRES_SKILL, HAS_ROLE
    """

    def __init__(self, company: Company) -> None:
        self.graph = nx.DiGraph()
        self._build(company)

    def _build(self, company: Company) -> None:
        for skill in company.skills:
            self.graph.add_node(skill.id, type="skill", data=skill)

        for role in company.roles:
            self.graph.add_node(role.id, type="role", data=role)
            for req in role.required_skills:
                self.graph.add_edge(
                    role.id,
                    req.skill_id,
                    relation="REQUIRES_SKILL",
                    minimum_level=req.minimum_level,
                    weight=req.weight,
                )

        for dept in company.departments:
            self.graph.add_node(dept.id, type="department", data=dept)
            for role_id in dept.roles:
                self.graph.add_edge(dept.id, role_id, relation="HAS_ROLE")

        for person in company.people:
            self.graph.add_node(person.id, type="person", data=person)
            for ps in person.skills:
                self.graph.add_edge(
                    person.id,
                    ps.skill_id,
                    relation="HAS_SKILL",
                    level=ps.level,
                    years=ps.years_experience,
                )

    def get_skills_for_role(self, role_id: UUID) -> list[dict]:
        """Return required skills for a role with their constraints."""
        results = []
        for _, target, data in self.graph.out_edges(role_id, data=True):
            if data.get("relation") == "REQUIRES_SKILL":
                results.append(
                    {
                        "skill_id": target,
                        "minimum_level": data["minimum_level"],
                        "weight": data["weight"],
                    }
                )
        return results

    def get_roles_in_department(self, dept_id: UUID) -> list[UUID]:
        """Return all role IDs in a department."""
        return [
            target
            for _, target, data in self.graph.out_edges(dept_id, data=True)
            if data.get("relation") == "HAS_ROLE"
        ]

    def get_person_skills(self, person_id: UUID) -> dict[UUID, dict]:
        """Return a person's skills as {skill_id: {level, years}}."""
        result: dict[UUID, dict] = {}
        for _, target, data in self.graph.out_edges(person_id, data=True):
            if data.get("relation") == "HAS_SKILL":
                result[target] = {"level": data["level"], "years": data["years"]}
        return result

    def find_people_with_skill(
        self, skill_id: UUID, min_level: SkillLevel | None = None
    ) -> list[UUID]:
        """Return person IDs who have a given skill, optionally at minimum level."""
        people = []
        for source, _, data in self.graph.in_edges(skill_id, data=True):
            if data.get("relation") == "HAS_SKILL":
                if min_level is None or data["level"].numeric >= min_level.numeric:
                    people.append(source)
        return people
