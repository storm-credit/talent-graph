"""Recommendation engine — wraps FitScoreEngine to provide actionable suggestions.

Provides:
- best_roles_for_person: Top N roles for a person, ranked by fit
- best_candidates_for_role: Top N people for a role, ranked by fit
- placement_matrix: Full person × role fit score matrix
- strengths/gaps analysis for each recommendation
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from talentgraph.ontology.enums import SkillLevel
from talentgraph.ontology.models import Company, Department, Person, Role
from talentgraph.scoring.engine import FitResult, FitScoreEngine
from talentgraph.scoring.weights import ScoringWeights


class SkillGap(BaseModel):
    """A gap between required and current skill level."""

    skill_name: str
    required_level: str
    current_level: str
    gap: int  # positive = person needs improvement


class Recommendation(BaseModel):
    """A single person→role or role→person recommendation."""

    person_id: UUID
    person_name: str
    role_id: UUID
    role_title: str
    department_id: UUID
    department_name: str
    fit_score: float
    predicted_performance: float
    strengths: list[str] = Field(default_factory=list)
    gaps: list[SkillGap] = Field(default_factory=list)
    growth_potential: str = "medium"  # "high" / "medium" / "low"
    recommendation_en: str = ""
    recommendation_ko: str = ""


class PlacementCell(BaseModel):
    """A single cell in the placement matrix."""

    person_id: UUID
    person_name: str
    role_id: UUID
    role_title: str
    department_id: UUID
    department_name: str
    fit_score: float


class RecommendationEngine:
    """Wraps FitScoreEngine to provide placement recommendations."""

    def __init__(
        self,
        company: Company,
        weights: ScoringWeights | None = None,
    ) -> None:
        self._company = company
        self._weights = weights or ScoringWeights()
        self._engine = FitScoreEngine(company, self._weights)
        self._skill_lookup = {s.id: s for s in company.skills}
        self._role_lookup = {r.id: r for r in company.roles}
        self._dept_lookup = {d.id: d for d in company.departments}

    def best_roles_for_person(
        self,
        person_id: UUID,
        top_n: int = 3,
    ) -> list[Recommendation]:
        """Return top N role recommendations for a person."""
        person = self._get_person(person_id)
        if person is None:
            return []

        results = self._engine.evaluate_person(person_id)
        results.sort(key=lambda r: r.fit_score, reverse=True)

        recs: list[Recommendation] = []
        for result in results[:top_n]:
            role = self._role_lookup.get(result.role_id)
            dept = self._dept_lookup.get(result.department_id)
            if not role or not dept:
                continue

            strengths, gaps = self._analyze_fit(person, role)
            growth = self._assess_growth_potential(person, role)

            rec = Recommendation(
                person_id=person.id,
                person_name=person.name,
                role_id=role.id,
                role_title=role.title,
                department_id=dept.id,
                department_name=dept.name,
                fit_score=round(result.fit_score, 3),
                predicted_performance=round(result.predicted_performance, 2),
                strengths=strengths,
                gaps=gaps,
                growth_potential=growth,
                recommendation_en=self._build_recommendation_en(
                    person, role, result.fit_score, strengths, gaps
                ),
                recommendation_ko=self._build_recommendation_ko(
                    person, role, result.fit_score, strengths, gaps
                ),
            )
            recs.append(rec)

        return recs

    def best_candidates_for_role(
        self,
        role_id: UUID,
        department_id: UUID,
        top_n: int = 5,
    ) -> list[Recommendation]:
        """Return top N candidate recommendations for a role."""
        role = self._role_lookup.get(role_id)
        dept = self._dept_lookup.get(department_id)
        if not role or not dept:
            return []

        candidates: list[tuple[Person, FitResult]] = []
        for person in self._company.people:
            if person.departed:
                continue
            results = self._engine.evaluate_person(person.id)
            match = next(
                (r for r in results if r.role_id == role_id and r.department_id == department_id),
                None,
            )
            if match:
                candidates.append((person, match))

        candidates.sort(key=lambda x: x[1].fit_score, reverse=True)

        recs: list[Recommendation] = []
        for person, result in candidates[:top_n]:
            strengths, gaps = self._analyze_fit(person, role)
            growth = self._assess_growth_potential(person, role)

            rec = Recommendation(
                person_id=person.id,
                person_name=person.name,
                role_id=role.id,
                role_title=role.title,
                department_id=dept.id,
                department_name=dept.name,
                fit_score=round(result.fit_score, 3),
                predicted_performance=round(result.predicted_performance, 2),
                strengths=strengths,
                gaps=gaps,
                growth_potential=growth,
                recommendation_en=self._build_recommendation_en(
                    person, role, result.fit_score, strengths, gaps
                ),
                recommendation_ko=self._build_recommendation_ko(
                    person, role, result.fit_score, strengths, gaps
                ),
            )
            recs.append(rec)

        return recs

    def placement_matrix(self) -> list[PlacementCell]:
        """Return full person × role fit score matrix."""
        cells: list[PlacementCell] = []
        for person in self._company.people:
            if person.departed:
                continue
            results = self._engine.evaluate_person(person.id)
            for result in results:
                role = self._role_lookup.get(result.role_id)
                dept = self._dept_lookup.get(result.department_id)
                if role and dept:
                    cells.append(
                        PlacementCell(
                            person_id=person.id,
                            person_name=person.name,
                            role_id=role.id,
                            role_title=role.title,
                            department_id=dept.id,
                            department_name=dept.name,
                            fit_score=round(result.fit_score, 3),
                        )
                    )
        return cells

    # ── Private helpers ──

    def _get_person(self, person_id: UUID) -> Person | None:
        for p in self._company.people:
            if p.id == person_id:
                return p
        return None

    def _analyze_fit(
        self,
        person: Person,
        role: Role,
    ) -> tuple[list[str], list[SkillGap]]:
        """Analyze strengths and gaps for a person→role match."""
        person_skills = {ps.skill_id: ps for ps in person.skills}
        strengths: list[str] = []
        gaps: list[SkillGap] = []

        for req in role.required_skills:
            skill = self._skill_lookup.get(req.skill_id)
            skill_name = skill.name if skill else "Unknown"
            ps = person_skills.get(req.skill_id)

            if ps is None:
                gaps.append(
                    SkillGap(
                        skill_name=skill_name,
                        required_level=req.minimum_level.value,
                        current_level="none",
                        gap=req.minimum_level.numeric,
                    )
                )
            elif ps.level.numeric >= req.minimum_level.numeric:
                strengths.append(
                    f"{skill_name} {ps.level.value.title()}"
                )
            else:
                gaps.append(
                    SkillGap(
                        skill_name=skill_name,
                        required_level=req.minimum_level.value,
                        current_level=ps.level.value,
                        gap=req.minimum_level.numeric - ps.level.numeric,
                    )
                )

        return strengths, gaps

    def _assess_growth_potential(self, person: Person, role: Role) -> str:
        """Assess growth potential based on person's potential and learning rate."""
        if person.potential >= 0.8 and person.learning_rate >= 1.2:
            return "high"
        elif person.potential >= 0.6 and person.learning_rate >= 0.8:
            return "medium"
        else:
            return "low"

    def _build_recommendation_en(
        self,
        person: Person,
        role: Role,
        fit_score: float,
        strengths: list[str],
        gaps: list[SkillGap],
    ) -> str:
        """Build English recommendation text."""
        pct = int(fit_score * 100)
        parts = [f"{person.name} is a {pct}% fit for {role.title}."]
        if strengths:
            parts.append(f"Strengths: {', '.join(strengths[:3])}.")
        if gaps:
            gap_names = [g.skill_name for g in gaps[:2]]
            parts.append(f"Needs improvement in: {', '.join(gap_names)}.")
        return " ".join(parts)

    def _build_recommendation_ko(
        self,
        person: Person,
        role: Role,
        fit_score: float,
        strengths: list[str],
        gaps: list[SkillGap],
    ) -> str:
        """Build Korean recommendation text."""
        pct = int(fit_score * 100)
        parts = [f"{person.name}의 {role.title} 적합도: {pct}%."]
        if strengths:
            parts.append(f"강점: {', '.join(strengths[:3])}.")
        if gaps:
            gap_names = [g.skill_name for g in gaps[:2]]
            parts.append(f"보완 필요: {', '.join(gap_names)}.")
        return " ".join(parts)
