"""Game endpoints: quarter reports, achievements, company score."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from talentgraph.api.deps import get_engine, get_achievement_tracker, get_score_history
from talentgraph.api.schemas import ChangeResponse, OutcomeChangeResponse
from talentgraph.game.achievements import AchievementTracker
from talentgraph.game.company_score import compute_company_score
from talentgraph.game.quarter_report import generate_quarter_report
from talentgraph.simulation.engine import SimulationEngine
from talentgraph.simulation.state import OutcomeRecord

router = APIRouter(prefix="/api/game", tags=["game"])


@router.get("/score")
def get_company_score(engine: SimulationEngine = Depends(get_engine)):
    """Get current company health score."""
    # Use last quarter's changes if available
    changes = []
    if engine.history:
        changes = engine.history[-1].changes
    score = compute_company_score(engine.company, changes)
    return score.model_dump()


@router.get("/score/history")
def get_score_history_endpoint(
    history: list = Depends(get_score_history),
):
    """Get company score history for chart display."""
    return history


@router.get("/achievements")
def get_achievements(
    tracker: AchievementTracker = Depends(get_achievement_tracker),
):
    """Get all achievements with unlock status."""
    return {
        "achievements": [a.model_dump() for a in tracker.achievements],
        "progress": tracker.get_progress(),
    }


@router.get("/achievements/unlocked")
def get_unlocked_achievements(
    tracker: AchievementTracker = Depends(get_achievement_tracker),
):
    """Get only unlocked achievements."""
    return [a.model_dump() for a in tracker.get_unlocked()]


@router.post("/advance")
def advance_with_report(
    engine: SimulationEngine = Depends(get_engine),
    tracker: AchievementTracker = Depends(get_achievement_tracker),
    score_history: list = Depends(get_score_history),
):
    """Advance one quarter with full analytics response.

    Primary advance endpoint used by the frontend. Returns:
    - changes: individual change records (same format as /api/simulation/advance)
    - report: QuarterReport with company score, headlines, MVP, warnings
    - newly_unlocked: milestone achievements unlocked this quarter
    - achievement_progress: overall milestone progress
    Also updates score_history and achievement_tracker singletons.
    """
    # Get previous score for delta
    previous_score = score_history[-1]["total"] if score_history else None

    # Advance
    quarter, changes = engine.advance()

    # Build change responses (same format as simulation/advance)
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
                ).model_dump()
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
                ).model_dump()
            )

    # Generate report
    report = generate_quarter_report(
        engine.company, quarter, changes, previous_score=previous_score
    )

    # Check achievements
    newly_unlocked = tracker.check_achievements(
        engine.company, quarter, changes, report.company_score.total
    )

    # Save score to history
    score_history.append({
        "quarter": str(quarter),
        "total": report.company_score.total,
        "team_performance": report.company_score.team_performance,
        "morale_health": report.company_score.morale_health,
        "retention_rate": report.company_score.retention_rate,
        "skill_coverage": report.company_score.skill_coverage,
        "growth_rate": report.company_score.growth_rate,
    })

    return {
        "quarter": str(quarter),
        "changes": change_responses,
        "report": report.model_dump(),
        "newly_unlocked": [a.model_dump() for a in newly_unlocked],
        "achievement_progress": tracker.get_progress(),
        "next_quarter": str(engine.current_quarter),
    }


@router.get("/report/latest")
def get_latest_report(
    engine: SimulationEngine = Depends(get_engine),
    score_history: list = Depends(get_score_history),
):
    """Get the latest quarter report (re-generated from last snapshot)."""
    if not engine.history:
        return {"detail": "No quarters simulated yet"}

    snapshot = engine.history[-1]
    previous_score = (
        score_history[-2]["total"] if len(score_history) >= 2 else None
    )

    report = generate_quarter_report(
        engine.company,
        snapshot.quarter,
        snapshot.changes,
        previous_score=previous_score,
    )
    return report.model_dump()
