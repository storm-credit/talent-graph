"""Simulation endpoints: advance, place, rollback, reset."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from talentgraph.api.deps import get_engine, reset_engine
from talentgraph.api.schemas import (
    ChangeResponse,
    FitResultResponse,
    OutcomeChangeResponse,
    PlacementRequest,
    PlacementResponse,
    PreviewPlacementRequest,
    QuarterAdvanceResponse,
    RollbackRequest,
    RollbackResponse,
    SimulationStatusResponse,
)
from talentgraph.simulation.engine import SimulationEngine
from talentgraph.simulation.state import OutcomeRecord

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.get("/status", response_model=SimulationStatusResponse)
def get_status(engine: SimulationEngine = Depends(get_engine)):
    return SimulationStatusResponse(
        current_quarter=str(engine.current_quarter),
        history_length=len(engine.history),
        people_count=len(engine.company.people),
    )


@router.post("/advance", response_model=QuarterAdvanceResponse)
def advance_quarter(engine: SimulationEngine = Depends(get_engine)):
    quarter, changes = engine.advance()

    change_responses = []
    for c in changes:
        if isinstance(c, OutcomeRecord):
            change_responses.append(
                OutcomeChangeResponse(
                    person_id=c.person_id,
                    person_name=c.person_name,
                    change_type=c.change_type,
                    description=c.description,
                    old_value=c.old_value,
                    new_value=c.new_value,
                    role_title=c.role_title,
                    department_name=c.department_name,
                    rating=c.rating.value,
                    predicted_performance=c.predicted_performance,
                )
            )
        else:
            change_responses.append(
                ChangeResponse(
                    person_id=c.person_id,
                    person_name=c.person_name,
                    change_type=c.change_type,
                    description=c.description,
                    old_value=c.old_value,
                    new_value=c.new_value,
                )
            )

    return QuarterAdvanceResponse(
        quarter=str(quarter),
        changes=change_responses,
        next_quarter=str(engine.current_quarter),
    )


@router.post("/place", response_model=PlacementResponse)
def place_person(req: PlacementRequest, engine: SimulationEngine = Depends(get_engine)):
    try:
        event = engine.place(req.person_id, req.role_id, req.department_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return PlacementResponse(
        person_name=event.person_name,
        role_title=event.role_title,
        department_name=event.department_name,
        previous_role_title=event.previous_role_title,
    )


@router.post("/preview-place", response_model=FitResultResponse)
def preview_placement(
    req: PreviewPlacementRequest, engine: SimulationEngine = Depends(get_engine)
):
    try:
        result = engine.preview_placement(req.person_id, req.role_id, req.department_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return FitResultResponse(**result.model_dump())


@router.post("/rollback", response_model=RollbackResponse)
def rollback(req: RollbackRequest, engine: SimulationEngine = Depends(get_engine)):
    try:
        quarter = engine.rollback(req.steps)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RollbackResponse(
        rolled_back_to=str(quarter),
        history_length=len(engine.history),
    )


@router.post("/reset", response_model=SimulationStatusResponse)
def reset(engine: SimulationEngine = Depends(get_engine)):
    engine.reset()
    return SimulationStatusResponse(
        current_quarter=str(engine.current_quarter),
        history_length=len(engine.history),
        people_count=len(engine.company.people),
    )
