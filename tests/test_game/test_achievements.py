"""Tests for achievements module."""

import random
from uuid import uuid4

import pytest

from talentgraph.game.achievements import (
    ACHIEVEMENTS,
    Achievement,
    AchievementCategory,
    AchievementTracker,
)
from talentgraph.game.company_score import compute_company_score
from talentgraph.ontology.enums import OutcomeRating, SkillLevel
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures
from talentgraph.simulation.state import ChangeRecord, OutcomeRecord, QuarterLabel


class TestAchievementDefinitions:
    """Test the achievement definitions are valid."""

    def test_all_achievements_have_ids(self):
        assert len(ACHIEVEMENTS) == 15
        ids = [a.id for a in ACHIEVEMENTS]
        assert len(set(ids)) == 15  # all unique

    def test_all_achievements_have_bilingual_names(self):
        for a in ACHIEVEMENTS:
            assert a.name, f"Achievement {a.id} missing name"
            assert a.name_ko, f"Achievement {a.id} missing name_ko"
            assert a.description, f"Achievement {a.id} missing description"
            assert a.description_ko, f"Achievement {a.id} missing description_ko"

    def test_all_achievements_have_icons(self):
        for a in ACHIEVEMENTS:
            assert a.icon, f"Achievement {a.id} missing icon"

    def test_achievement_categories(self):
        categories = {a.category for a in ACHIEVEMENTS}
        assert AchievementCategory.MILESTONE in categories
        assert AchievementCategory.STREAK in categories
        assert AchievementCategory.SPECIAL in categories

    def test_milestone_count(self):
        milestones = [a for a in ACHIEVEMENTS if a.category == AchievementCategory.MILESTONE]
        assert len(milestones) == 6

    def test_streak_count(self):
        streaks = [a for a in ACHIEVEMENTS if a.category == AchievementCategory.STREAK]
        assert len(streaks) == 4

    def test_special_count(self):
        specials = [a for a in ACHIEVEMENTS if a.category == AchievementCategory.SPECIAL]
        assert len(specials) == 5


