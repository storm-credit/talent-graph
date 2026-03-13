"""Graph endpoint for React Flow visualization."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from talentgraph.api.deps import get_engine
from talentgraph.api.schemas import GraphEdge, GraphNode, GraphResponse
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.engine import SimulationEngine

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=GraphResponse)
def get_org_graph(engine: SimulationEngine = Depends(get_engine)):
    company = engine.company
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    role_lookup = {r.id: r for r in company.roles}

    # Department nodes
    for dept in company.departments:
        nodes.append(
            GraphNode(
                id=f"dept-{dept.id}",
                type="department",
                label=dept.name,
                data={"role_count": len(dept.roles)},
            )
        )

        # Role nodes under department
        for role_id in dept.roles:
            role = role_lookup.get(role_id)
            if role is None:
                continue
            nodes.append(
                GraphNode(
                    id=f"role-{role.id}",
                    type="role",
                    label=role.title,
                    data={"level": role.level},
                )
            )
            edges.append(
                GraphEdge(
                    id=f"dept-{dept.id}->role-{role.id}",
                    source=f"dept-{dept.id}",
                    target=f"role-{role.id}",
                )
            )

    # Person nodes with edges to their active role
    for person in company.people:
        burnout = round(compute_burnout_risk(person), 3)
        active_assignment = next((a for a in person.assignments if a.end_date is None), None)

        fit_score = None
        if active_assignment:
            try:
                results = engine.evaluate_person(person.id)
                match = next(
                    (r for r in results
                     if r.role_id == active_assignment.role_id
                     and r.department_id == active_assignment.department_id),
                    None,
                )
                if match:
                    fit_score = match.fit_score
            except ValueError:
                pass

        nodes.append(
            GraphNode(
                id=f"person-{person.id}",
                type="person",
                label=person.name,
                data={
                    "tenure": person.tenure_years,
                    "burnout_risk": burnout,
                    "fit_score": fit_score,
                    "skill_count": len(person.skills),
                },
            )
        )

        if active_assignment:
            edges.append(
                GraphEdge(
                    id=f"person-{person.id}->role-{active_assignment.role_id}",
                    source=f"role-{active_assignment.role_id}",
                    target=f"person-{person.id}",
                    label="assigned",
                )
            )

    return GraphResponse(nodes=nodes, edges=edges)
