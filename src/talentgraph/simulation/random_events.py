"""Random events system for simulation richness.

Each quarter, roll for company-wide and individual events.
Events affect morale, skills, burnout, and team dynamics.
"""

from __future__ import annotations

import random
from datetime import date
from uuid import UUID

from talentgraph.config.simulation_config import EventConfig
from talentgraph.ontology.enums import EventType, SkillLevel
from talentgraph.ontology.models import Company, Person
from talentgraph.simulation.state import ChangeRecord


# ── Event definitions ──

# Company-wide events: probability per quarter
COMPANY_EVENTS = {
    EventType.MARKET_BOOM: 0.05,  # 5% chance: boosts morale, increases attrition risk
    EventType.MARKET_DOWNTURN: 0.05,  # 5% chance: lowers morale, reduces attrition
    EventType.REORG: 0.03,  # 3% chance: shuffles stress, morale hit
}

# Individual events: probability per person per quarter
INDIVIDUAL_EVENTS = {
    EventType.CERTIFICATION: 0.08,  # 8% chance: skill boost
    EventType.PERSONAL_ISSUE: 0.05,  # 5% chance: morale/performance dip
    EventType.MENTORING: 0.06,  # 6% chance: mentored by senior, skill boost
}


class SimulationEvent:
    """Represents an event that occurred during simulation."""

    def __init__(
        self,
        event_type: EventType,
        description: str,
        affected_person_id: UUID | None = None,
        affected_person_name: str | None = None,
    ):
        self.event_type = event_type
        self.description = description
        self.affected_person_id = affected_person_id
        self.affected_person_name = affected_person_name


def _build_company_event_probs(
    config: EventConfig | None = None,
) -> dict[EventType, float]:
    """Build company event probabilities from config or defaults."""
    if config:
        return {
            EventType.MARKET_BOOM: config.market_boom_probability,
            EventType.MARKET_DOWNTURN: config.market_downturn_probability,
            EventType.REORG: config.reorg_probability,
        }
    return COMPANY_EVENTS


def _build_individual_event_probs(
    config: EventConfig | None = None,
) -> dict[EventType, float]:
    """Build individual event probabilities from config or defaults."""
    if config:
        return {
            EventType.CERTIFICATION: config.certification_probability,
            EventType.PERSONAL_ISSUE: config.personal_issue_probability,
            EventType.MENTORING: config.mentoring_probability,
        }
    return INDIVIDUAL_EVENTS


def process_random_events(
    company: Company,
    quarter_date: date,
    rng: random.Random,
    config: EventConfig | None = None,
) -> tuple[list[ChangeRecord], list[SimulationEvent]]:
    """Roll and apply random events. Mutates company in place.

    Returns (change_records, events).
    """
    changes: list[ChangeRecord] = []
    events: list[SimulationEvent] = []

    company_probs = _build_company_event_probs(config)
    individual_probs = _build_individual_event_probs(config)

    # ── Company-wide events ──
    for event_type, prob in company_probs.items():
        if rng.random() < prob:
            evt, evt_changes = _apply_company_event(
                event_type, company, rng, config
            )
            events.append(evt)
            changes.extend(evt_changes)

    # ── Individual events ──
    active_people = [p for p in company.people if not p.departed]
    for person in active_people:
        for event_type, prob in individual_probs.items():
            if rng.random() < prob:
                evt, evt_changes = _apply_individual_event(
                    event_type, person, company, rng, config
                )
                events.append(evt)
                changes.extend(evt_changes)

    return changes, events


