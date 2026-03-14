"""Game elements module — quarter reports, achievements, company score."""

from talentgraph.game.quarter_report import QuarterReport, generate_quarter_report
from talentgraph.game.achievements import Achievement, AchievementTracker
from talentgraph.game.company_score import CompanyScore, compute_company_score

__all__ = [
    "QuarterReport",
    "generate_quarter_report",
    "Achievement",
    "AchievementTracker",
    "CompanyScore",
    "compute_company_score",
]
