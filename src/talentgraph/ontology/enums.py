from enum import Enum


class SkillLevel(str, Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

    @property
    def numeric(self) -> int:
        return {"novice": 1, "beginner": 2, "intermediate": 3, "advanced": 4, "expert": 5}[
            self.value
        ]

    def next_level(self) -> "SkillLevel | None":
        """Return the next higher skill level, or None if already expert."""
        order = list(SkillLevel)
        idx = order.index(self)
        return order[idx + 1] if idx < len(order) - 1 else None

    def prev_level(self) -> "SkillLevel | None":
        """Return the next lower skill level, or None if already novice."""
        order = list(SkillLevel)
        idx = order.index(self)
        return order[idx - 1] if idx > 0 else None


class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    COMMUNICATION = "communication"
    ANALYTICAL = "analytical"
    DOMAIN = "domain"


class TraitType(str, Enum):
    MBTI = "mbti"
    COLLABORATION_STYLE = "collaboration_style"
    WORK_PREFERENCE = "work_preference"
    CULTURE = "culture"


class EventType(str, Enum):
    """Types of random simulation events."""

    MARKET_BOOM = "market_boom"
    MARKET_DOWNTURN = "market_downturn"
    REORG = "reorg"
    CERTIFICATION = "certification"
    PERSONAL_ISSUE = "personal_issue"
    MENTORING = "mentoring"
    PROMOTION_PASSED = "promotion_passed"


class OutcomeRating(str, Enum):
    EXCEPTIONAL = "exceptional"
    EXCEEDS = "exceeds"
    MEETS = "meets"
    BELOW = "below"
    UNSATISFACTORY = "unsatisfactory"

    @property
    def numeric(self) -> int:
        return {"exceptional": 5, "exceeds": 4, "meets": 3, "below": 2, "unsatisfactory": 1}[
            self.value
        ]
