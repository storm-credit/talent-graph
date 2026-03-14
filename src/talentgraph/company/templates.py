"""Industry-specific templates for company generation.

Each template defines:
- Departments with culture traits
- Roles with skill requirements and levels
- Skills across categories
- SimulationConfig overrides for industry-specific behavior
"""

from __future__ import annotations

from dataclasses import dataclass, field

from talentgraph.company.profile import CultureType, GrowthStage, IndustryType
from talentgraph.ontology.enums import SkillCategory


@dataclass
class SkillTemplate:
    """Template for a skill to be created."""

    name: str
    category: SkillCategory
    description: str = ""


@dataclass
class RoleSkillReq:
    """Skill requirement for a role template."""

    skill_name: str  # resolved to ID at generation time
    min_level: int  # 1-5 (NOVICE to EXPERT)
    weight: int = 3  # importance 1-5
    critical: bool = False


@dataclass
class RoleTemplate:
    """Template for a role to be created."""

    title: str
    level: int  # 1-10
    required_skills: list[RoleSkillReq] = field(default_factory=list)
    max_headcount: int = 3


@dataclass
class DepartmentTemplate:
    """Template for a department with its roles."""

    name: str
    role_titles: list[str]  # references RoleTemplate.title
    culture_traits: list[str] = field(default_factory=list)


@dataclass
class ConfigOverrides:
    """Simulation config overrides for this industry."""

    attrition_base_rate: float | None = None
    growth_gap_1_prob: float | None = None
    morale_mean_reversion_target: float | None = None
    morale_stagnation_penalty: float | None = None
    event_reorg_probability: float | None = None


@dataclass
class IndustryTemplate:
    """Complete template for generating a company in a specific industry."""

    industry: IndustryType
    name_en: str
    name_ko: str
    description_en: str
    description_ko: str
    default_culture: CultureType
    skills: list[SkillTemplate]
    roles: list[RoleTemplate]
    departments: list[DepartmentTemplate]
    config_overrides: ConfigOverrides = field(default_factory=ConfigOverrides)

    # Name pools for random person generation
    first_names: list[str] = field(default_factory=list)
    last_names: list[str] = field(default_factory=list)


# ── Shared name pools ──

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Henry",
    "Ivy", "Jack", "Kate", "Leo", "Mia", "Nick", "Olivia", "Paul",
    "Quinn", "Ruby", "Sam", "Tina", "Uma", "Vince", "Wendy", "Xander",
    "Yuna", "Zach", "Aria", "Brian", "Clara", "Daniel",
]

LAST_NAMES = [
    "Chen", "Park", "Kim", "Lee", "Wang", "Johnson", "Smith", "Brown",
    "Garcia", "Martinez", "Taylor", "Anderson", "Thomas", "Wilson",
    "Moore", "Jackson", "White", "Harris", "Clark", "Lewis",
    "Young", "Hall", "Allen", "King", "Wright", "Scott", "Green",
    "Adams", "Baker", "Nelson",
]


# ── Industry Templates ──


