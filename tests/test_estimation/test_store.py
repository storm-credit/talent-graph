"""Tests for EstimationStore."""

from uuid import uuid4

from talentgraph.estimation.enums import (
    ProjectDifficulty,
    ProjectResult,
    ProjectRole,
    ProjectStatus,
)
from talentgraph.estimation.store import EstimationStore


class TestEstimationStore:
    def setup_method(self):
        self.store = EstimationStore()
        self.skill_ids = [uuid4() for _ in range(3)]
        self.person_id = uuid4()

    def test_initialize_prior(self):
        est = self.store.initialize_prior(
            self.person_id, self.skill_ids[0], "Senior Developer", 5.0
        )
        assert est.mu > 3.0
        assert est.sigma > 0
        assert est.update_count == 0

    def test_initialize_person(self):
        estimates = self.store.initialize_person(
            self.person_id, self.skill_ids, "주니어 개발자", 1.0
        )
        assert len(estimates) == 3
        assert all(e.mu < 3.0 for e in estimates)

    def test_initialize_idempotent(self):
        est1 = self.store.initialize_prior(
            self.person_id, self.skill_ids[0], "Senior", 5.0
        )
        est2 = self.store.initialize_prior(
            self.person_id, self.skill_ids[0], "Junior", 1.0  # different params
        )
        assert est1.mu == est2.mu  # Should not overwrite

    def test_add_project(self):
        project = self.store.add_project(
            name="Website Redesign",
            difficulty=ProjectDifficulty.HARD,
            required_skill_ids=self.skill_ids[:2],
        )
        assert project.name == "Website Redesign"
        assert project.difficulty == ProjectDifficulty.HARD
        assert len(project.required_skill_ids) == 2

    def test_assign_person(self):
        project = self.store.add_project(
            "Test", ProjectDifficulty.MODERATE, self.skill_ids
        )
        assignment = self.store.assign_person(
            project.id, self.person_id, ProjectRole.LEAD
        )
        assert assignment is not None
        assert assignment.role_in_project == ProjectRole.LEAD

    def test_assign_duplicate_ignored(self):
        project = self.store.add_project(
            "Test", ProjectDifficulty.MODERATE, self.skill_ids
        )
        a1 = self.store.assign_person(project.id, self.person_id)
        a2 = self.store.assign_person(project.id, self.person_id)
        assert a1.id == a2.id

    def test_record_outcome_updates_estimates(self):
        project = self.store.add_project(
            "Test Project",
            ProjectDifficulty.HARD,
            self.skill_ids[:2],
        )
        self.store.assign_person(project.id, self.person_id, ProjectRole.LEAD)

        # Initialize priors first
        self.store.initialize_person(
            self.person_id, self.skill_ids[:2], "사원", 1.0
        )

        updated = self.store.record_outcome(
            project.id, self.person_id, ProjectResult.SUCCESS
        )
        assert len(updated) == 2
        for est in updated:
            assert est.update_count == 1
            assert est.confidence > 0

    def test_record_outcome_auto_initializes(self):
        """If no prior exists, auto-initialize with neutral prior."""
        project = self.store.add_project(
            "Test", ProjectDifficulty.MODERATE, [self.skill_ids[0]]
        )
        updated = self.store.record_outcome(
            project.id, self.person_id, ProjectResult.SUCCESS
        )
        assert len(updated) == 1
        assert updated[0].update_count == 1

    def test_record_outcome_marks_completed(self):
        project = self.store.add_project(
            "Test", ProjectDifficulty.MODERATE, self.skill_ids[:1]
        )
        self.store.record_outcome(project.id, self.person_id, ProjectResult.SUCCESS)
        assert self.store.get_project(project.id).status == ProjectStatus.COMPLETED

    def test_delete_project(self):
        project = self.store.add_project(
            "Test", ProjectDifficulty.EASY, self.skill_ids[:1]
        )
        assert self.store.delete_project(project.id)
        assert self.store.get_project(project.id) is None

    def test_get_estimates_for_person(self):
        self.store.initialize_person(
            self.person_id, self.skill_ids, "과장", 7.0
        )
        estimates = self.store.get_estimates_for_person(self.person_id)
        assert len(estimates) == 3

    def test_full_workflow(self):
        """End-to-end: init → project → assign → outcome → check estimates."""
        person_id = uuid4()
        skills = [uuid4(), uuid4()]

        # 1. Initialize priors
        self.store.initialize_person(person_id, skills, "Junior Developer", 2.0)

        # 2. Create project
        project = self.store.add_project(
            "API Migration",
            ProjectDifficulty.HARD,
            skills,
        )

        # 3. Assign person
        self.store.assign_person(project.id, person_id, ProjectRole.CONTRIBUTOR)

        # 4. Record excellent outcome
        updated = self.store.record_outcome(
            project.id, person_id, ProjectResult.EXCELLENT
        )

        # 5. Check: skills should have risen from Junior level
        for est in updated:
            assert est.mu > 2.5  # Should have improved
            assert est.confidence > 0
            assert est.update_count == 1