class TestAchievementTracker:
    """Test the AchievementTracker."""

    def test_initial_state(self):
        tracker = AchievementTracker()
        assert len(tracker.achievements) == 15
        assert all(not a.unlocked for a in tracker.achievements)
        assert tracker.quarters_completed == 0

    def test_first_quarter_unlocks(self, sample_company):
        tracker = AchievementTracker()
        quarter = QuarterLabel(year=2025, quarter=1)
        score = compute_company_score(sample_company)

        newly = tracker.check_achievements(
            sample_company, quarter, [], score.total
        )
        # Should unlock "first_quarter" and possibly others
        ids = [a.id for a in newly]
        assert "first_quarter" in ids

    def test_year_one_after_4_quarters(self, sample_company):
        tracker = AchievementTracker()
        quarter = QuarterLabel(year=2025, quarter=1)
        score = compute_company_score(sample_company)

        for i in range(4):
            q = QuarterLabel(year=2025, quarter=i + 1)
            tracker.check_achievements(sample_company, q, [], score.total)

        assert tracker.quarters_completed == 4
        unlocked_ids = [a.id for a in tracker.get_unlocked()]
        assert "year_one" in unlocked_ids

    def test_zero_departures(self, sample_company):
        tracker = AchievementTracker()
        quarter = QuarterLabel(year=2025, quarter=1)
        score = compute_company_score(sample_company)

        # No departure changes
        newly = tracker.check_achievements(
            sample_company, quarter, [], score.total
        )
        ids = [a.id for a in newly]
        assert "zero_departures" in ids

    def test_zero_departures_not_unlocked_with_departure(self, sample_company):
        tracker = AchievementTracker()
        quarter = QuarterLabel(year=2025, quarter=1)
        score = compute_company_score(sample_company)

        changes = [
            ChangeRecord(
                person_id=sample_company.people[0].id,
                person_name=sample_company.people[0].name,
                change_type="departure",
                description="Someone left",
            )
        ]
        # Unlock first to reset
        newly = tracker.check_achievements(
            sample_company, quarter, changes, score.total
        )
        ids = [a.id for a in newly]
        # zero_departures should NOT be in newly (departure happened)
        # But actually since the tracker checks departures == 0, it won't unlock
        assert "zero_departures" not in ids

    def test_all_stars_with_all_exceeds(self, sample_company):
        tracker = AchievementTracker()
        quarter = QuarterLabel(year=2025, quarter=1)
        score = compute_company_score(sample_company)

        changes = [
            OutcomeRecord(
                person_id=p.id,
                person_name=p.name,
                change_type="outcome",
                description=f"{p.name}: exceeds",
                rating=OutcomeRating.EXCEEDS,
                predicted_performance=4.0,
                role_title="Role",
                department_name="Dept",
            )
            for p in sample_company.people
            if not p.departed
        ]

        newly = tracker.check_achievements(
            sample_company, quarter, changes, score.total
        )
        ids = [a.id for a in newly]
        assert "all_stars" in ids

    def test_skill_master_with_expert(self, sample_company):
        tracker = AchievementTracker()
        quarter = QuarterLabel(year=2025, quarter=1)
        score = compute_company_score(sample_company)

        # Give someone Expert skill
        sample_company.people[0].skills[0].level = SkillLevel.EXPERT

        newly = tracker.check_achievements(
            sample_company, quarter, [], score.total
        )
        ids = [a.id for a in newly]
        assert "skill_master" in ids

    def test_happy_team_streak(self, sample_company):
        tracker = AchievementTracker()
        score = compute_company_score(sample_company)

        # Set everyone's morale high
        for p in sample_company.people:
            p.morale = 0.85
            p.departed = False

        # Run 3 quarters
        for i in range(3):
            q = QuarterLabel(year=2025, quarter=i + 1)
            tracker.check_achievements(sample_company, q, [], score.total)

        unlocked_ids = [a.id for a in tracker.get_unlocked()]
        assert "happy_team_3" in unlocked_ids

    def test_happy_team_streak_broken(self, sample_company):
        tracker = AchievementTracker()
        score = compute_company_score(sample_company)

        # Q1: high morale
        for p in sample_company.people:
            p.morale = 0.85
            p.departed = False
        tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=1), [], score.total
        )

        # Q2: low morale → breaks streak
        for p in sample_company.people:
            p.morale = 0.3
        tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=2), [], score.total
        )

        # Q3: high again
        for p in sample_company.people:
            p.morale = 0.85
        tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=3), [], score.total
        )

        assert tracker.happy_streak == 1  # reset, not 3

    def test_growth_star_cumulative(self, sample_company):
        tracker = AchievementTracker()
        score = compute_company_score(sample_company)
        person = sample_company.people[0]

        # 3 growth events for the same person
        changes = [
            ChangeRecord(
                person_id=person.id,
                person_name=person.name,
                change_type="skill_growth",
                description=f"{person.name} grew skill",
            )
            for _ in range(3)
        ]

        newly = tracker.check_achievements(
            sample_company,
            QuarterLabel(year=2025, quarter=1),
            changes,
            score.total,
        )
        ids = [a.id for a in newly]
        assert "growth_star" in ids

    def test_turnaround(self, sample_company):
        tracker = AchievementTracker()
        score = compute_company_score(sample_company)
        person = sample_company.people[0]

        # Q1: low morale — registers in tracker
        person.morale = 0.2
        tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=1), [], score.total
        )
        assert str(person.id) in tracker.low_morale_people

        # Q2: morale recovered
        person.morale = 0.8
        newly = tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=2), [], score.total
        )
        ids = [a.id for a in newly]
        assert "turnaround" in ids

    def test_perfect_score(self, sample_company):
        tracker = AchievementTracker()

        newly = tracker.check_achievements(
            sample_company,
            QuarterLabel(year=2025, quarter=1),
            [],
            95.0,  # company score above 90
        )
        ids = [a.id for a in newly]
        assert "perfect_score" in ids

    def test_get_progress(self, sample_company):
        tracker = AchievementTracker()
        score = compute_company_score(sample_company)

        tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=1), [], score.total
        )
        progress = tracker.get_progress()
        assert progress["total"] == 15
        assert progress["unlocked"] >= 1
        assert progress["quarters_completed"] == 1
        assert 0 <= progress["percentage"] <= 100

    def test_achievements_only_unlock_once(self, sample_company):
        tracker = AchievementTracker()
        score = compute_company_score(sample_company)

        # Run same quarter twice
        newly1 = tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=1), [], score.total
        )
        newly2 = tracker.check_achievements(
            sample_company, QuarterLabel(year=2025, quarter=2), [], score.total
        )

        # first_quarter should only appear in newly1
        ids1 = [a.id for a in newly1]
        ids2 = [a.id for a in newly2]
        assert "first_quarter" in ids1
        assert "first_quarter" not in ids2

    def test_serialization(self):
        tracker = AchievementTracker()
        data = tracker.model_dump()
        assert "achievements" in data
        assert len(data["achievements"]) == 15

        # Round-trip
        tracker2 = AchievementTracker.model_validate(data)
        assert len(tracker2.achievements) == 15


class TestAchievementsIntegration:
    """Integration tests with the simulation engine."""

    def test_achievements_with_engine(self, sample_company):
        """Run a few quarters with the engine and check achievements."""
        engine = SimulationEngine(
            sample_company,
            seed=42,
            features=SimulationFeatures(enhanced=True),
        )
        tracker = AchievementTracker()

        all_newly = []
        for _ in range(4):
            quarter, changes = engine.advance()
            score = compute_company_score(engine.company, changes)
            newly = tracker.check_achievements(
                engine.company, quarter, changes, score.total
            )
            all_newly.extend(newly)

        # After 4 quarters, should have unlocked at least first_quarter and year_one
        all_ids = [a.id for a in all_newly]
        assert "first_quarter" in all_ids
        assert "year_one" in all_ids
        assert tracker.quarters_completed == 4