def _tech_startup_template() -> IndustryTemplate:
    skills = [
        SkillTemplate("Python", SkillCategory.TECHNICAL, "Python programming"),
        SkillTemplate("JavaScript", SkillCategory.TECHNICAL, "Frontend/backend JS"),
        SkillTemplate("Cloud Infrastructure", SkillCategory.TECHNICAL, "AWS/GCP/Azure"),
        SkillTemplate("Machine Learning", SkillCategory.TECHNICAL, "ML/AI systems"),
        SkillTemplate("System Design", SkillCategory.TECHNICAL, "Architecture design"),
        SkillTemplate("Data Analysis", SkillCategory.ANALYTICAL, "Data-driven decisions"),
        SkillTemplate("Product Thinking", SkillCategory.ANALYTICAL, "Product sense"),
        SkillTemplate("Team Leadership", SkillCategory.LEADERSHIP, "Leading small teams"),
        SkillTemplate("Communication", SkillCategory.COMMUNICATION, "Cross-team communication"),
        SkillTemplate("Agile/Scrum", SkillCategory.DOMAIN, "Agile methodology"),
    ]
    roles = [
        RoleTemplate("Junior Engineer", 3, [
            RoleSkillReq("Python", 2, 4, True),
            RoleSkillReq("JavaScript", 2, 3),
            RoleSkillReq("Agile/Scrum", 1, 2),
        ], max_headcount=5),
        RoleTemplate("Senior Engineer", 6, [
            RoleSkillReq("Python", 4, 5, True),
            RoleSkillReq("System Design", 3, 4, True),
            RoleSkillReq("Cloud Infrastructure", 3, 3),
            RoleSkillReq("Communication", 2, 2),
        ], max_headcount=4),
        RoleTemplate("Tech Lead", 7, [
            RoleSkillReq("System Design", 4, 5, True),
            RoleSkillReq("Team Leadership", 3, 4, True),
            RoleSkillReq("Python", 4, 3),
            RoleSkillReq("Communication", 3, 3),
        ], max_headcount=2),
        RoleTemplate("Data Scientist", 5, [
            RoleSkillReq("Machine Learning", 3, 5, True),
            RoleSkillReq("Python", 3, 4, True),
            RoleSkillReq("Data Analysis", 3, 4),
        ], max_headcount=3),
        RoleTemplate("Product Manager", 6, [
            RoleSkillReq("Product Thinking", 4, 5, True),
            RoleSkillReq("Data Analysis", 3, 4),
            RoleSkillReq("Communication", 3, 3),
            RoleSkillReq("Agile/Scrum", 3, 3),
        ], max_headcount=2),
        RoleTemplate("Engineering Manager", 8, [
            RoleSkillReq("Team Leadership", 4, 5, True),
            RoleSkillReq("System Design", 3, 4),
            RoleSkillReq("Communication", 4, 4),
            RoleSkillReq("Agile/Scrum", 3, 2),
        ], max_headcount=2),
    ]
    departments = [
        DepartmentTemplate("Engineering", ["Junior Engineer", "Senior Engineer", "Tech Lead"], ["innovation", "speed"]),
        DepartmentTemplate("Data", ["Data Scientist", "Junior Engineer"], ["analytical", "research"]),
        DepartmentTemplate("Product", ["Product Manager"], ["user-focused", "agile"]),
        DepartmentTemplate("Management", ["Engineering Manager", "Tech Lead"], ["leadership", "strategy"]),
    ]
    return IndustryTemplate(
        industry=IndustryType.TECH_STARTUP,
        name_en="Tech Startup",
        name_ko="테크 스타트업",
        description_en="Fast-paced technology startup with flat hierarchy and rapid iteration.",
        description_ko="빠른 반복과 수평적 조직의 기술 스타트업.",
        default_culture=CultureType.ADHOCRACY,
        skills=skills,
        roles=roles,
        departments=departments,
        config_overrides=ConfigOverrides(
            attrition_base_rate=0.03,  # 50% higher turnover
            growth_gap_1_prob=0.20,  # faster skill growth
        ),
        first_names=FIRST_NAMES,
        last_names=LAST_NAMES,
    )


