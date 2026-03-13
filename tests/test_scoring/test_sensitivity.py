"""Weight sensitivity analysis: verify weight changes produce expected effects."""

from talentgraph.data.seed import _id
from talentgraph.scoring.engine import FitScoreEngine
from talentgraph.scoring.weights import ScoringWeights


class TestWeightSensitivity:
    def test_max_burnout_weight_penalizes_dave(self, sample_company):
        default_engine = FitScoreEngine(sample_company)
        heavy_burnout = FitScoreEngine(
            sample_company,
            ScoringWeights(
                skill_match=0.30, historical_performance=0.20,
                level_match=0.10, burnout_risk=0.40,
            ),
        )

        dave_id = _id("person:dave")
        default_fa = next(
            r for r in default_engine.evaluate_person(dave_id)
            if r.role_title == "Financial Analyst"
        )
        heavy_fa = next(
            r for r in heavy_burnout.evaluate_person(dave_id)
            if r.role_title == "Financial Analyst"
        )

        assert heavy_fa.fit_score < default_fa.fit_score - 0.05

    def test_zero_burnout_weight_ignores_burnout(self, sample_company):
        no_burnout = FitScoreEngine(
            sample_company,
            ScoringWeights(
                skill_match=0.50, historical_performance=0.35,
                level_match=0.15, burnout_risk=0.0,
            ),
        )
        dave_id = _id("person:dave")
        results = no_burnout.evaluate_person(dave_id)
        fa = next(r for r in results if r.role_title == "Financial Analyst")

        assert fa.breakdown["burnout_penalty"] == 0.0

    def test_skill_only_weights(self, sample_company):
        skill_only = FitScoreEngine(
            sample_company,
            ScoringWeights(
                skill_match=1.0, historical_performance=0.0,
                level_match=0.0, burnout_risk=0.0,
            ),
        )
        alice_id = _id("person:alice")
        results = skill_only.evaluate_person(alice_id)
        sde = next(r for r in results if r.role_title == "Senior Data Engineer")

        assert abs(sde.fit_score - sde.skill_match_score) < 0.01

    def test_weights_reorder_rankings(self, sample_company):
        default_engine = FitScoreEngine(sample_company)
        history_heavy = FitScoreEngine(
            sample_company,
            ScoringWeights(
                skill_match=0.10, historical_performance=0.70,
                level_match=0.10, burnout_risk=0.10,
            ),
        )

        def get_ranking(engine, role_title):
            ranking = []
            for person in sample_company.people:
                results = engine.evaluate_person(person.id)
                r = next(x for x in results if x.role_title == role_title)
                ranking.append((person.name, r.fit_score))
            return sorted(ranking, key=lambda x: x[1], reverse=True)

        default_rank = get_ranking(default_engine, "Senior Data Engineer")
        history_rank = get_ranking(history_heavy, "Senior Data Engineer")

        default_names = [x[0] for x in default_rank]
        history_names = [x[0] for x in history_rank]
        assert default_names != history_names, "Weight changes should affect ranking order"
