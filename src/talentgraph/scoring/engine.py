from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from talentgraph.ontology.graph import OntologyGraph
from talentgraph.ontology.models import Company, Department, Person, Role
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.scoring.history import compute_historical_performance
from talentgraph.scoring.level_match import compute_level_match
from talentgraph.scoring.skill_match import compute_skill_match
from talentgraph.scoring.weights import ScoringWeights


class FitResult(BaseModel):
    person_id: UUID
    person_name: str
    department_id: UUID
    department_name: str
    role_id: UUID
    role_title: str
    skill_match_score: float
    historical_score: float
    level_match_score: float
    burnout_risk_score: float
    fit_score: float
    predicted_performance: float
    breakdown: dict[str, float]


class FitScoreEngine:
    """Orchestrates scoring for a person across all available roles/departments."""

    def __init__(self, company: Company, weights: ScoringWeights | None = None) -> None:
        self.company = company
        self.graph = OntologyGraph(company)
        self.weights = weights or ScoringWeights()
        self._skill_lookup = {s.id: s for s in company.skills}
        self._role_lookup = {r.id: r for r in company.roles}

    def evaluate_person(self, person_id: UUID) -> list[FitResult]:
        """Score person against every role in every department. Returns sorted by fit_score desc."""
        person = self._get_person(person_id)
        self._inject_role_levels(person)

        results = []
        for dept in self.company.departments:
            for role_id in dept.roles:
                role = self._role_lookup.get(role_id)
                if role is None:
                    continue
                result = self._score(person, role, dept)
                results.append(result)

        return sorted(results, key=lambda r: r.fit_score, reverse=True)

    def evaluate_person_by_name(self, name: str) -> list[FitResult]:
        """Find person by name and evaluate."""
        for p in self.company.people:
            if p.name.lower() == name.lower():
                return self.evaluate_person(p.id)
        raise ValueError(f"Person not found: {name}")

    def top_n(self, results: list[FitResult], n: int = 3) -> list[FitResult]:
        return results[:n]

    def _score(self, person: Person, role: Role, department: Department) -> FitResult:
        sm = compute_skill_match(person, role, self._skill_lookup)
        hp = compute_historical_performance(person, role)
        lm = compute_level_match(person, role)
        br = compute_burnout_risk(person)

        w = self.weights
        raw = (
            w.skill_match * sm
            + w.historical_performance * hp
            + w.level_match * lm
            - w.burnout_risk * br
        )
        fit = max(0.0, min(1.0, raw))

        predicted = self._predict_performance(fit, hp)

        return FitResult(
            person_id=person.id,
            person_name=person.name,
            department_id=department.id,
            department_name=department.name,
            role_id=role.id,
            role_title=role.title,
            skill_match_score=sm,
            historical_score=hp,
            level_match_score=lm,
            burnout_risk_score=br,
            fit_score=round(fit, 4),
            predicted_performance=round(predicted, 1),
            breakdown={
                "skill_match": round(w.skill_match * sm, 4),
                "historical": round(w.historical_performance * hp, 4),
                "level_match": round(w.level_match * lm, 4),
                "burnout_penalty": round(-w.burnout_risk * br, 4),
            },
        )

    def _predict_performance(self, fit_score: float, historical_score: float) -> float:
        """Map fit_score to predicted performance on 1-5 scale, weighted by history."""
        base = 1.0 + fit_score * 4.0  # [0,1] → [1,5]
        history_adj = (historical_score - 0.5) * 0.5  # history pulls toward actual track record
        return max(1.0, min(5.0, base + history_adj))

    def _get_person(self, person_id: UUID) -> Person:
        for p in self.company.people:
            if p.id == person_id:
                return p
        raise ValueError(f"Person not found: {person_id}")

    def _inject_role_levels(self, person: Person) -> None:
        """Attach role level info to assignments for level_match scorer."""
        for assignment in person.assignments:
            role = self._role_lookup.get(assignment.role_id)
            if role:
                object.__setattr__(assignment, "_role_level", role.level)
