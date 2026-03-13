"""People endpoints: list, detail, evaluate."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from talentgraph.api.deps import get_engine
from talentgraph.api.schemas import (
    FitResultResponse,
    PersonDetail,
    PersonSummary,
    SkillInfo,
)
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.engine import SimulationEngine

router = APIRouter(prefix="/api/people", tags=["people"])


def _get_active_role_info(person, company):
    role_lookup = {r.id: r for r in company.roles}
    dept_lookup = {d.id: d for d in company.departments}
    for a in person.assignments:
        if a.end_date is None:
            role = role_lookup.get(a.role_id)
            dept = dept_lookup.get(a.department_id)
            return (
                role.title if role else None,
                dept.name if dept else None,
            )
    return None, None


@router.get("", response_model=list[PersonSummary])
def list_people(engine: SimulationEngine = Depends(get_engine)):
    company = engine.company
    result = []
    for p in company.people:
        role_title, dept_name = _get_active_role_info(p, company)
        result.append(
            PersonSummary(
                id=p.id,
                name=p.name,
                tenure_years=p.tenure_years,
                skill_count=len(p.skills),
                active_role=role_title,
                active_department=dept_name,
                burnout_risk=round(compute_burnout_risk(p), 3),
            )
        )
    return result


@router.get("/{person_id}", response_model=PersonDetail)
def get_person(person_id: UUID, engine: SimulationEngine = Depends(get_engine)):
    company = engine.company
    person = next((p for p in company.people if p.id == person_id), None)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    skill_lookup = {s.id: s for s in company.skills}
    skills = []
    for ps in person.skills:
        skill = skill_lookup.get(ps.skill_id)
        skills.append(
            SkillInfo(
                id=ps.skill_id,
                name=skill.name if skill else "Unknown",
                category=skill.category.value if skill else "unknown",
                person_level=ps.level.value,
                person_years=ps.years_experience,
            )
        )

    role_title, dept_name = _get_active_role_info(person, company)
    fit_results = engine.evaluate_person(person_id)

    return PersonDetail(
        id=person.id,
        name=person.name,
        tenure_years=person.tenure_years,
        skills=skills,
        active_role=role_title,
        active_department=dept_name,
        burnout_risk=round(compute_burnout_risk(person), 3),
        fit_results=[FitResultResponse(**r.model_dump()) for r in fit_results],
    )


@router.get("/{person_id}/evaluate", response_model=list[FitResultResponse])
def evaluate_person(person_id: UUID, engine: SimulationEngine = Depends(get_engine)):
    try:
        results = engine.evaluate_person(person_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return [FitResultResponse(**r.model_dump()) for r in results]