def _enterprise_it_template() -> IndustryTemplate:
    skills = [
        SkillTemplate("Java", SkillCategory.TECHNICAL, "Enterprise Java development"),
        SkillTemplate("SQL/Database", SkillCategory.TECHNICAL, "Database management"),
        SkillTemplate("Cloud Infrastructure", SkillCategory.TECHNICAL, "AWS/GCP/Azure"),
        SkillTemplate("Security", SkillCategory.TECHNICAL, "IT security & compliance"),
        SkillTemplate("System Design", SkillCategory.TECHNICAL, "Enterprise architecture"),
        SkillTemplate("Project Management", SkillCategory.LEADERSHIP, "Project delivery"),
        SkillTemplate("Team Leadership", SkillCategory.LEADERSHIP, "Managing teams"),
        SkillTemplate("Stakeholder Management", SkillCategory.COMMUNICATION, "Executive communication"),
        SkillTemplate("Data Analysis", SkillCategory.ANALYTICAL, "Business intelligence"),
        SkillTemplate("ITIL/DevOps", SkillCategory.DOMAIN, "IT service management"),
    ]
    roles = [
        RoleTemplate("Junior Developer", 3, [
            RoleSkillReq("Java", 2, 4, True),
            RoleSkillReq("SQL/Database", 2, 3),
        ], max_headcount=6),
        RoleTemplate("Senior Developer", 6, [
            RoleSkillReq("Java", 4, 5, True),
            RoleSkillReq("System Design", 3, 4),
            RoleSkillReq("SQL/Database", 3, 3),
            RoleSkillReq("Security", 2, 3),
        ], max_headcount=4),
        RoleTemplate("Solution Architect", 8, [
            RoleSkillReq("System Design", 5, 5, True),
            RoleSkillReq("Cloud Infrastructure", 4, 4, True),
            RoleSkillReq("Stakeholder Management", 3, 3),
        ], max_headcount=2),
        RoleTemplate("IT Manager", 7, [
            RoleSkillReq("Team Leadership", 4, 5, True),
            RoleSkillReq("Project Management", 4, 4, True),
            RoleSkillReq("ITIL/DevOps", 3, 3),
            RoleSkillReq("Stakeholder Management", 3, 3),
        ], max_headcount=2),
        RoleTemplate("DBA", 5, [
            RoleSkillReq("SQL/Database", 4, 5, True),
            RoleSkillReq("Security", 3, 4),
            RoleSkillReq("Data Analysis", 2, 3),
        ], max_headcount=2),
        RoleTemplate("DevOps Engineer", 5, [
            RoleSkillReq("Cloud Infrastructure", 4, 5, True),
            RoleSkillReq("ITIL/DevOps", 3, 4),
            RoleSkillReq("Security", 3, 3),
        ], max_headcount=3),
    ]
    departments = [
        DepartmentTemplate("Development", ["Junior Developer", "Senior Developer"], ["structured", "quality"]),
        DepartmentTemplate("Infrastructure", ["DevOps Engineer", "DBA"], ["reliability", "process"]),
        DepartmentTemplate("Architecture", ["Solution Architect"], ["standards", "governance"]),
        DepartmentTemplate("IT Management", ["IT Manager"], ["leadership", "planning"]),
    ]
    return IndustryTemplate(
        industry=IndustryType.ENTERPRISE_IT,
        name_en="Enterprise IT",
        name_ko="대기업 IT",
        description_en="Large enterprise IT organization with structured processes and governance.",
        description_ko="체계적인 프로세스와 거버넌스를 갖춘 대기업 IT 조직.",
        default_culture=CultureType.HIERARCHY,
        skills=skills,
        roles=roles,
        departments=departments,
        config_overrides=ConfigOverrides(
            attrition_base_rate=0.015,  # lower turnover
            morale_stagnation_penalty=-0.01,  # less stagnation sensitivity
        ),
        first_names=FIRST_NAMES,
        last_names=LAST_NAMES,
    )


def _consulting_template() -> IndustryTemplate:
    skills = [
        SkillTemplate("Business Analysis", SkillCategory.ANALYTICAL, "Strategic business analysis"),
        SkillTemplate("Data Analysis", SkillCategory.ANALYTICAL, "Quantitative analysis"),
        SkillTemplate("Presentation", SkillCategory.COMMUNICATION, "Client presentations"),
        SkillTemplate("Client Management", SkillCategory.COMMUNICATION, "Client relationships"),
        SkillTemplate("Problem Solving", SkillCategory.ANALYTICAL, "Structured problem solving"),
        SkillTemplate("Industry Knowledge", SkillCategory.DOMAIN, "Sector expertise"),
        SkillTemplate("Project Management", SkillCategory.LEADERSHIP, "Engagement delivery"),
        SkillTemplate("Team Leadership", SkillCategory.LEADERSHIP, "Team management"),
        SkillTemplate("Excel/Modeling", SkillCategory.TECHNICAL, "Financial modeling"),
        SkillTemplate("Strategy", SkillCategory.DOMAIN, "Strategic planning"),
    ]
    roles = [
        RoleTemplate("Analyst", 3, [
            RoleSkillReq("Business Analysis", 2, 4, True),
            RoleSkillReq("Excel/Modeling", 2, 4),
            RoleSkillReq("Data Analysis", 2, 3),
        ], max_headcount=6),
        RoleTemplate("Consultant", 5, [
            RoleSkillReq("Business Analysis", 3, 5, True),
            RoleSkillReq("Presentation", 3, 4),
            RoleSkillReq("Problem Solving", 3, 4, True),
            RoleSkillReq("Client Management", 2, 3),
        ], max_headcount=4),
        RoleTemplate("Senior Consultant", 7, [
            RoleSkillReq("Problem Solving", 4, 5, True),
            RoleSkillReq("Client Management", 4, 4, True),
            RoleSkillReq("Project Management", 3, 4),
            RoleSkillReq("Strategy", 3, 3),
        ], max_headcount=3),
        RoleTemplate("Manager", 8, [
            RoleSkillReq("Team Leadership", 4, 5, True),
            RoleSkillReq("Client Management", 4, 4, True),
            RoleSkillReq("Strategy", 4, 4),
            RoleSkillReq("Project Management", 4, 3),
        ], max_headcount=2),
        RoleTemplate("Partner", 10, [
            RoleSkillReq("Strategy", 5, 5, True),
            RoleSkillReq("Client Management", 5, 5, True),
            RoleSkillReq("Team Leadership", 4, 4),
            RoleSkillReq("Industry Knowledge", 5, 4),
        ], max_headcount=1),
    ]
    departments = [
        DepartmentTemplate("Strategy", ["Analyst", "Consultant", "Senior Consultant"], ["analytical", "fast-paced"]),
        DepartmentTemplate("Technology Advisory", ["Consultant", "Senior Consultant"], ["technical", "advisory"]),
        DepartmentTemplate("Leadership", ["Manager", "Partner"], ["client-focused", "business-development"]),
    ]
    return IndustryTemplate(
        industry=IndustryType.CONSULTING,
        name_en="Consulting Firm",
        name_ko="컨설팅 펌",
        description_en="Professional services firm with up-or-out culture and client focus.",
        description_ko="클라이언트 중심의 전문 서비스 기업.",
        default_culture=CultureType.MARKET,
        skills=skills,
        roles=roles,
        departments=departments,
        config_overrides=ConfigOverrides(
            attrition_base_rate=0.04,  # highest turnover
            morale_stagnation_penalty=-0.03,  # high stagnation sensitivity
        ),
        first_names=FIRST_NAMES,
        last_names=LAST_NAMES,
    )


