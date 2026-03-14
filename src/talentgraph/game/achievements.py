"""Achievement system — unlock milestones through simulation play.

Tracks 15 achievements across milestone, streak, and special categories.
Achievements persist across the simulation session via AchievementTracker.
"""

from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from talentgraph.ontology.enums import OutcomeRating, SkillLevel
from talentgraph.ontology.models import Company
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.state import ChangeRecord, OutcomeRecord, QuarterLabel


class AchievementCategory(str, Enum):
    MILESTONE = "milestone"
    STREAK = "streak"
    SPECIAL = "special"


class Achievement(BaseModel):
    """Definition of an achievement that can be unlocked."""

    id: str
    name: str
    name_ko: str
    description: str
    description_ko: str
    icon: str
    category: AchievementCategory
    unlocked: bool = False
    unlocked_at: str | None = None  # quarter string


# ── Achievement Definitions ──

ACHIEVEMENTS: list[Achievement] = [
    # ── Milestones ──
    Achievement(
        id="first_quarter",
        name="First Quarter",
        name_ko="첫 분기",
        description="Complete your first quarter simulation",
        description_ko="첫 분기 시뮬레이션 완료",
        icon="🎯",
        category=AchievementCategory.MILESTONE,
    ),
    Achievement(
        id="year_one",
        name="Year One",
        name_ko="첫 해",
        description="Complete 4 quarters (1 full year)",
        description_ko="4분기(1년) 완료",
        icon="📅",
        category=AchievementCategory.MILESTONE,
    ),
    Achievement(
        id="zero_departures",
        name="Zero Departures",
        name_ko="이직 제로",
        description="Complete a quarter with no departures",
        description_ko="이직 없이 분기 완료",
        icon="🛡️",
        category=AchievementCategory.MILESTONE,
    ),
    Achievement(
        id="all_stars",
        name="All Stars",
        name_ko="올스타",
        description="All active people rated Exceeds or better",
        description_ko="전원 '기대 초과' 이상 성과",
        icon="⭐",
        category=AchievementCategory.MILESTONE,
    ),
    Achievement(
        id="full_house",
        name="Full House",
        name_ko="풀 하우스",
        description="Every role has at least one person assigned",
        description_ko="모든 역할에 인원 배치 완료",
        icon="🏠",
        category=AchievementCategory.MILESTONE,
    ),
    Achievement(
        id="big_company",
        name="Big Company",
        name_ko="대기업",
        description="Have 20 or more active employees",
        description_ko="20명 이상 활성 직원 보유",
        icon="🏢",
        category=AchievementCategory.MILESTONE,
    ),
    # ── Streaks ──
    Achievement(
        id="happy_team_3",
        name="Happy Team ×3",
        name_ko="행복한 팀 ×3",
        description="Average morale above 70% for 3 consecutive quarters",
        description_ko="3분기 연속 평균 사기 70% 이상",
        icon="😊",
        category=AchievementCategory.STREAK,
    ),
    Achievement(
        id="no_burnout_3",
        name="No Burnout ×3",
        name_ko="번아웃 제로 ×3",
        description="No high burnout warnings for 3 consecutive quarters",
        description_ko="3분기 연속 고위험 번아웃 없음",
        icon="💚",
        category=AchievementCategory.STREAK,
    ),
    Achievement(
        id="growth_streak_3",
        name="Growth Streak ×3",
        name_ko="성장 연속 ×3",
        description="At least one skill growth event for 3 consecutive quarters",
        description_ko="3분기 연속 스킬 성장 발생",
        icon="📈",
        category=AchievementCategory.STREAK,
    ),
    Achievement(
        id="score_up_3",
        name="Rising Star ×3",
        name_ko="상승세 ×3",
        description="Company score increased for 3 consecutive quarters",
        description_ko="3분기 연속 회사 점수 상승",
        icon="🚀",
        category=AchievementCategory.STREAK,
    ),
    # ── Special ──
    Achievement(
        id="growth_star",
        name="Growth Star",
        name_ko="성장 스타",
        description="Someone grew 3 skill levels total",
        description_ko="누군가 총 3레벨 스킬 성장",
        icon="💪",
        category=AchievementCategory.SPECIAL,
    ),
    Achievement(
        id="turnaround",
        name="Turnaround",
        name_ko="턴어라운드",
        description="Someone recovered from morale below 30% to above 70%",
        description_ko="사기 30% 미만에서 70% 초과로 회복",
        icon="🔄",
        category=AchievementCategory.SPECIAL,
    ),
    Achievement(
        id="skill_master",
        name="Skill Master",
        name_ko="스킬 마스터",
        description="Someone reached Expert level in any skill",
        description_ko="누군가 Expert 레벨 달성",
        icon="🎓",
        category=AchievementCategory.SPECIAL,
    ),
    Achievement(
        id="perfect_score",
        name="Perfect Score",
        name_ko="만점",
        description="Company score reached 90 or above",
        description_ko="회사 점수 90점 이상 달성",
        icon="💯",
        category=AchievementCategory.SPECIAL,
    ),
    Achievement(
        id="diversity_hire",
        name="Skill Diversity",
        name_ko="스킬 다양성",
        description="Team covers 10 or more distinct skills",
        description_ko="팀이 10개 이상 다양한 스킬 보유",
        icon="🌈",
        category=AchievementCategory.SPECIAL,
    ),
]


