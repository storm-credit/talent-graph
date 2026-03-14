"""Tests for explainer formula registry and glossary."""

import pytest

from talentgraph.explainer.definitions import (
    ConstantDefinition,
    FormulaDefinition,
    GlossaryEntry,
    VariableDefinition,
)
from talentgraph.explainer.registry import get_all_formulas, get_glossary


class TestFormulaRegistry:
    """Tests for the formula registry."""

    def test_returns_all_formulas(self):
        formulas = get_all_formulas()
        assert len(formulas) >= 12

    def test_all_formulas_are_formula_definitions(self):
        formulas = get_all_formulas()
        for f in formulas:
            assert isinstance(f, FormulaDefinition)

    def test_formula_ids_unique(self):
        formulas = get_all_formulas()
        ids = [f.id for f in formulas]
        assert len(ids) == len(set(ids)), "Formula IDs must be unique"

    def test_formula_has_required_fields(self):
        formulas = get_all_formulas()
        for f in formulas:
            assert f.id, f"Formula missing id"
            assert f.name_ko, f"Formula {f.id} missing name_ko"
            assert f.name_en, f"Formula {f.id} missing name_en"
            assert f.formula_plain, f"Formula {f.id} missing formula_plain"
            assert f.description_ko, f"Formula {f.id} missing description_ko"
            assert f.description_en, f"Formula {f.id} missing description_en"
            assert f.theoretical_basis, f"Formula {f.id} missing theoretical_basis"
            assert f.theoretical_basis_ko, f"Formula {f.id} missing theoretical_basis_ko"
            assert f.category, f"Formula {f.id} missing category"

    def test_formula_categories_valid(self):
        valid_categories = {"scoring", "simulation", "growth", "morale", "attrition", "events"}
        formulas = get_all_formulas()
        for f in formulas:
            assert f.category in valid_categories, (
                f"Formula {f.id} has invalid category: {f.category}"
            )

    def test_formula_variables_are_valid(self):
        formulas = get_all_formulas()
        for f in formulas:
            for v in f.variables:
                assert isinstance(v, VariableDefinition)
                assert v.symbol
                assert v.name_ko
                assert v.name_en

    def test_formula_constants_are_valid(self):
        formulas = get_all_formulas()
        for f in formulas:
            for c in f.constants:
                assert isinstance(c, ConstantDefinition)
                assert c.symbol
                assert c.name_en
                assert c.value

    def test_core_formulas_present(self):
        """Verify the essential scoring formulas are defined."""
        formulas = get_all_formulas()
        ids = {f.id for f in formulas}
        expected = {
            "fit_score",
            "predicted_performance",
            "skill_match",
            "historical_performance",
            "level_match",
            "burnout_risk",
        }
        assert expected.issubset(ids), f"Missing core formulas: {expected - ids}"

    def test_simulation_formulas_present(self):
        """Verify the simulation-related formulas are defined."""
        formulas = get_all_formulas()
        ids = {f.id for f in formulas}
        expected = {
            "skill_growth",
            "skill_decay",
            "morale_system",
            "attrition",
        }
        assert expected.issubset(ids), f"Missing simulation formulas: {expected - ids}"

    def test_related_formulas_reference_valid_ids(self):
        formulas = get_all_formulas()
        all_ids = {f.id for f in formulas}
        for f in formulas:
            for ref in f.related_formulas:
                assert ref in all_ids, (
                    f"Formula {f.id} references unknown formula: {ref}"
                )

    def test_fit_score_formula_details(self):
        """Verify the main FitScore formula has correct weights and references."""
        formulas = get_all_formulas()
        fit = next(f for f in formulas if f.id == "fit_score")

        assert fit.category == "scoring"
        assert len(fit.variables) >= 4  # sm, hp, lm, br
        assert len(fit.constants) >= 4  # w1, w2, w3, w4
        assert "Schmidt" in fit.theoretical_basis or "Hunter" in fit.theoretical_basis


class TestGlossary:
    """Tests for the glossary registry."""

    def test_returns_all_entries(self):
        glossary = get_glossary()
        assert len(glossary) >= 20

    def test_all_entries_are_glossary_entries(self):
        glossary = get_glossary()
        for g in glossary:
            assert isinstance(g, GlossaryEntry)

    def test_glossary_ids_unique(self):
        glossary = get_glossary()
        ids = [g.id for g in glossary]
        assert len(ids) == len(set(ids)), "Glossary IDs must be unique"

    def test_glossary_has_required_fields(self):
        glossary = get_glossary()
        for g in glossary:
            assert g.id, f"Glossary entry missing id"
            assert g.term_ko, f"Glossary {g.id} missing term_ko"
            assert g.term_en, f"Glossary {g.id} missing term_en"
            assert g.definition_ko, f"Glossary {g.id} missing definition_ko"
            assert g.definition_en, f"Glossary {g.id} missing definition_en"
            assert g.category, f"Glossary {g.id} missing category"

    def test_glossary_categories_valid(self):
        valid_categories = {"core", "scoring", "simulation", "skill", "metric"}
        glossary = get_glossary()
        for g in glossary:
            assert g.category in valid_categories, (
                f"Glossary {g.id} has invalid category: {g.category}"
            )

    def test_core_terms_present(self):
        glossary = get_glossary()
        ids = {g.id for g in glossary}
        expected = {
            "fit_score",
            "predicted_performance",
            "morale",
            "burnout_risk",
            "skill_match",
        }
        assert expected.issubset(ids), f"Missing core terms: {expected - ids}"

    def test_bilingual_content(self):
        """All entries should have both Korean and English content."""
        glossary = get_glossary()
        for g in glossary:
            assert g.term_ko != g.term_en, (
                f"Glossary {g.id}: KO and EN terms should differ"
            )
            assert g.definition_ko != g.definition_en, (
                f"Glossary {g.id}: KO and EN definitions should differ"
            )
