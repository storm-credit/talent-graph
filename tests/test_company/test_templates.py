"""Tests for industry templates."""

from __future__ import annotations

import pytest

from talentgraph.company.profile import IndustryType
from talentgraph.company.templates import get_all_templates, get_template


class TestTemplateRegistry:
    """Test template registry completeness and validity."""

    def test_all_industries_have_templates(self):
        for ind in IndustryType:
            tmpl = get_template(ind)
            assert tmpl is not None
            assert tmpl.industry == ind

    def test_get_all_templates_returns_all(self):
        templates = get_all_templates()
        assert len(templates) == len(IndustryType)

    def test_each_template_has_skills(self):
        for tmpl in get_all_templates():
            assert len(tmpl.skills) >= 5, f"{tmpl.industry}: needs at least 5 skills"

    def test_each_template_has_roles(self):
        for tmpl in get_all_templates():
            assert len(tmpl.roles) >= 3, f"{tmpl.industry}: needs at least 3 roles"

    def test_each_template_has_departments(self):
        for tmpl in get_all_templates():
            assert len(tmpl.departments) >= 2, f"{tmpl.industry}: needs at least 2 departments"

    def test_role_skills_reference_valid_skills(self):
        """Every role's required skill must exist in the template's skill list."""
        for tmpl in get_all_templates():
            skill_names = {s.name for s in tmpl.skills}
            for role in tmpl.roles:
                for req in role.required_skills:
                    assert req.skill_name in skill_names, (
                        f"{tmpl.industry}/{role.title}: skill '{req.skill_name}' not in template skills"
                    )

    def test_department_roles_reference_valid_roles(self):
        """Every department's role must exist in the template's role list."""
        for tmpl in get_all_templates():
            role_titles = {r.title for r in tmpl.roles}
            for dept in tmpl.departments:
                for rt in dept.role_titles:
                    assert rt in role_titles, (
                        f"{tmpl.industry}/{dept.name}: role '{rt}' not in template roles"
                    )

    def test_templates_have_bilingual_names(self):
        for tmpl in get_all_templates():
            assert tmpl.name_en, f"{tmpl.industry}: missing English name"
            assert tmpl.name_ko, f"{tmpl.industry}: missing Korean name"
            assert tmpl.description_en, f"{tmpl.industry}: missing English description"
            assert tmpl.description_ko, f"{tmpl.industry}: missing Korean description"

    def test_templates_have_name_pools(self):
        for tmpl in get_all_templates():
            assert len(tmpl.first_names) >= 10
            assert len(tmpl.last_names) >= 10

    def test_role_levels_in_range(self):
        for tmpl in get_all_templates():
            for role in tmpl.roles:
                assert 1 <= role.level <= 10, f"{tmpl.industry}/{role.title}: level {role.level} out of range"

    def test_skill_min_levels_in_range(self):
        for tmpl in get_all_templates():
            for role in tmpl.roles:
                for req in role.required_skills:
                    assert 1 <= req.min_level <= 5, (
                        f"{tmpl.industry}/{role.title}/{req.skill_name}: min_level {req.min_level} out of range"
                    )