def _manufacturing_template() -> IndustryTemplate:
    skills = [
        SkillTemplate("Process Engineering", SkillCategory.TECHNICAL, "Manufacturing process design"),
        SkillTemplate("Quality Control", SkillCategory.TECHNICAL, "QA/QC systems"),
        SkillTemplate("Safety Management", SkillCategory.DOMAIN, "Workplace safety"),
        SkillTemplate("Supply Chain", SkillCategory.DOMAIN, "Supply chain management"),
        SkillTemplate("Lean/Six Sigma", SkillCategory.ANALYTICAL, "Process improvement"),
        SkillTemplate("Equipment Maintenance", SkillCategory.TECHNICAL, "Machinery upkeep"),
        SkillTemplate("Team Leadership", SkillCategory.LEADERSHIP, "Shop floor leadership"),
        SkillTemplate("ERP Systems", SkillCategory.TECHNICAL, "Enterprise resource planning"),
        SkillTemplate("Communication", SkillCategory.COMMUNICATION, "Cross-functional communication"),
        SkillTemplate("Problem Solving", SkillCategory.ANALYTICAL, "Root cause analysis"),
    ]
    roles = [
        RoleTemplate("Technician", 3, [
            RoleSkillReq("Equipment Maintenance", 2, 4, True),
            RoleSkillReq("Safety Management", 2, 4, True),
        ], max_headcount=6),
        RoleTemplate("Process Engineer", 5, [
            RoleSkillReq("Process Engineering", 3, 5, True),
            RoleSkillReq("Lean/Six Sigma", 3, 4),
            RoleSkillReq("Quality Control", 3, 3),
        ], max_headcount=4),
        RoleTemplate("Quality Manager", 6, [
            RoleSkillReq("Quality Control", 4, 5, True),
            RoleSkillReq("Lean/Six Sigma", 3, 4),
            RoleSkillReq("Problem Solving", 3, 3),
            RoleSkillReq("Communication", 3, 3),
        ], max_headcount=2),
        RoleTemplate("Supply Chain Manager", 7, [
            RoleSkillReq("Supply Chain", 4, 5, True),
            RoleSkillReq("ERP Systems", 3, 4),
            RoleSkillReq("Team Leadership", 3, 3),
        ], max_headcount=2),
        RoleTemplate("Plant Manager", 9, [
            RoleSkillReq("Team Leadership", 4, 5, True),
            RoleSkillReq("Process Engineering", 3, 4),
            RoleSkillReq("Safety Management", 4, 4, True),
            RoleSkillReq("Communication", 3, 3),
        ], max_headcount=1),
    ]
    departments = [
        DepartmentTemplate("Production", ["Technician", "Process Engineer"], ["efficiency", "safety"]),
        DepartmentTemplate("Quality", ["Quality Manager"], ["standards", "continuous-improvement"]),
        DepartmentTemplate("Supply Chain", ["Supply Chain Manager"], ["logistics", "cost-optimization"]),
        DepartmentTemplate("Plant Management", ["Plant Manager"], ["leadership", "safety-culture"]),
    ]
    return IndustryTemplate(
        industry=IndustryType.MANUFACTURING,
        name_en="Manufacturing",
        name_ko="제조업",
        description_en="Manufacturing company with focus on process efficiency and safety.",
        description_ko="공정 효율성과 안전에 중점을 둔 제조 기업.",
        default_culture=CultureType.HIERARCHY,
        skills=skills,
        roles=roles,
        departments=departments,
        config_overrides=ConfigOverrides(
            attrition_base_rate=0.012,  # lowest turnover
            growth_gap_1_prob=0.10,  # slower skill growth
        ),
        first_names=FIRST_NAMES,
        last_names=LAST_NAMES,
    )


