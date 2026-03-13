"""Cross-person ranking verification: validate scoring produces intuitive results."""

from uuid import uuid4

import pytest

from talentgraph.data.seed import _id, create_sample_company
from talentgraph.ontology.enums import SkillLevel
from talentgraph.ontology.models import Person, PersonSkill
from talentgraph.scoring.engine import FitScoreEngine


class TestCrossPersonRankings:
    def test_alice_beats_carol_for_sr_data_eng(self, sample_company):
        engine = FitScoreEngine(sample_company)
        alice = engine.evaluate_person(_id("person:alice"))
        carol = engine.evaluate_person(_id("person:carol"))

        alice_sde = next(r for r in alice if r.role_title == "Senior Data Engineer")
        carol_sde = next(r for r in carol if r.role_title == "Senior Data Engineer")

        assert alice_sde.fit_score > carol_sde.fit_score
        assert alice_sde.fit_score > carol_sde.fit_score + 0.05

    def test_bob_dominates_eng_manager(self, sample_company):
        engine = FitScoreEngine(sample_company)
        scores = {}
        for person in sample_company.people:
            results = engine.evaluate_person(person.id)
            em = next(r for r in results if r.role_title == "Engineering Manager")
            scores[person.name] = em.fit_score

        assert scores["Bob Park"] == max(scores.values())

    def test_dave_best_skill_match_for_financial_analyst(self, sample_company):
        engine = FitScoreEngine(sample_company)
        sm_scores = {}
        for person in sample_company.people:
            results = engine.evaluate_person(person.id)
            fa = next(r for r in results if r.role_title == "Financial Analyst")
            sm_scores[person.name] = fa.skill_match_score

        assert sm_scores["Dave Lee"] == max(sm_scores.values())

    def test_dave_burnout_drags_overall_fit(self, sample_company):
        engine = FitScoreEngine(sample_company)
        results = engine.evaluate_person(_id("person:dave"))
        fa = next(r for r in results if r.role_title == "Financial Analyst")

        assert fa.breakdown["burnout_penalty"] < -0.03

    def test_eve_never_tops_any_role(self, sample_company):
        engine = FitScoreEngine(sample_company)
        eve_results = engine.evaluate_person(_id("person:eve"))

        for eve_r in eve_results:
            someone_beats_eve = False
            for person in sample_company.people:
                if person.name == "Eve Wang":
                    continue
                results = engine.evaluate_person(person.id)
                match = next(
                    (r for r in results
                     if r.role_id == eve_r.role_id and r.department_id == eve_r.department_id),
                    None,
                )
                if match and match.fit_score > eve_r.fit_score:
                    someone_beats_eve = True
                    break
            assert someone_beats_eve, f"Eve should not be #1 for {eve_r.role_title}"


class TestEdgeCases:
    def test_zero_skill_person(self, sample_company):
        company = sample_company.model_copy(deep=True)
        empty = Person(name="Ghost")
        company.people.append(empty)
        engine = FitScoreEngine(company)
        results = engine.evaluate_person(empty.id)

        for r in results:
            assert r.skill_match_score == 0.0

    def test_overqualified_person(self, sample_company):
        company = sample_company.model_copy(deep=True)
        god = Person(
            name="God Mode",
            skills=[
                PersonSkill(skill_id=s.id, level=SkillLevel.EXPERT, years_experience=20.0)
                for s in company.skills
            ],
        )
        company.people.append(god)
        engine = FitScoreEngine(company)
        results = engine.evaluate_person(god.id)

        for r in results:
            assert r.skill_match_score == 1.0

    def test_identical_people_get_identical_scores(self, sample_company):
        company = sample_company.model_copy(deep=True)
        alice = next(p for p in company.people if p.name == "Alice Chen")
        clone = alice.model_copy(deep=True)
        clone.id = uuid4()
        clone.name = "Alice Clone"
        for a in clone.assignments:
            a.person_id = clone.id
        company.people.append(clone)

        engine = FitScoreEngine(company)
        alice_results = engine.evaluate_person(alice.id)
        clone_results = engine.evaluate_person(clone.id)

        for ar, cr in zip(alice_results, clone_results):
            assert abs(ar.fit_score - cr.fit_score) < 0.001
