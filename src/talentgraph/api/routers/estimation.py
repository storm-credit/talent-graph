"""Estimation API — Bayesian skill estimation via project outcomes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from talentgraph.api.deps import get_engine, get_estimation_store
from talentgraph.estimation.csv_import import parse_csv
from talentgraph.estimation.enums import (
    ProjectDifficulty,
    ProjectResult,
    ProjectRole,
    ProjectStatus,
)
from talentgraph.estimation.store import EstimationStore
from talentgraph.simulation.engine import SimulationEngine

router = APIRouter(prefix="/api/estimation", tags=["estimation"])


# ── Request schemas ───────────────────────────────────────────────────


class ProjectCreateRequest(BaseModel):
    name: str
    description: str = ""
    difficulty: int = 3
    required_skill_ids: list[str] = []
    start_date: str | None = None
    end_date: str | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    difficulty: int | None = None
    status: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class AssignRequest(BaseModel):
    person_id: str
    role: str = "contributor"


class OutcomeRequest(BaseModel):
    person_id: str
    result: int  # 1=failure, 2=partial, 3=success, 4=excellent
    notes: str = ""


# ── Project CRUD ──────────────────────────────────────────────────────


@router.get("/projects")
def list_projects(store: EstimationStore = Depends(get_estimation_store)):
    projects = store.list_projects()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "difficulty": p.difficulty.value,
            "required_skill_ids": [str(s) for s in p.required_skill_ids],
            "start_date": p.start_date.isoformat(),
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "status": p.status.value,
            "assignment_count": len(store.get_assignments(p.id)),
            "outcome_count": len(store.get_outcomes_for_project(p.id)),
        }
        for p in projects
    ]


@router.post("/projects")
def create_project(
    req: ProjectCreateRequest,
    store: EstimationStore = Depends(get_estimation_store),
):
    project = store.add_project(
        name=req.name,
        description=req.description,
        difficulty=ProjectDifficulty(req.difficulty),
        required_skill_ids=[UUID(s) for s in req.required_skill_ids],
        start_date=req.start_date,
        end_date=req.end_date,
    )
    return {"id": str(project.id), "name": project.name, "status": project.status.value}


@router.get("/projects/{project_id}")
def get_project(
    project_id: str,
    store: EstimationStore = Depends(get_estimation_store),
    engine: SimulationEngine = Depends(get_engine),
):
    project = store.get_project(UUID(project_id))
    if not project:
        raise HTTPException(404, "Project not found")

    company = engine.company
    skill_map = {s.id: s.name for s in company.skills}
    person_map = {p.id: p.name for p in company.people}

    assignments = store.get_assignments(project.id)
    outcomes = store.get_outcomes_for_project(project.id)

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "difficulty": project.difficulty.value,
        "required_skills": [
            {"id": str(sid), "name": skill_map.get(sid, "Unknown")}
            for sid in project.required_skill_ids
        ],
        "start_date": project.start_date.isoformat(),
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "status": project.status.value,
        "assignments": [
            {
                "id": str(a.id),
                "person_id": str(a.person_id),
                "person_name": person_map.get(a.person_id, "Unknown"),
                "role": a.role_in_project.value,
            }
            for a in assignments
        ],
        "outcomes": [
            {
                "id": str(o.id),
                "person_id": str(o.person_id),
                "person_name": person_map.get(o.person_id, "Unknown"),
                "result": o.result.value,
                "result_label": o.result.name.lower(),
                "evaluated_at": o.evaluated_at.isoformat(),
                "notes": o.notes,
            }
            for o in outcomes
        ],
    }


@router.put("/projects/{project_id}")
def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    store: EstimationStore = Depends(get_estimation_store),
):
    updates = {}
    if req.name is not None:
        updates["name"] = req.name
    if req.description is not None:
        updates["description"] = req.description
    if req.difficulty is not None:
        updates["difficulty"] = ProjectDifficulty(req.difficulty)
    if req.status is not None:
        updates["status"] = ProjectStatus(req.status)

    project = store.update_project(UUID(project_id), **updates)
    if not project:
        raise HTTPException(404, "Project not found")
    return {"id": str(project.id), "status": project.status.value}


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: str,
    store: EstimationStore = Depends(get_estimation_store),
):
    if not store.delete_project(UUID(project_id)):
        raise HTTPException(404, "Project not found")
    return {"deleted": True}


# ── Assignments & Outcomes ────────────────────────────────────────────


@router.post("/projects/{project_id}/assign")
def assign_person(
    project_id: str,
    req: AssignRequest,
    store: EstimationStore = Depends(get_estimation_store),
):
    assignment = store.assign_person(
        UUID(project_id),
        UUID(req.person_id),
        ProjectRole(req.role),
    )
    if not assignment:
        raise HTTPException(404, "Project not found")
    return {"id": str(assignment.id), "person_id": req.person_id, "role": assignment.role_in_project.value}


@router.post("/projects/{project_id}/outcome")
def record_outcome(
    project_id: str,
    req: OutcomeRequest,
    store: EstimationStore = Depends(get_estimation_store),
    engine: SimulationEngine = Depends(get_engine),
):
    updated = store.record_outcome(
        UUID(project_id),
        UUID(req.person_id),
        ProjectResult(req.result),
        req.notes,
    )

    company = engine.company
    skill_map = {s.id: s.name for s in company.skills}

    return {
        "updated_estimates": [
            {
                "skill_id": str(e.skill_id),
                "skill_name": skill_map.get(e.skill_id, "Unknown"),
                "mu": round(e.mu, 2),
                "sigma": round(e.sigma, 2),
                "confidence": round(e.confidence * 100, 1),
                "level": e.level_name,
                "trend": e.trend.value,
                "update_count": e.update_count,
            }
            for e in updated
        ]
    }


# ── Scout Report ──────────────────────────────────────────────────────


@router.get("/people/{person_id}/estimates")
def get_scout_report(
    person_id: str,
    store: EstimationStore = Depends(get_estimation_store),
    engine: SimulationEngine = Depends(get_engine),
):
    pid = UUID(person_id)
    company = engine.company
    person = next((p for p in company.people if p.id == pid), None)
    if not person:
        raise HTTPException(404, "Person not found")

    skill_map = {s.id: s.name for s in company.skills}
    estimates = store.get_estimates_for_person(pid)

    # Also include current official PersonSkill levels for comparison
    official_skills = {ps.skill_id: ps.level.value for ps in person.skills}

    return {
        "person_id": person_id,
        "person_name": person.name,
        "estimates": [
            {
                "skill_id": str(e.skill_id),
                "skill_name": skill_map.get(e.skill_id, "Unknown"),
                "mu": round(e.mu, 2),
                "sigma": round(e.sigma, 2),
                "confidence": round(e.confidence * 100, 1),
                "discrete_level": e.discrete_level,
                "level_name": e.level_name,
                "trend": e.trend.value,
                "update_count": e.update_count,
                "official_level": official_skills.get(e.skill_id),
            }
            for e in estimates
        ],
        "avg_confidence": round(
            sum(e.confidence for e in estimates) / len(estimates) * 100, 1
        )
        if estimates
        else 0,
        "total_projects": len(store.get_outcomes_for_person(pid)),
    }


@router.get("/people/{person_id}/estimates/{skill_id}/history")
def get_estimate_history(
    person_id: str,
    skill_id: str,
    store: EstimationStore = Depends(get_estimation_store),
):
    estimate = store.get_estimate(UUID(person_id), UUID(skill_id))
    if not estimate:
        raise HTTPException(404, "No estimate found")

    return {
        "person_id": person_id,
        "skill_id": skill_id,
        "history": [
            {
                "mu": round(s.mu, 2),
                "sigma": round(s.sigma, 2),
                "timestamp": s.timestamp.isoformat(),
            }
            for s in estimate.history
        ],
    }


# ── Initialize all priors ────────────────────────────────────────────


@router.post("/initialize-all")
def initialize_all(
    store: EstimationStore = Depends(get_estimation_store),
    engine: SimulationEngine = Depends(get_engine),
):
    """Initialize Bayesian priors for all people based on current role + tenure."""
    company = engine.company
    skill_ids = [s.id for s in company.skills]
    initialized = 0

    for person in company.people:
        if person.departed:
            continue
        # Get current role title
        title = "사원"
        if person.assignments:
            active = [a for a in person.assignments if a.end_date is None]
            if active:
                role = next(
                    (r for r in company.roles if r.id == active[0].role_id), None
                )
                if role:
                    title = role.title

        store.initialize_person(person.id, skill_ids, title, person.tenure_years)
        initialized += 1

    return {"initialized_people": initialized, "skills_per_person": len(skill_ids)}


# ── Skills list (for project creation form) ───────────────────────────


@router.get("/skills")
def list_skills(engine: SimulationEngine = Depends(get_engine)):
    """Return all company skills (for project creation skill picker)."""
    return [
        {"id": str(s.id), "name": s.name, "category": s.category.value}
        for s in engine.company.skills
    ]


# ── CSV Import ────────────────────────────────────────────────────────


@router.post("/import")
async def import_csv(
    file: UploadFile,
    store: EstimationStore = Depends(get_estimation_store),
    engine: SimulationEngine = Depends(get_engine),
):
    """Import employees from CSV file."""
    content = await file.read()
    text = content.decode("utf-8-sig")  # Handle BOM from Excel

    result = parse_csv(text)

    return {
        "imported_count": result.imported_count,
        "employees": [
            {
                "name": emp.name,
                "position": emp.position,
                "department": emp.department,
                "hire_date": emp.hire_date.isoformat(),
            }
            for emp in result.imported
        ],
        "errors": result.errors,
        "warnings": result.warnings,
    }
