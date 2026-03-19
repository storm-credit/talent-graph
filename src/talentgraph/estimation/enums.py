"""Enums for the estimation module."""

from __future__ import annotations

from enum import Enum


class ProjectDifficulty(int, Enum):
    """How hard the project is — affects signal strength."""

    TRIVIAL = 1
    EASY = 2
    MODERATE = 3
    HARD = 4
    EXTREME = 5


class ProjectStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectResult(int, Enum):
    """Outcome of a person's contribution to a project."""

    FAILURE = 1
    PARTIAL = 2
    SUCCESS = 3
    EXCELLENT = 4


class ProjectRole(str, Enum):
    """Role a person plays in a project — affects signal noise."""

    LEAD = "lead"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"


class SkillTrend(str, Enum):
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
