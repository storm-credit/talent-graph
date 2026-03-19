"""Company profile & template endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from talentgraph.api.deps import get_engine, reset_engine
from talentgraph.company.factory import (
    build_config_for_profile,
    create_company_from_template,
)
from talentgraph.company.profile import CompanyProfile, IndustryType
from talentgraph.company.templates import get_all_templates, get_template
from talentgraph.simulation.engine import SimulationEngine, SimulationFeatures

router = APIRouter(prefix="/api/company-profile", tags=["company-profile"])


@router.get("/templates")
def list_templates():
    """Return all available industry templates (summary only)."""
    templates = get_all_templates()
    return [
        {
            "industry": t.industry.value,
            "name_en": t.name_en,
            "name_ko": t.name_ko,
            "description_en": t.description_en,
            "description_ko": t.description_ko,
            "default_culture": t.default_culture.value,
            "departments": [d.name for d in t.departments],
            "roles": [r.title for r in t.roles],
            "skills": [s.name for s in t.skills],
        }
        for t in templates
    ]


@router.get("/templates/{industry}")
def get_template_detail(industry: str):
    """Return detailed template for a specific industry."""
    try:
        ind = IndustryType(industry)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown industry: {industry}")

    t = get_template(ind)
    return {
        "industry": t.industry.value,
        "name_en": t.name_en,
        "name_ko": t.name_ko,
        "description_en": t.description_en,
        "description_ko": t.description_ko,
        "default_culture": t.default_culture.value,
        "skills": [
            {"name": s.name, "category": s.category.value, "description": s.description}
            for s in t.skills
        ],
        "roles": [
            {
                "title": r.title,
                "level": r.level,
                "max_headcount": r.max_headcount,
                "required_skills": [
                    {"skill_name": rs.skill_name, "min_level": rs.min_level, "weight": rs.weight}
                    for rs in r.required_skills
                ],
            }
            for r in t.roles
        ],
        "departments": [
            {"name": d.name, "role_titles": d.role_titles, "culture_traits": d.culture_traits}
            for d in t.departments
        ],
        "config_overrides": {
            "attrition_base_rate": t.config_overrides.attrition_base_rate,
            "growth_gap_1_prob": t.config_overrides.growth_gap_1_prob,
            "morale_mean_reversion_target": t.config_overrides.morale_mean_reversion_target,
            "morale_stagnation_penalty": t.config_overrides.morale_stagnation_penalty,
            "event_reorg_probability": t.config_overrides.event_reorg_probability,
        },
    }


@router.post("/create")
def create_company(profile: CompanyProfile):
    """Create a new company from a template. Resets the simulation."""
    from talentgraph.api import deps

    company = create_company_from_template(profile, seed=42)
    config = build_config_for_profile(profile)

    # Reset all singletons (engine + achievement tracker + score history)
    reset_engine()

    # Replace the engine singleton with new company
    new_engine = SimulationEngine(
        company,
        seed=42,
        features=SimulationFeatures(enhanced=True),
        config=config,
    )
    deps._engine = new_engine

    return {
        "name": company.name,
        "industry": profile.industry.value,
        "people_count": len(company.people),
        "department_count": len(company.departments),
        "role_count": len(company.roles),
        "skill_count": len(company.skills),
    }
