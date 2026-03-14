"""Company profile models — industry, culture, growth stage.

Based on Cameron & Quinn's Competing Values Framework for culture types
and standard industry classification for industry templates.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class IndustryType(str, Enum):
    """Industry classification for company templates."""

    TECH_STARTUP = "tech_startup"
    ENTERPRISE_IT = "enterprise_it"
    CONSULTING = "consulting"
    MANUFACTURING = "manufacturing"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"


class GrowthStage(str, Enum):
    """Company growth stage affects headcount, role levels, churn."""

    EARLY = "early"  # < 30 people, flat hierarchy
    GROWTH = "growth"  # 30-100, rapid hiring
    MATURE = "mature"  # 100+, stable processes
    ENTERPRISE = "enterprise"  # 500+, complex hierarchy


class CultureType(str, Enum):
    """Cameron & Quinn Competing Values Framework.

    Each culture type modifies simulation parameters differently.
    """

    CLAN = "clan"  # Collaborative, mentoring, family-like
    ADHOCRACY = "adhocracy"  # Innovative, risk-taking, dynamic
    MARKET = "market"  # Competitive, results-oriented
    HIERARCHY = "hierarchy"  # Structured, efficient, stable


class CompanyProfile(BaseModel):
    """Describes a company's identity beyond just its org chart.

    Used by the factory to generate appropriate departments, roles,
    skills, and people — and to override simulation config parameters.
    """

    industry: IndustryType = Field(
        description="Industry sector of the company.",
    )
    growth_stage: GrowthStage = Field(
        default=GrowthStage.GROWTH,
        description="Current growth stage.",
    )
    culture_type: CultureType = Field(
        default=CultureType.ADHOCRACY,
        description="Organizational culture type (Cameron & Quinn).",
    )
    name: str = Field(
        default="My Company",
        description="Company display name.",
    )
    num_people: int = Field(
        default=15,
        ge=3,
        le=200,
        description="Target number of people to generate.",
    )

    # Descriptive metadata
    description_en: str = Field(
        default="",
        description="English description of this company profile.",
    )
    description_ko: str = Field(
        default="",
        description="Korean description of this company profile.",
    )
