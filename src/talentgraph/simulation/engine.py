"""SimulationEngine: orchestrates quarter advancement, placement, rollback.

v0.3: Enhanced mode adds skill growth, morale, attrition, random events.
v0.4: SimulationConfig for all tunable parameters.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from uuid import UUID

from talentgraph.config.simulation_config import SimulationConfig
from talentgraph.ontology.models import Company, Person
from talentgraph.scoring.engine import FitScoreEngine, FitResult
from talentgraph.scoring.weights import ScoringWeights
from talentgraph.simulation.events import PlacementEvent
from talentgraph.simulation.quarter import advance_quarter, place_person
from talentgraph.simulation.enhanced_quarter import advance_quarter_enhanced
from talentgraph.simulation.state import (
    ChangeRecord,
    QuarterLabel,
    QuarterSnapshot,
    SimulationState,
)


@dataclass
class SimulationFeatures:
    """Feature flags for v0.3 enhanced simulation systems."""

    enhanced: bool = False
    growth: bool = True
    morale: bool = True
    attrition: bool = True
    events: bool = True


class SimulationEngine:
    """Manages simulation state with advance, place, rollback, and reset.

    v0.3: Set `features=SimulationFeatures(enhanced=True)` to enable
    skill growth, morale tracking, attrition, and random events.

    v0.4: Pass `config=SimulationConfig(...)` to tune all simulation
    parameters. When None, modules use their built-in defaults.
    """

    def __init__(
        self,
        company: Company,
        weights: ScoringWeights | None = None,
        seed: int | None = None,
        features: SimulationFeatures | None = None,
        config: SimulationConfig | None = None,
    ) -> None:
        self._weights = weights or ScoringWeights()
        self._state = SimulationState(initial_company=company.model_copy(deep=True))
        self._current_company = company.model_copy(deep=True)
        self._rng = random.Random(seed)
        self._features = features or SimulationFeatures()
        self._config = config

    @property
    def state(self) -> SimulationState:
        return self._state

    @property
    def company(self) -> Company:
        return self._current_company

    @property
    def current_quarter(self) -> QuarterLabel:
        return self._state.current_quarter

    @property
    def weights(self) -> ScoringWeights:
        return self._weights

    @weights.setter
    def weights(self, value: ScoringWeights) -> None:
        self._weights = value

    @property
    def history(self) -> list[QuarterSnapshot]:
        return self._state.history

    @property
    def features(self) -> SimulationFeatures:
        return self._features

    @features.setter
    def features(self, value: SimulationFeatures) -> None:
        self._features = value

    @property
    def config(self) -> SimulationConfig | None:
        return self._config

    @config.setter
    def config(self, value: SimulationConfig | None) -> None:
        self._config = value

    def advance(self) -> tuple[QuarterLabel, list[ChangeRecord]]:
        """Advance one quarter. Returns (quarter_label, changes).

        Uses enhanced mode if `features.enhanced` is True.
        """
        quarter = self._state.current_quarter

        if self._features.enhanced:
            updated_company, changes = advance_quarter_enhanced(
                self._current_company,
                quarter,
                self._weights,
                self._rng,
                enable_growth=self._features.growth,
                enable_morale=self._features.morale,
                enable_attrition=self._features.attrition,
                enable_events=self._features.events,
                config=self._config,
            )
        else:
            updated_company, changes = advance_quarter(
                self._current_company, quarter, self._weights, self._rng
            )

        snapshot = QuarterSnapshot(
            quarter=quarter,
            company=self._current_company.model_copy(deep=True),
            changes=changes,
        )
        self._state.history.append(snapshot)
        self._current_company = updated_company
        self._state.current_quarter = quarter.next()

        return quarter, changes

    def place(
        self, person_id: UUID, role_id: UUID, department_id: UUID
    ) -> PlacementEvent:
        """Place a person in a new role/department."""
        updated, event = place_person(
            self._current_company,
            person_id,
            role_id,
            department_id,
            self._state.current_quarter,
        )
        self._current_company = updated
        return event

    def preview_placement(
        self, person_id: UUID, role_id: UUID, department_id: UUID
    ) -> FitResult:
        """Preview what a person's fit would be in a new role without committing."""
        engine = FitScoreEngine(self._current_company, self._weights)
        results = engine.evaluate_person(person_id)
        match = next(
            (r for r in results if r.role_id == role_id and r.department_id == department_id),
            None,
        )
        if match is None:
            raise ValueError(f"Role/Department combination not found: {role_id}/{department_id}")
        return match

    def rollback(self, steps: int = 1) -> QuarterLabel:
        """Roll back N quarters. Returns the new current quarter."""
        if steps < 1 or steps > len(self._state.history):
            raise ValueError(
                f"Cannot rollback {steps} steps (history has {len(self._state.history)} entries)"
            )

        for _ in range(steps):
            snapshot = self._state.history.pop()

        self._current_company = snapshot.company.model_copy(deep=True)
        self._state.current_quarter = snapshot.quarter
        return self._state.current_quarter

    def reset(self) -> None:
        """Reset to initial state."""
        if self._state.initial_company is None:
            raise ValueError("No initial company state saved")
        self._current_company = self._state.initial_company.model_copy(deep=True)
        self._state.history.clear()
        self._state.current_quarter = QuarterLabel(year=2025, quarter=1)

    def evaluate_person(self, person_id: UUID) -> list[FitResult]:
        """Evaluate a person against all roles using current company state."""
        engine = FitScoreEngine(self._current_company, self._weights)
        return engine.evaluate_person(person_id)

    # ── v0.3 convenience methods ──

    def get_active_people(self) -> list[Person]:
        """Return all non-departed people."""
        return [p for p in self._current_company.people if not p.departed]

    def get_departed_people(self) -> list[Person]:
        """Return all departed people."""
        return [p for p in self._current_company.people if p.departed]

    def get_person(self, person_id: UUID) -> Person | None:
        """Get a specific person by ID."""
        for p in self._current_company.people:
            if p.id == person_id:
                return p
        return None

    def get_stats(self) -> dict:
        """Return summary statistics for the current simulation state."""
        active = self.get_active_people()
        departed = self.get_departed_people()

        avg_morale = (
            sum(p.morale for p in active) / len(active) if active else 0.0
        )
        burnout_warnings = sum(
            1 for p in active if any(
                a.end_date is None for a in p.assignments
            ) and p.morale < 0.4
        )

        return {
            "total_people": len(self._current_company.people),
            "active_people": len(active),
            "departed_people": len(departed),
            "average_morale": round(avg_morale, 3),
            "burnout_warnings": burnout_warnings,
            "quarters_simulated": len(self._state.history),
            "current_quarter": str(self._state.current_quarter),
            "enhanced_mode": self._features.enhanced,
        }
