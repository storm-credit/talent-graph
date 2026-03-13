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
