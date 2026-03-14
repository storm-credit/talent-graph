"""Tests for quarter_report module."""

import random

import pytest

from talentgraph.game.quarter_report import (
    QuarterReport,
    generate_quarter_report,
    PersonHighlight,
    Headline,
    DepartmentScore,
)
from talentgraph.simulation.state import ChangeRecord, OutcomeRecord, QuarterLabel
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures
from talentgraph.ontology.enums import OutcomeRating


class TestQuarterReportModels:
    """Test Pydantic models for quarter report."""

    def test_person_highlight(self):
        from uuid import uuid4

        h = PersonHighlight(
            person_id=uuid4(),
            person_name="Alice",
            highlight_type="mvp",
            description="MVP",
            description_ko="MVP",
            metric_value=5.0,
        )
        assert h.highlight_type == "mvp"

    def test_headline(self):
        h = Headline(
            icon="🎯", text="Skill grew", text_ko="스킬 성장", category="positive"
        )
        assert h.category == "positive"

    def test_department_score(self):
        from uuid import uuid4

        ds = DepartmentScore(
            department_id=uuid4(),
            department_name="Engineering",
            avg_rating=4.2,
            active_count=5,
            departed_count=0,
        )
        assert ds.avg_rating == 4.2

    def test_quarter_report_model(self):
        from talentgraph.game.company_score import CompanyScore

        report = QuarterReport(
            quarter="2025-Q1",
            company_score=CompanyScore(
                total=72.5,
                team_performance=80.0,
                morale_health=75.0,
                retention_rate=90.0,
                skill_coverage=60.0,
                growth_rate=50.0,
            ),
        )
        assert report.quarter == "2025-Q1"
        assert report.company_score.total == 72.5


class TestGenerateQuarterReport:
    """Test the generate_quarter_report function."""

    def test_basic_report_generation(self, sample_company):
        """Generate a report from a basic company with no changes."""
        quarter = QuarterLabel(year=2025, quarter=1)
        report = generate_quarter_report(sample_company, quarter, [])
        assert report.quarter == "2025-Q1"
        assert report.total_active > 0
        assert report.company_score.total >= 0

    def test_report_with_outcome_changes(self, sample_company):
        """Generate a report with outcome records."""
        quarter = QuarterLabel(year=2025, quarter=1)
        person = sample_company.people[0]

        changes = [
            OutcomeRecord(
                person_id=person.id,
                person_name=person.name,
                change_type="outcome",
                description=f"{person.name}: exceeds in Senior Data Engineer",
                rating=OutcomeRating.EXCEEDS,
                predicted_performance=4.0,
                role_title="Senior Data Engineer",
                department_name="Data Engineering",
            )
        ]

        report = generate_quarter_report(sample_company, quarter, changes)
        assert report.mvp is not None
        assert report.mvp.person_name == person.name

    def test_report_with_growth_headlines(self, sample_company):
        """Skill growth events appear as headlines."""
        quarter = QuarterLabel(year=2025, quarter=1)
        changes = [
            ChangeRecord(
                person_id=sample_company.people[0].id,
                person_name=sample_company.people[0].name,
                change_type="skill_growth",
                description="Alice grew Python to Advanced",
            )
        ]
        report = generate_quarter_report(sample_company, quarter, changes)
        assert len(report.headlines) >= 1
        assert any(h.category == "positive" for h in report.headlines)

    def test_report_with_departure_headlines(self, sample_company):
        """Departure events appear as headlines."""
        quarter = QuarterLabel(year=2025, quarter=1)
        person = sample_company.people[0]
        person.departed = True

        changes = [
            ChangeRecord(
                person_id=person.id,
                person_name=person.name,
                change_type="departure",
                description=f"{person.name} has departed the company",
            )
        ]
        report = generate_quarter_report(sample_company, quarter, changes)
        assert report.departures_this_quarter == 1
        assert any(h.category == "negative" for h in report.headlines)

    def test_report_warnings_high_burnout(self, sample_company):
        """People with high burnout appear in warnings."""
        quarter = QuarterLabel(year=2025, quarter=1)
        # Dave has long tenure → high burnout risk
        dave = next(p for p in sample_company.people if p.name == "Dave Lee")
        dave.morale = 0.2  # low morale to ensure warning

        report = generate_quarter_report(sample_company, quarter, [])
        # Check if Dave appears in warnings (either burnout or low morale)
        warning_names = [w.person_name for w in report.warnings]
        assert "Dave Lee" in warning_names

    def test_report_score_delta(self, sample_company):
        """Score delta is computed from previous score."""
        quarter = QuarterLabel(year=2025, quarter=1)
        report = generate_quarter_report(
            sample_company, quarter, [], previous_score=60.0
        )
        assert report.previous_score == 60.0
        assert report.score_delta is not None
        expected_delta = round(report.company_score.total - 60.0, 1)
        assert abs(report.score_delta - expected_delta) < 0.2

    def test_report_no_previous_score(self, sample_company):
        """No delta when no previous score."""
        quarter = QuarterLabel(year=2025, quarter=1)
        report = generate_quarter_report(sample_company, quarter, [])
        assert report.score_delta is None

    def test_report_department_scores(self, sample_company):
        """Department scores are computed."""
        quarter = QuarterLabel(year=2025, quarter=1)
        report = generate_quarter_report(sample_company, quarter, [])
        assert len(report.department_scores) == len(sample_company.departments)

    def test_report_avg_morale(self, sample_company):
        """Average morale is computed from active people."""
        for p in sample_company.people:
            p.morale = 0.8
            p.departed = False
        quarter = QuarterLabel(year=2025, quarter=1)
        report = generate_quarter_report(sample_company, quarter, [])
        assert abs(report.avg_morale - 0.8) < 0.01

    def test_headlines_limited_to_8(self, sample_company):
        """Headlines are capped at 8."""
        from uuid import uuid4

        quarter = QuarterLabel(year=2025, quarter=1)
        changes = [
            ChangeRecord(
                person_id=uuid4(),
                person_name=f"Person {i}",
                change_type="skill_growth",
                description=f"Person {i} grew skill",
            )
            for i in range(15)
        ]
        report = generate_quarter_report(sample_company, quarter, changes)
        assert len(report.headlines) <= 8


class TestQuarterReportIntegration:
    """Integration tests with simulation engine."""

    def test_report_after_engine_advance(self, sample_company):
        """Generate a report from actual engine output."""
        engine = SimulationEngine(
            sample_company,
            seed=42,
            features=SimulationFeatures(enhanced=True),
        )
        quarter, changes = engine.advance()
        report = generate_quarter_report(engine.company, quarter, changes)

        assert report.quarter == str(quarter)
        assert report.total_active >= 0
        assert report.company_score.total >= 0

    def test_report_serialization(self, sample_company):
        """Report can be serialized to JSON (for API)."""
        quarter = QuarterLabel(year=2025, quarter=1)
        report = generate_quarter_report(sample_company, quarter, [])
        data = report.model_dump()
        assert "quarter" in data
        assert "company_score" in data
        assert "headlines" in data

    def test_multi_quarter_reports(self, sample_company):
        """Multiple quarters produce valid reports with deltas."""
        engine = SimulationEngine(
            sample_company,
            seed=42,
            features=SimulationFeatures(enhanced=True),
        )

        prev_score = None
        for _ in range(3):
            quarter, changes = engine.advance()
            report = generate_quarter_report(
                engine.company, quarter, changes, previous_score=prev_score
            )
            assert report.quarter == str(quarter)
            if prev_score is not None:
                assert report.score_delta is not None
            prev_score = report.company_score.total