def _finance_template() -> IndustryTemplate:
    skills = [
        SkillTemplate("Financial Analysis", SkillCategory.ANALYTICAL, "Financial modeling & analysis"),
        SkillTemplate("Risk Management", SkillCategory.ANALYTICAL, "Risk assessment"),
        SkillTemplate("Regulatory Compliance", SkillCategory.DOMAIN, "Financial regulations"),
        SkillTemplate("Trading Systems", SkillCategory.TECHNICAL, "Trading platforms"),
        SkillTemplate("Data Analysis", SkillCategory.ANALYTICAL, "Quantitative data work"),
        SkillTemplate("Client Relations", SkillCategory.COMMUNICATION, "Client advisory"),
        SkillTemplate("Team Leadership", SkillCategory.LEADERSHIP, "Team management"),
        SkillTemplate("Portfolio Management", SkillCategory.DOMAIN, "Investment portfolio"),
        SkillTemplate("Python", SkillCategory.TECHNICAL, "Quantitative programming"),
        SkillTemplate("Communication", SkillCategory.COMMUNICATION, "Professional communication"),
    ]
    roles = [
        RoleTemplate("Junior Analyst", 3, [
            RoleSkillReq("Financial Analysis", 2, 4, True),
            RoleSkillReq("Data Analysis", 2, 4),
            RoleSkillReq("Python", 2, 3),
        ], max_headcount=5),
        RoleTemplate("Senior Analyst", 6, [
            RoleSkillReq("Financial Analysis", 4, 5, True),
            RoleSkillReq("Risk Management", 3, 4),
            RoleSkillReq("Data Analysis", 3, 3),
            RoleSkillReq("Regulatory Compliance", 2, 3),
        ], max_headcount=4),
        RoleTemplate("Portfolio Manager", 7, [
            RoleSkillReq("Portfolio Management", 4, 5, True),
            RoleSkillReq("Risk Management", 4, 4, True),
            RoleSkillReq("Client Relations", 3, 4),
            RoleSkillReq("Financial Analysis", 4, 3),
        ], max_headcount=2),
        RoleTemplate("Risk Officer", 7, [
            RoleSkillReq("Risk Management", 5, 5, True),
            RoleSkillReq("Regulatory Compliance", 4, 5, True),
            RoleSkillReq("Communication", 3, 3),
        ], max_headcount=2),
        RoleTemplate("Managing Director", 9, [
            RoleSkillReq("Team Leadership", 4, 5, True),
            RoleSkillReq("Client Relations", 5, 5, True),
            RoleSkillReq("Portfolio Management", 4, 4),
            RoleSkillReq("Communication", 4, 3),
        ], max_headcount=1),
    ]
    departments = [
        DepartmentTemplate("Research", ["Junior Analyst", "Senior Analyst"], ["analytical", "quantitative"]),
        DepartmentTemplate("Trading", ["Senior Analyst", "Portfolio Manager"], ["performance", "speed"]),
        DepartmentTemplate("Risk & Compliance", ["Risk Officer"], ["regulatory", "governance"]),
        DepartmentTemplate("Management", ["Managing Director"], ["leadership", "client-focus"]),
    ]
    return IndustryTemplate(
        industry=IndustryType.FINANCE,
        name_en="Finance",
        name_ko="금융",
        description_en="Financial services company focused on analysis, risk management, and compliance.",
        description_ko="분석, 리스크 관리, 규정 준수에 중점을 둔 금융 서비스 기업.",
        default_culture=CultureType.MARKET,
        skills=skills,
        roles=roles,
        departments=departments,
        config_overrides=ConfigOverrides(
            attrition_base_rate=0.02,
            morale_mean_reversion_target=0.55,  # slightly higher baseline
        ),
        first_names=FIRST_NAMES,
        last_names=LAST_NAMES,
    )


