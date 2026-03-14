"""Company score — overall health metric (0-100).

Score = 30%×TeamPerformance + 25%×MoraleHealth + 20%×RetentionRate
      + 15%×SkillCoverage + 10%×GrowthRate
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from talentgraph.ontology.models import Company
from talentgraph.scoring.burnout import compute_burnout_risk
from talentgraph.simulation.state import ChangeRecord


class CompanyScore(BaseModel):
    """Company health score breakdown."""

    total: float = Field(description="Overall score 0-100")
    team_performance: float = Field(description="Team performance component (0-100)")
    morale_health: float = Field(description="Morale health component (0-100)")
    retention_rate: float = Field(description="Retention rate component (0-100)")
    skill_coverage: float = Field(description="Skill coverage component (0-100)")
    growth_rate: float = Field(description="Growth rate component (0-100)")


def compute_company_score(
    company: Company,
    changes: list[ChangeRecord] | None = None,
) -> CompanyScore:
    """Compute the company health score.

    Args:
        company: Current company state
        changes: Recent quarter's change records (for growth rate)
    """
    changes = changes or []
    active = [p for p in company.people if not p.departed]
    all_people = company.people

    if not active:
        return CompanyScore(
            total=0.0,
            team_performance=0.0,
            morale_health=0.0,
            retention_rate=0.0,
            skill_coverage=0.0,
            growth_rate=0.0,
        )

    # 1. Team Performance (30%) — based on average predicted performance
    # Approximate from morale + burnout (since we don't have direct performance)
    avg_morale = sum(p.morale for p in active) / len(active)
    avg_burnout = sum(compute_burnout_risk(p) for p in active) / len(active)
    team_perf = min(100.0, max(0.0, (avg_morale * 80 + (1 - avg_burnout) * 20)))

    # 2. Morale Health (25%) — percentage of team with healthy morale
    healthy = sum(1 for p in active if p.morale >= 0.5) / len(active)
    morale_health = healthy * 100

    # 3. Retention Rate (20%) — based on departed vs total
    departed_count = sum(1 for p in all_people if p.departed)
    total_count = len(all_people)
    retention = ((total_count - departed_count) / total_count * 100) if total_count > 0 else 100

    # 4. Skill Coverage (15%) — how many roles have required skills covered
    role_coverage_scores: list[float] = []
    skill_lookup = {ps.skill_id: ps for p in active for ps in p.skills}
    for role in company.roles:
        if not role.required_skills:
            role_coverage_scores.append(100.0)
            continue
        met = sum(
            1 for req in role.required_skills
            if req.skill_id in skill_lookup
            and skill_lookup[req.skill_id].level.numeric >= req.minimum_level.numeric
        )
        role_coverage_scores.append(met / len(role.required_skills) * 100)
    skill_cov = sum(role_coverage_scores) / len(role_coverage_scores) if role_coverage_scores else 0

    # 5. Growth Rate (10%) — skill growth events this quarter
    growth_events = sum(1 for c in changes if c.change_type == "skill_growth")
    decay_events = sum(1 for c in changes if c.change_type == "skill_decay")
    net_growth = growth_events - decay_events
    growth_rate = min(100.0, max(0.0, 50 + net_growth * 15))

    total = (
        0.30 * team_perf
        + 0.25 * morale_health
        + 0.20 * retention
        + 0.15 * skill_cov
        + 0.10 * growth_rate
    )

    return CompanyScore(
        total=round(total, 1),
        team_performance=round(team_perf, 1),
        morale_health=round(morale_health, 1),
        retention_rate=round(retention, 1),
        skill_coverage=round(skill_cov, 1),
        growth_rate=round(growth_rate, 1),
    )