def _apply_company_event(
    event_type: EventType,
    company: Company,
    rng: random.Random,
    config: EventConfig | None = None,
) -> tuple[SimulationEvent, list[ChangeRecord]]:
    """Apply a company-wide event."""
    changes: list[ChangeRecord] = []

    if event_type == EventType.MARKET_BOOM:
        lo, hi = config.market_boom_morale_range if config else (0.02, 0.06)
        for p in company.people:
            if not p.departed:
                p.morale = min(1.0, p.morale + rng.uniform(lo, hi))
        evt = SimulationEvent(EventType.MARKET_BOOM, "Market boom: industry demand rising")

    elif event_type == EventType.MARKET_DOWNTURN:
        lo, hi = config.market_downturn_morale_range if config else (0.03, 0.08)
        for p in company.people:
            if not p.departed:
                p.morale = max(0.0, p.morale - rng.uniform(lo, hi))
        evt = SimulationEvent(
            EventType.MARKET_DOWNTURN, "Market downturn: budget pressures rising"
        )

    elif event_type == EventType.REORG:
        lo, hi = config.reorg_morale_range if config else (0.02, 0.05)
        for p in company.people:
            if not p.departed:
                p.morale = max(0.0, p.morale - rng.uniform(lo, hi))
        evt = SimulationEvent(EventType.REORG, "Company reorganization announced")

    else:
        evt = SimulationEvent(event_type, f"Company event: {event_type.value}")

    changes.append(
        ChangeRecord(
            person_id=company.people[0].id if company.people else __import__("uuid").uuid4(),
            person_name="Company",
            change_type="event",
            description=evt.description,
        )
    )

    return evt, changes


def _apply_individual_event(
    event_type: EventType,
    person: Person,
    company: Company,
    rng: random.Random,
    config: EventConfig | None = None,
) -> tuple[SimulationEvent, list[ChangeRecord]]:
    """Apply an individual event."""
    changes: list[ChangeRecord] = []

    if event_type == EventType.CERTIFICATION:
        # Random skill gets a boost
        if person.skills:
            skill = rng.choice(person.skills)
            if skill.level != SkillLevel.EXPERT:
                new_level = skill.level.next_level()
                if new_level:
                    old_level = skill.level
                    skill.level = new_level
                    skill_name = _skill_name(skill.skill_id, company)
                    changes.append(
                        ChangeRecord(
                            person_id=person.id,
                            person_name=person.name,
                            change_type="certification",
                            description=(
                                f"{person.name} earned certification: "
                                f"{skill_name} {old_level.value} → {new_level.value}"
                            ),
                            old_value=old_level.value,
                            new_value=new_level.value,
                        )
                    )
        evt = SimulationEvent(
            EventType.CERTIFICATION,
            f"{person.name} earned a professional certification",
            person.id,
            person.name,
        )

    elif event_type == EventType.PERSONAL_ISSUE:
        lo, hi = config.personal_issue_morale_range if config else (0.05, 0.15)
        person.morale = max(0.0, person.morale - rng.uniform(lo, hi))
        changes.append(
            ChangeRecord(
                person_id=person.id,
                person_name=person.name,
                change_type="personal_event",
                description=f"{person.name}: personal issue affecting performance",
                old_value=None,
                new_value=f"morale={person.morale:.2f}",
            )
        )
        evt = SimulationEvent(
            EventType.PERSONAL_ISSUE,
            f"{person.name} dealing with personal issues",
            person.id,
            person.name,
        )

    elif event_type == EventType.MENTORING:
        morale_boost = config.mentoring_morale_boost if config else 0.05
        learning_accel = config.mentoring_learning_acceleration if config else 2
        person.morale = min(1.0, person.morale + morale_boost)
        if person.skills:
            skill = rng.choice(person.skills)
            skill.quarters_active += learning_accel  # simulates accelerated learning
        changes.append(
            ChangeRecord(
                person_id=person.id,
                person_name=person.name,
                change_type="mentoring",
                description=f"{person.name} received mentoring from senior colleague",
            )
        )
        evt = SimulationEvent(
            EventType.MENTORING,
            f"{person.name} being mentored",
            person.id,
            person.name,
        )

    else:
        evt = SimulationEvent(
            event_type, f"{person.name}: {event_type.value}", person.id, person.name
        )

    return evt, changes


def _skill_name(skill_id, company: Company) -> str:
    for s in company.skills:
        if s.id == skill_id:
            return s.name
    return "Unknown"
