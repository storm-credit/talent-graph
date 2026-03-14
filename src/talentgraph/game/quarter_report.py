"""Quarter report — post-advance summary with headlines, MVP, warnings.

Generates a structured report after each quarter advance, highlighting
key events, top performers, at-risk employees, and department scores.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from uuid import UUID

from talentgraph.ontology.enums import OutcomeRating
from talentgraph.ontology.models import Company
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.state import ChangeRecord, OutcomeRecord, QuarterLabel
from talentgraph.game.company_score import CompanyScore, compute_company_score


class PersonHighlight(BaseModel):
    """A highlighted person in the quarter report."""

    person_id: UUID
    person_name: str
    highlight_type: str  # "mvp", "warning", "growth", "departure"
    description: str
    description_ko: str
    metric_value: float | None = None  # e.g., morale %, burnout %


class Headline(BaseModel):
    """A headline event for the quarter report."""

    icon: str  # emoji
    text: str
    text_ko: str
    category: str  # "positive", "negative", "neutral"


class DepartmentScore(BaseModel):
    """Department-level performance summary."""

    department_id: UUID
    department_name: str
    avg_rating: float  # 1-5 average outcome
    active_count: int
    departed_count: int


class QuarterReport(BaseModel):
    """Full quarter report with all summary data."""

    quarter: str  # e.g., "2025-Q1"
    company_score: CompanyScore
    previous_score: float | None = None  # for delta display
    score_delta: float | None = None

    headlines: list[Headline] = Field(default_factory=list)
    mvp: PersonHighlight | None = None
    warnings: list[PersonHighlight] = Field(default_factory=list)
    highlights: list[PersonHighlight] = Field(default_factory=list)
    department_scores: list[DepartmentScore] = Field(default_factory=list)

    total_active: int = 0
    total_departed: int = 0
    avg_morale: float = 0.0
    growth_events: int = 0
    decay_events: int = 0
    departures_this_quarter: int = 0


def generate_quarter_report(
    company: Company,
    quarter: QuarterLabel,
    changes: list[ChangeRecord],
    previous_score: float | None = None,
) -> QuarterReport:
    """Generate a structured quarter report from simulation results.

    Args:
        company: Company state AFTER the quarter advance
        quarter: The quarter that was just completed
        changes: Change records from the quarter
        previous_score: Previous quarter's company score (for delta)

    Returns:
        QuarterReport with all summary data
    """
    active = [p for p in company.people if not p.departed]
    departed = [p for p in company.people if p.departed]

    # Compute company score
    score = compute_company_score(company, changes)

    # Score delta
    delta = None
    if previous_score is not None:
        delta = round(score.total - previous_score, 1)

    # Headlines
    headlines = _build_headlines(changes, company)

    # MVP — person with best outcome this quarter
    mvp = _find_mvp(changes, company)

    # Warnings — burnout risk, low morale
    warnings = _find_warnings(active)

    # Highlights — growth, certifications, departures
    highlights = _build_highlights(changes)

    # Department scores
    dept_scores = _compute_department_scores(company, changes)

    # Stats
    departures = sum(1 for c in changes if c.change_type == "departure")
    growth_events = sum(1 for c in changes if c.change_type == "skill_growth")
    decay_events = sum(1 for c in changes if c.change_type == "skill_decay")
    avg_morale = sum(p.morale for p in active) / len(active) if active else 0.0

    return QuarterReport(
        quarter=str(quarter),
        company_score=score,
        previous_score=previous_score,
        score_delta=delta,
        headlines=headlines,
        mvp=mvp,
        warnings=warnings,
        highlights=highlights,
        department_scores=dept_scores,
        total_active=len(active),
        total_departed=len(departed),
        avg_morale=round(avg_morale, 3),
        growth_events=growth_events,
        decay_events=decay_events,
        departures_this_quarter=departures,
    )


def _build_headlines(
    changes: list[ChangeRecord], company: Company
) -> list[Headline]:
    """Extract top headlines from changes."""
    headlines: list[Headline] = []

    # Skill growth headlines
    for c in changes:
        if c.change_type == "skill_growth":
            headlines.append(
                Headline(
                    icon="🎯",
                    text=c.description,
                    text_ko=c.description,  # description is already descriptive
                    category="positive",
                )
            )
        elif c.change_type == "certification":
            headlines.append(
                Headline(
                    icon="🎓",
                    text=c.description,
                    text_ko=c.description,
                    category="positive",
                )
            )
        elif c.change_type == "departure":
            headlines.append(
                Headline(
                    icon="🚪",
                    text=c.description,
                    text_ko=c.description,
                    category="negative",
                )
            )
        elif c.change_type == "event":
            headlines.append(
                Headline(
                    icon="📰",
                    text=c.description,
                    text_ko=c.description,
                    category="neutral",
                )
            )
        elif c.change_type == "skill_decay":
            headlines.append(
                Headline(
                    icon="📉",
                    text=c.description,
                    text_ko=c.description,
                    category="negative",
                )
            )

    # Limit to top 8 headlines (prioritize positive, then negative, then neutral)
    priority = {"positive": 0, "negative": 1, "neutral": 2}
    headlines.sort(key=lambda h: priority.get(h.category, 3))
    return headlines[:8]


def _find_mvp(
    changes: list[ChangeRecord], company: Company
) -> PersonHighlight | None:
    """Find the MVP — person with highest outcome rating this quarter."""
    outcomes = [c for c in changes if isinstance(c, OutcomeRecord)]
    if not outcomes:
        return None

    # Pick the one with the highest rating
    best = max(outcomes, key=lambda o: o.rating.numeric)

    return PersonHighlight(
        person_id=best.person_id,
        person_name=best.person_name,
        highlight_type="mvp",
        description=f"MVP: {best.person_name} — {best.rating.value} in {best.role_title}",
        description_ko=f"MVP: {best.person_name} — {best.role_title}에서 {best.rating.value}",
        metric_value=best.rating.numeric,
    )


def _find_warnings(active: list) -> list[PersonHighlight]:
    """Find at-risk people: high burnout, low morale."""
    warnings: list[PersonHighlight] = []

    for person in active:
        burnout = compute_burnout_risk(person)
        if burnout >= 0.6:
            warnings.append(
                PersonHighlight(
                    person_id=person.id,
                    person_name=person.name,
                    highlight_type="warning",
                    description=f"Burnout risk: {person.name} ({burnout:.0%})",
                    description_ko=f"번아웃 위험: {person.name} ({burnout:.0%})",
                    metric_value=burnout,
                )
            )
        elif person.morale < 0.3:
            warnings.append(
                PersonHighlight(
                    person_id=person.id,
                    person_name=person.name,
                    highlight_type="warning",
                    description=f"Low morale: {person.name} ({person.morale:.0%})",
                    description_ko=f"낮은 사기: {person.name} ({person.morale:.0%})",
                    metric_value=person.morale,
                )
            )

    return warnings


def _build_highlights(changes: list[ChangeRecord]) -> list[PersonHighlight]:
    """Build highlight cards for notable changes."""
    highlights: list[PersonHighlight] = []
    seen_people: set[UUID] = set()

    for c in changes:
        if c.person_id in seen_people:
            continue

        if c.change_type == "skill_growth":
            highlights.append(
                PersonHighlight(
                    person_id=c.person_id,
                    person_name=c.person_name,
                    highlight_type="growth",
                    description=c.description,
                    description_ko=c.description,
                )
            )
            seen_people.add(c.person_id)
        elif c.change_type == "departure":
            highlights.append(
                PersonHighlight(
                    person_id=c.person_id,
                    person_name=c.person_name,
                    highlight_type="departure",
                    description=c.description,
                    description_ko=c.description,
                )
            )
            seen_people.add(c.person_id)

    return highlights[:6]  # limit


def _compute_department_scores(
    company: Company, changes: list[ChangeRecord]
) -> list[DepartmentScore]:
    """Compute per-department performance summary."""
    dept_lookup = {d.id: d for d in company.departments}
    dept_outcomes: dict[UUID, list[float]] = {}
    dept_active: dict[UUID, int] = {}
    dept_departed: dict[UUID, int] = {}

    # Initialize
    for dept in company.departments:
        dept_outcomes[dept.id] = []
        dept_active[dept.id] = 0
        dept_departed[dept.id] = 0

    # Count active/departed per department and collect outcome ratings
    for person in company.people:
        for assignment in person.assignments:
            if assignment.end_date is None and assignment.department_id in dept_lookup:
                if person.departed:
                    dept_departed[assignment.department_id] = (
                        dept_departed.get(assignment.department_id, 0) + 1
                    )
                else:
                    dept_active[assignment.department_id] = (
                        dept_active.get(assignment.department_id, 0) + 1
                    )

    # Get this quarter's outcomes from changes
    outcomes = [c for c in changes if isinstance(c, OutcomeRecord)]
    for outcome in outcomes:
        # Map outcome to department via person's assignment
        for person in company.people:
            if person.id == outcome.person_id:
                for assignment in person.assignments:
                    if assignment.end_date is None and assignment.department_id in dept_lookup:
                        dept_outcomes[assignment.department_id].append(
                            outcome.rating.numeric
                        )
                break

    # Build scores
    scores: list[DepartmentScore] = []
    for dept in company.departments:
        ratings = dept_outcomes.get(dept.id, [])
        avg = sum(ratings) / len(ratings) if ratings else 0.0
        scores.append(
            DepartmentScore(
                department_id=dept.id,
                department_name=dept.name,
                avg_rating=round(avg, 2),
                active_count=dept_active.get(dept.id, 0),
                departed_count=dept_departed.get(dept.id, 0),
            )
        )

    return scores