class AchievementTracker(BaseModel):
    """Tracks achievement state across simulation quarters.

    Maintains internal streak counters and records of low-morale people
    for the turnaround achievement.
    """

    achievements: list[Achievement] = Field(
        default_factory=lambda: [a.model_copy() for a in ACHIEVEMENTS]
    )

    # Streak counters
    happy_streak: int = 0
    no_burnout_streak: int = 0
    growth_streak: int = 0
    score_streak: int = 0
    last_score: float | None = None

    # Turnaround tracking: people who had morale < 0.3
    low_morale_people: set[str] = Field(default_factory=set)  # person_id strings

    # Growth tracking: cumulative skill growth per person
    growth_counts: dict[str, int] = Field(default_factory=dict)  # person_id → total growths

    # Quarters simulated
    quarters_completed: int = 0

    def check_achievements(
        self,
        company: Company,
        quarter: QuarterLabel,
        changes: list[ChangeRecord],
        company_score: float,
    ) -> list[Achievement]:
        """Check and unlock achievements after a quarter advance.

        Args:
            company: Company state after the quarter
            quarter: The completed quarter
            changes: Change records from the quarter
            company_score: Current company total score

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked: list[Achievement] = []
        quarter_str = str(quarter)

        self.quarters_completed += 1

        active = [p for p in company.people if not p.departed]

        # ── Update tracking state ──
        departures = sum(1 for c in changes if c.change_type == "departure")
        growth_events = sum(1 for c in changes if c.change_type == "skill_growth")
        avg_morale = sum(p.morale for p in active) / len(active) if active else 0.0
        high_burnout = any(compute_burnout_risk(p) >= 0.6 for p in active)

        # Track growth per person
        for c in changes:
            if c.change_type == "skill_growth":
                pid = str(c.person_id)
                self.growth_counts[pid] = self.growth_counts.get(pid, 0) + 1

        # Track low morale people for turnaround
        for p in active:
            pid = str(p.id)
            if p.morale < 0.3:
                self.low_morale_people.add(pid)

        # Streak updates
        if avg_morale >= 0.7:
            self.happy_streak += 1
        else:
            self.happy_streak = 0

        if not high_burnout:
            self.no_burnout_streak += 1
        else:
            self.no_burnout_streak = 0

        if growth_events > 0:
            self.growth_streak += 1
        else:
            self.growth_streak = 0

        if self.last_score is not None and company_score > self.last_score:
            self.score_streak += 1
        else:
            self.score_streak = 0
        self.last_score = company_score

        # Outcome records for this quarter
        outcomes = [c for c in changes if isinstance(c, OutcomeRecord)]

        # ── Check each achievement ──

        # first_quarter
        if self.quarters_completed >= 1:
            newly_unlocked.extend(self._unlock("first_quarter", quarter_str))

        # year_one
        if self.quarters_completed >= 4:
            newly_unlocked.extend(self._unlock("year_one", quarter_str))

        # zero_departures
        if departures == 0:
            newly_unlocked.extend(self._unlock("zero_departures", quarter_str))

        # all_stars — all outcomes this quarter are exceeds or exceptional
        if outcomes and all(
            o.rating in (OutcomeRating.EXCEEDS, OutcomeRating.EXCEPTIONAL)
            for o in outcomes
        ):
            newly_unlocked.extend(self._unlock("all_stars", quarter_str))

        # full_house — every role has at least one active person
        role_ids_with_people = set()
        for p in active:
            for a in p.assignments:
                if a.end_date is None:
                    role_ids_with_people.add(a.role_id)
        if company.roles and all(r.id in role_ids_with_people for r in company.roles):
            newly_unlocked.extend(self._unlock("full_house", quarter_str))

        # big_company
        if len(active) >= 20:
            newly_unlocked.extend(self._unlock("big_company", quarter_str))

        # happy_team_3
        if self.happy_streak >= 3:
            newly_unlocked.extend(self._unlock("happy_team_3", quarter_str))

        # no_burnout_3
        if self.no_burnout_streak >= 3:
            newly_unlocked.extend(self._unlock("no_burnout_3", quarter_str))

        # growth_streak_3
        if self.growth_streak >= 3:
            newly_unlocked.extend(self._unlock("growth_streak_3", quarter_str))

        # score_up_3
        if self.score_streak >= 3:
            newly_unlocked.extend(self._unlock("score_up_3", quarter_str))

        # growth_star — someone has 3+ total skill growths
        if any(count >= 3 for count in self.growth_counts.values()):
            newly_unlocked.extend(self._unlock("growth_star", quarter_str))

        # turnaround — someone who was < 0.3 morale is now > 0.7
        for p in active:
            pid = str(p.id)
            if pid in self.low_morale_people and p.morale > 0.7:
                newly_unlocked.extend(self._unlock("turnaround", quarter_str))
                self.low_morale_people.discard(pid)
                break

        # skill_master — someone has Expert level
        for p in active:
            if any(s.level == SkillLevel.EXPERT for s in p.skills):
                newly_unlocked.extend(self._unlock("skill_master", quarter_str))
                break

        # perfect_score
        if company_score >= 90.0:
            newly_unlocked.extend(self._unlock("perfect_score", quarter_str))

        # diversity — 10+ distinct skills across active people
        all_skills = set()
        for p in active:
            for s in p.skills:
                all_skills.add(s.skill_id)
        if len(all_skills) >= 10:
            newly_unlocked.extend(self._unlock("diversity_hire", quarter_str))

        return newly_unlocked

    def _unlock(self, achievement_id: str, quarter_str: str) -> list[Achievement]:
        """Attempt to unlock an achievement. Returns list with the achievement if newly unlocked."""
        for a in self.achievements:
            if a.id == achievement_id and not a.unlocked:
                a.unlocked = True
                a.unlocked_at = quarter_str
                return [a]
        return []

    def get_unlocked(self) -> list[Achievement]:
        """Return all unlocked achievements."""
        return [a for a in self.achievements if a.unlocked]

    def get_locked(self) -> list[Achievement]:
        """Return all locked achievements."""
        return [a for a in self.achievements if not a.unlocked]

    def get_progress(self) -> dict:
        """Return achievement progress summary."""
        unlocked = len(self.get_unlocked())
        total = len(self.achievements)
        return {
            "unlocked": unlocked,
            "total": total,
            "percentage": round(unlocked / total * 100, 1) if total > 0 else 0.0,
            "quarters_completed": self.quarters_completed,
        }