def _healthcare_template() -> IndustryTemplate:
    skills = [
        SkillTemplate("Clinical Knowledge", SkillCategory.DOMAIN, "Medical/clinical expertise"),
        SkillTemplate("Patient Care", SkillCategory.COMMUNICATION, "Patient interaction"),
        SkillTemplate("Medical Records", SkillCategory.TECHNICAL, "EHR/EMR systems"),
        SkillTemplate("Regulatory Compliance", SkillCategory.DOMAIN, "Healthcare regulations"),
        SkillTemplate("Research Methods", SkillCategory.ANALYTICAL, "Clinical research"),
        SkillTemplate("Team Leadership", SkillCategory.LEADERSHIP, "Clinical team leadership"),
        SkillTemplate("Data Analysis", SkillCategory.ANALYTICAL, "Health data analytics"),
        SkillTemplate("Quality Improvement", SkillCategory.ANALYTICAL, "Process improvement"),
        SkillTemplate("Communication", SkillCategory.COMMUNICATION, "Healthcare communication"),
        SkillTemplate("Safety Protocols", SkillCategory.DOMAIN, "Patient safety"),
    ]
    roles = [
        RoleTemplate("Clinical Assistant", 3, [
            RoleSkillReq("Clinical Knowledge", 2, 4, True),
            RoleSkillReq("Patient Care", 2, 4, True),
            RoleSkillReq("Medical Records", 1, 3),
        ], max_headcount=6),
        RoleTemplate("Clinician", 6, [
            RoleSkillReq("Clinical Knowledge", 4, 5, True),
            RoleSkillReq("Patient Care", 4, 4, True),
            RoleSkillReq("Safety Protocols", 3, 4),
            RoleSkillReq("Communication", 3, 3),
        ], max_headcount=4),
        RoleTemplate("Research Scientist", 6, [
            RoleSkillReq("Research Methods", 4, 5, True),
            RoleSkillReq("Data Analysis", 3, 4),
            RoleSkillReq("Clinical Knowledge", 3, 3),
        ], max_headcount=3),
        RoleTemplate("Department Head", 8, [
            RoleSkillReq("Team Leadership", 4, 5, True),
            RoleSkillReq("Clinical Knowledge", 4, 4),
            RoleSkillReq("Quality Improvement", 3, 4),
            RoleSkillReq("Communication", 4, 3),
        ], max_headcount=2),
        RoleTemplate("Compliance Officer", 7, [
            RoleSkillReq("Regulatory Compliance", 5, 5, True),
            RoleSkillReq("Safety Protocols", 4, 5, True),
            RoleSkillReq("Quality Improvement", 3, 3),
        ], max_headcount=1),
    ]
    departments = [
        DepartmentTemplate("Clinical", ["Clinical Assistant", "Clinician"], ["patient-centered", "evidence-based"]),
        DepartmentTemplate("Research", ["Research Scientist"], ["innovation", "academic"]),
        DepartmentTemplate("Administration", ["Department Head", "Compliance Officer"], ["governance", "safety"]),
    ]
    return IndustryTemplate(
        industry=IndustryType.HEALTHCARE,
        name_en="Healthcare",
        name_ko="의료",
        description_en="Healthcare organization focused on patient care, research, and safety.",
        description_ko="환자 치료, 연구, 안전에 중점을 둔 의료 기관.",
        default_culture=CultureType.CLAN,
        skills=skills,
        roles=roles,
        departments=departments,
        config_overrides=ConfigOverrides(
            attrition_base_rate=0.015,  # lower turnover
            growth_gap_1_prob=0.12,  # slower growth (longer training)
            event_reorg_probability=0.01,  # rare reorgs
        ),
        first_names=FIRST_NAMES,
        last_names=LAST_NAMES,
    )


# ── Template Registry ──

_TEMPLATE_REGISTRY: dict[IndustryType, IndustryTemplate] = {}


def get_template(industry: IndustryType) -> IndustryTemplate:
    """Get the template for a specific industry."""
    if not _TEMPLATE_REGISTRY:
        _register_all()
    return _TEMPLATE_REGISTRY[industry]


def get_all_templates() -> list[IndustryTemplate]:
    """Get all available industry templates."""
    if not _TEMPLATE_REGISTRY:
        _register_all()
    return list(_TEMPLATE_REGISTRY.values())


def _register_all() -> None:
    """Register all industry templates."""
    for factory_fn in [
        _tech_startup_template,
        _enterprise_it_template,
        _consulting_template,
        _manufacturing_template,
        _finance_template,
        _healthcare_template,
    ]:
        tmpl = factory_fn()
        _TEMPLATE_REGISTRY[tmpl.industry] = tmpl
