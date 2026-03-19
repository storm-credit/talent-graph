"""In-memory store for estimation data (projects, outcomes, estimates)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from .bayesian import compute_confidence, update_estimate
from .enums import ProjectDifficulty, ProjectResult, ProjectRole, ProjectStatus, SkillTrend
from .models import (
    EstimateSnapshot,
    Project,
    ProjectAssignment,
    ProjectOutcome,
    SkillEstimate,
)
from .prior import dreyfus_prior


class EstimationStore:
    """Manages all estimation-related state."""

    def __init__(self) -> None:
        self.projects: dict[UUID, Project] = {}
        self.assignments: dict[UUID, list[ProjectAssignment]] = {}  # project_id → assignments
        self.outcomes: list[ProjectOutcome] = []
        self.estimates: dict[tuple[UUID, UUID], SkillEstimate] = {}  # (person_id, skill_id)

    # ── Prior initialization ──────────────────────────────────────────

    def initialize_prior(
        self,
        person_id: UUID,
        skill_id: UUID,
        title: str,
        years_experience: float,
    ) -> SkillEstimate:
        """Initialize a skill estimate from job title + experience (Dreyfus prior)."""
        key = (person_id, skill_id)
        if key in self.estimates:
            return self.estimates[key]

        mu, sigma = dreyfus_prior(title, years_experience)
        estimate = SkillEstimate(
            person_id=person_id,
            skill_id=skill_id,
            mu=mu,
            sigma=sigma,
            confidence=compute_confidence(sigma),
            trend=SkillTrend.STABLE,
            update_count=0,
            last_updated=datetime.now(),
            history=[EstimateSnapshot(mu=mu, sigma=sigma, timestamp=datetime.now())],
        )
        self.estimates[key] = estimate
        return estimate

    def initialize_person(
        self,
        person_id: UUID,
        skill_ids: list[UUID],
        title: str,
        years_experience: float,
    ) -> list[SkillEstimate]:
        """Initialize all skill estimates for a person."""
        return [
            self.initialize_prior(person_id, sid, title, years_experience)
            for sid in skill_ids
        ]

    # ── Project CRUD ──────────────────────────────────────────────────

    def add_project(
        self,
        name: str,
        difficulty: ProjectDifficulty,
        required_skill_ids: list[UUID],
        start_date: str | None = None,
        end_date: str | None = None,
        description: str = "",
    ) -> Project:
        from datetime import date

        project = Project(
            id=uuid4(),
            name=name,
            description=description,
            difficulty=difficulty,
            required_skill_ids=required_skill_ids,
            start_date=date.fromisoformat(start_date) if start_date else date.today(),
            end_date=date.fromisoformat(end_date) if end_date else None,
            status=ProjectStatus.PLANNED,
        )
        self.projects[project.id] = project
        self.assignments[project.id] = []
        return project

    def get_project(self, project_id: UUID) -> Project | None:
        return self.projects.get(project_id)

    def list_projects(self) -> list[Project]:
        return sorted(self.projects.values(), key=lambda p: p.created_at, reverse=True)

    def update_project(self, project_id: UUID, **kwargs) -> Project | None:
        project = self.projects.get(project_id)
        if not project:
            return None
        updated = project.model_copy(update=kwargs)
        self.projects[project_id] = updated
        return updated

    def delete_project(self, project_id: UUID) -> bool:
        if project_id not in self.projects:
            return False
        del self.projects[project_id]
        self.assignments.pop(project_id, None)
        self.outcomes = [o for o in self.outcomes if o.project_id != project_id]
        return True

    # ── Assignments ───────────────────────────────────────────────────

    def assign_person(
        self,
        project_id: UUID,
        person_id: UUID,
        role: ProjectRole = ProjectRole.CONTRIBUTOR,
    ) -> ProjectAssignment | None:
        if project_id not in self.projects:
            return None

        # Don't duplicate
        existing = self.assignments.get(project_id, [])
        for a in existing:
            if a.person_id == person_id:
                return a

        assignment = ProjectAssignment(
            id=uuid4(),
            project_id=project_id,
            person_id=person_id,
            role_in_project=role,
        )
        self.assignments.setdefault(project_id, []).append(assignment)
        return assignment

    def get_assignments(self, project_id: UUID) -> list[ProjectAssignment]:
        return self.assignments.get(project_id, [])

    def get_person_role(self, project_id: UUID, person_id: UUID) -> ProjectRole:
        """Get the role of a person in a specific project."""
        for a in self.assignments.get(project_id, []):
            if a.person_id == person_id:
                return a.role_in_project
        return ProjectRole.CONTRIBUTOR

    # ── Outcomes & Bayesian Update ────────────────────────────────────

    def record_outcome(
        self,
        project_id: UUID,
        person_id: UUID,
        result: ProjectResult,
        notes: str = "",
    ) -> list[SkillEstimate]:
        """Record a project outcome and update all affected skill estimates.

        Returns the list of updated SkillEstimates.
        """
        project = self.projects.get(project_id)
        if not project:
            return []

        # Record the outcome
        outcome = ProjectOutcome(
            id=uuid4(),
            project_id=project_id,
            person_id=person_id,
            result=result,
            notes=notes,
        )
        self.outcomes.append(outcome)

        # Get person's role in this project
        role = self.get_person_role(project_id, person_id)

        # Update estimates for each required skill
        updated: list[SkillEstimate] = []
        for skill_id in project.required_skill_ids:
            key = (person_id, skill_id)
            estimate = self.estimates.get(key)
            if estimate is None:
                # Auto-initialize with neutral prior if not yet initialized
                estimate = SkillEstimate(
                    person_id=person_id,
                    skill_id=skill_id,
                    mu=3.0,
                    sigma=1.5,
                    confidence=0.0,
                )
                self.estimates[key] = estimate

            new_estimate = update_estimate(estimate, result, project.difficulty, role)
            self.estimates[key] = new_estimate
            updated.append(new_estimate)

        # Mark project as completed if not already
        if project.status != ProjectStatus.COMPLETED:
            self.projects[project_id] = project.model_copy(
                update={"status": ProjectStatus.COMPLETED}
            )

        return updated

    # ── Query ─────────────────────────────────────────────────────────

    def get_estimates_for_person(self, person_id: UUID) -> list[SkillEstimate]:
        """Get all skill estimates for a person (the scout report data)."""
        return [
            est for (pid, _), est in self.estimates.items()
            if pid == person_id
        ]

    def get_estimate(self, person_id: UUID, skill_id: UUID) -> SkillEstimate | None:
        return self.estimates.get((person_id, skill_id))

    def get_outcomes_for_person(self, person_id: UUID) -> list[ProjectOutcome]:
        return [o for o in self.outcomes if o.person_id == person_id]

    def get_outcomes_for_project(self, project_id: UUID) -> list[ProjectOutcome]:
        return [o for o in self.outcomes if o.project_id == project_id]
