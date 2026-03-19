"""Tests for Dreyfus prior initialization."""

from talentgraph.estimation.prior import dreyfus_prior, title_to_base_level, SIGMA_INITIAL


class TestTitleToBaseLevel:
    def test_junior(self):
        assert title_to_base_level("Junior Developer") == 2.0

    def test_senior(self):
        assert title_to_base_level("Senior Engineer") == 4.0

    def test_korean_titles(self):
        assert title_to_base_level("주니어 개발자") == 2.0
        assert title_to_base_level("시니어 엔지니어") == 4.0
        assert title_to_base_level("인턴") == 1.2
        assert title_to_base_level("사원") == 2.0
        assert title_to_base_level("대리") == 2.5
        assert title_to_base_level("과장") == 3.0
        assert title_to_base_level("차장") == 4.0
        assert title_to_base_level("부장") == 4.5

    def test_unknown_defaults(self):
        assert title_to_base_level("Unknown Role XYZ") == 3.0

    def test_lead(self):
        assert title_to_base_level("Tech Lead") == 4.5

    def test_intern(self):
        assert title_to_base_level("Summer Intern") == 1.2


class TestDreyfusPrior:
    def test_junior_low_experience(self):
        mu, sigma = dreyfus_prior("Junior Developer", 1.0)
        assert 1.5 < mu < 3.0
        assert sigma > 1.0

    def test_senior_high_experience(self):
        mu, sigma = dreyfus_prior("Senior Engineer", 10.0)
        assert mu > 4.0
        assert sigma < SIGMA_INITIAL  # More certain for veterans

    def test_intern_zero_experience(self):
        mu, sigma = dreyfus_prior("인턴", 0.0)
        assert mu == 1.2  # No experience adjustment
        assert sigma == SIGMA_INITIAL

    def test_mu_clamped(self):
        mu, _ = dreyfus_prior("CTO", 30.0)
        assert mu <= 5.0

    def test_experience_diminishing_returns(self):
        mu2, _ = dreyfus_prior("과장", 2.0)
        mu10, _ = dreyfus_prior("과장", 10.0)
        mu30, _ = dreyfus_prior("과장", 30.0)
        # Growth slows down (logarithmic) over wider intervals
        assert (mu10 - mu2) > (mu30 - mu10)

    def test_sigma_decreases_with_experience(self):
        _, sigma0 = dreyfus_prior("과장", 0.0)
        _, sigma10 = dreyfus_prior("과장", 10.0)
        assert sigma10 < sigma0
