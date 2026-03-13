"""Company overview endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from talentgraph.api.deps import get_engine
from talentgraph.api.schemas import CompanyOverview
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.engine import SimulationEngine

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("", response_model=CompanyOverview)
def get_company(engine: SimulationEngine = Depends(get_engine)):
    company = engine.company
    burnout_risks = [compute_burnout_risk(p) for p in company.people]
    avg_burnout = sum(burnout_risks) / len(burnout_risks) if burnout_risks else 0.0
    tenures = [p.tenure_years for p in company.people]
    avg_tenure = sum(tenures) / len(tenures) if tenures else 0.0

    return CompanyOverview(
        name=company.name,
        people_count=len(company.people),
        department_count=len(company.departments),
        role_count=len(company.roles),
        skill_count=len(company.skills),
        avg_tenure=round(avg_tenure, 1),
        avg_burnout_risk=round(avg_burnout, 3),
    )
