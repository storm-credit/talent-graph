"""Tests for random events system (v0.3)."""

from __future__ import annotations

import random
from datetime import date

import pytest

from talentgraph.data.seed import create_sample_company
from talentgraph.ontology.enums import EventType
from talentgraph.simulation.random_events import (
    COMPANY_EVENTS,
    INDIVIDUAL_EVENTS,
    SimulationEvent,
    process_random_events,
)


@pytest.fixture()
def company():
    return create_sample_company()


class TestCompanyEvents:
    def test_market_boom_boosts_morale(self, company):
        """Market boom should raise everyone's morale."""
        rng = random.Random(42)
        for p in company.people:
            p.morale = 0.5

        found_boom = False
        for seed in range(200):
            c = company.model_copy(deep=True)
            changes, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            boom_events = [e for e in events if e.event_type == EventType.MARKET_BOOM]
            if boom_events:
                found_boom = True
                for p in c.people:
                    if not p.departed:
                        assert p.morale >= 0.5
                break

        assert found_boom, "Expected to find a MARKET_BOOM in 200 attempts"

    def test_market_downturn_reduces_morale(self, company):
        """Market downturn should lower everyone's morale."""
        rng = random.Random(42)
        for p in company.people:
            p.morale = 0.5

        found_downturn = False
        for seed in range(200):
            c = company.model_copy(deep=True)
            changes, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            downturn_events = [e for e in events if e.event_type == EventType.MARKET_DOWNTURN]
            if downturn_events:
                found_downturn = True
                for p in c.people:
                    if not p.departed:
                        assert p.morale <= 0.5
                break

        assert found_downturn, "Expected to find a MARKET_DOWNTURN in 200 attempts"


class TestIndividualEvents:
    def test_certification_can_boost_skill(self, company):
        """Certification event should potentially boost a skill level."""
        found_cert = False
        for seed in range(200):
            c = company.model_copy(deep=True)
            changes, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            cert_changes = [ch for ch in changes if ch.change_type == "certification"]
            if cert_changes:
                found_cert = True
                break

        assert found_cert, "Expected certification event in 200 attempts"

    def test_personal_issue_drops_morale(self, company):
        """Personal issue event should reduce morale."""
        found_issue = False
        for seed in range(200):
            c = company.model_copy(deep=True)
            for p in c.people:
                p.morale = 0.8
            changes, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            issue_events = [e for e in events if e.event_type == EventType.PERSONAL_ISSUE]
            if issue_events:
                found_issue = True
                person = next(
                    p for p in c.people
                    if p.id == issue_events[0].affected_person_id
                )
                assert person.morale < 0.8
                break

        assert found_issue

    def test_mentoring_boosts_morale(self, company):
        """Mentoring should boost morale slightly."""
        found_mentoring = False
        for seed in range(200):
            c = company.model_copy(deep=True)
            for p in c.people:
                p.morale = 0.5
            changes, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            mentor_events = [e for e in events if e.event_type == EventType.MENTORING]
            if mentor_events:
                found_mentoring = True
                person = next(
                    p for p in c.people
                    if p.id == mentor_events[0].affected_person_id
                )
                assert person.morale >= 0.5
                break

        assert found_mentoring


class TestEventRecords:
    def test_returns_change_records_and_events(self, company):
        """Should return both ChangeRecords and SimulationEvents."""
        all_changes = []
        all_events = []
        for seed in range(50):
            c = company.model_copy(deep=True)
            changes, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            all_changes.extend(changes)
            all_events.extend(events)

        assert len(all_changes) > 0
        assert len(all_events) > 0

    def test_company_event_has_change_record(self, company):
        """Company events should produce change records."""
        found = False
        for seed in range(200):
            c = company.model_copy(deep=True)
            changes, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            company_changes = [ch for ch in changes if ch.change_type == "event"]
            if company_changes:
                found = True
                break

        assert found

    def test_departed_people_skip_individual_events(self, company):
        """Departed people should not receive individual events."""
        for p in company.people:
            p.departed = True

        all_events = []
        for seed in range(100):
            c = company.model_copy(deep=True)
            _, events = process_random_events(c, date(2025, 4, 1), random.Random(seed))
            individual_events = [e for e in events if e.affected_person_id is not None]
            all_events.extend(individual_events)

        assert len(all_events) == 0
