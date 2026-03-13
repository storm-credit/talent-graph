from talentgraph.scoring.skill_match import compute_skill_match


def test_alice_sr_data_eng_high_match(alice, sr_data_eng_role, skill_lookup):
    """Alice should score high for Sr Data Engineer (strong Python, SQL, Data Analysis)."""
    score = compute_skill_match(alice, sr_data_eng_role, skill_lookup)
    assert score >= 0.9


def test_alice_eng_manager_low_match(alice, eng_manager_role, skill_lookup):
    """Alice should score low for Eng Manager (weak leadership)."""
    score = compute_skill_match(alice, eng_manager_role, skill_lookup)
    assert score < 0.5


def test_bob_eng_manager_high_match(bob, eng_manager_role, skill_lookup):
    """Bob should score high for Eng Manager (strong leadership, PM, communication)."""
    score = compute_skill_match(bob, eng_manager_role, skill_lookup)
    assert score >= 0.9


def test_dave_financial_analyst_high_match(dave, financial_analyst_role, skill_lookup):
    """Dave should score high for Financial Analyst."""
    score = compute_skill_match(dave, financial_analyst_role, skill_lookup)
    assert score >= 0.8


def test_score_bounded(alice, sr_data_eng_role, skill_lookup):
    """Score should always be in [0, 1]."""
    score = compute_skill_match(alice, sr_data_eng_role, skill_lookup)
    assert 0.0 <= score <= 1.0


def test_no_skills_person(sr_data_eng_role, skill_lookup):
    """Person with no skills should score 0."""
    from talentgraph.ontology.models import Person

    empty = Person(name="Empty")
    score = compute_skill_match(empty, sr_data_eng_role, skill_lookup)
    assert score == 0.0
