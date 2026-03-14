"""Simulation endpoints: advance, place, rollback, reset, enhanced mode, config."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from talentgraph.api.deps import get_engine, reset_engine
from talentgraph.api.schemas import (
    ChangeResponse,
    EnhancedModeRequest,
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
from talentgraph.config.simulation_config import SimulationConfig
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures
from talentgraph.simulation.state import OutcomeRecord

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


def _build_status(engine: SimulationEngine) -> SimulationStatusResponse:
    stats = engine.get_stats()
    return SimulationStatusResponse(
        current_quarter=stats["current_quarter"],
        history_length=stats["quarters_simulated"],
        people_count=stats["total_people"],
        active_people=stats["active_people"],
        departed_people=stats["departed_people"],
        average_morale=stats["average_morale"],
        enhanced_mode=stats["enhanced_mode"],
    )


@router.get("/status", response_model=SimulationStatusResponse)
def get_status(engine: SimulationEngine = Depends(get_engine)):
    return _build_status(engine)


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
def reset():
    engine = reset_engine()
    return _build_status(engine)


@router.put("/enhanced", response_model=SimulationStatusResponse)
def set_enhanced_mode(
    req: EnhancedModeRequest, engine: SimulationEngine = Depends(get_engine)
):
    """Toggle enhanced simulation mode and feature flags."""
    engine.features = SimulationFeatures(
        enhanced=req.enhanced,
        growth=req.growth,
        morale=req.morale,
        attrition=req.attrition,
        events=req.events,
    )
    return _build_status(engine)


@router.get("/config")
def get_config(engine: SimulationEngine = Depends(get_engine)):
    """Return current simulation config (or defaults if not set)."""
    cfg = engine.config or SimulationConfig()
    return cfg.model_dump()


@router.put("/config")
def update_config(
    body: dict,
    engine: SimulationEngine = Depends(get_engine),
):
    """Update simulation config. Accepts partial updates.

    Only provided sections/fields are updated. Missing fields keep defaults.
    """
    current = engine.config or SimulationConfig()
    current_data = current.model_dump()

    # Merge provided sections into current config
    for key, value in body.items():
        if key in current_data and isinstance(value, dict):
            current_data[key].update(value)
        else:
            current_data[key] = value

    updated = SimulationConfig(**current_data)
    engine.config = updated
    return updated.model_dump()
