from datetime import date

from talentgraph.scoring.burnout import compute_burnout_risk


def test_dave_high_burnout(dave):
    """Dave has long tenure + declining perf → high burnout risk."""
    risk = compute_burnout_risk(dave, reference_date=date(2026, 1, 1))
    assert risk >= 0.4


def test_carol_low_burnout(carol):
    """Carol is new with rising perf → low burnout risk."""
    risk = compute_burnout_risk(carol, reference_date=date(2026, 1, 1))
    assert risk < 0.3


def test_no_assignments():
    """Person with no assignments → low base risk."""
    from talentgraph.ontology.models import Person

    p = Person(name="Newbie")
    risk = compute_burnout_risk(p)
    assert risk == 0.1


def test_risk_bounded(alice):
    """Risk should always be in [0, 1]."""
    risk = compute_burnout_risk(alice)
    assert 0.0 <= risk <= 1.0
