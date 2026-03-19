"""Bayesian skill estimation engine.

Uses Normal-Normal conjugate model for closed-form updates.
Each project outcome provides a noisy observation of true skill level,
and the posterior is updated via precision-weighted averaging.

Algorithm combines ideas from:
- Glicko-2 rating system (uncertainty decay over time)
- Item Response Theory (difficulty × ability interaction)
- TrueSkill (role-based noise adjustment)

References:
- Glickman, M.E. (2001) "Dynamic paired comparison models with stochastic variances"
- Schmidt & Hunter (1998) "The validity and utility of selection methods"
- Dreyfus, S.E. (2004) "The Five-Stage Model of Adult Skill Acquisition"
"""

from __future__ import annotations

import math
from datetime import datetime

from .enums import ProjectDifficulty, ProjectResult, ProjectRole, SkillTrend
from .models import EstimateSnapshot, SkillEstimate
from .prior import SIGMA_INITIAL


# ── Observation signal mapping ────────────────────────────────────────

def outcome_to_signal(result: ProjectResult, difficulty: ProjectDifficulty) -> float:
    """Convert (result, difficulty) → observed skill level estimate.

    Higher difficulty + better result = higher inferred skill.
    Based on IRT: a person who succeeds at a hard task likely has high ability.
    """
    d = float(difficulty.value)

    match result:
        case ProjectResult.FAILURE:
            # Failed → skill is probably below project difficulty
            signal = d * 0.4
        case ProjectResult.PARTIAL:
            # Partial success → skill roughly matches difficulty
            signal = d * 0.7
        case ProjectResult.SUCCESS:
            # Succeeded → skill meets or exceeds difficulty
            signal = d * 1.0
        case ProjectResult.EXCELLENT:
            # Exceptional → skill clearly exceeds difficulty
            signal = d * 1.2

    return max(1.0, min(5.0, signal))


def observation_noise(
    difficulty: ProjectDifficulty,
    role: ProjectRole,
) -> float:
    """Compute observation noise (sigma) for a project outcome.

    Lower noise = stronger signal:
    - Harder projects give clearer signals (less noise)
    - Lead roles give clearer signals than reviewers
    """
    base_noise = 0.8

    # Harder projects → less noisy (more discriminating)
    difficulty_adj = 0.1 * (5 - difficulty.value)

    # Lead roles → clearest signal; reviewers → noisiest
    role_adj = {
        ProjectRole.LEAD: 0.0,
        ProjectRole.CONTRIBUTOR: 0.2,
        ProjectRole.REVIEWER: 0.4,
    }[role]

    return base_noise + difficulty_adj + role_adj


# ── Bayesian update (Normal-Normal conjugate) ─────────────────────────

def bayesian_update(
    prior_mu: float,
    prior_sigma: float,
    obs_mu: float,
    obs_sigma: float,
) -> tuple[float, float]:
    """Normal-Normal conjugate Bayesian update.

    Given:
        prior ~ N(prior_mu, prior_sigma²)
        observation ~ N(obs_mu, obs_sigma²)

    Returns:
        posterior (mu, sigma)

    This is the core mathematical operation:
        precision_prior = 1 / σ²_prior
        precision_obs = 1 / σ²_obs
        precision_post = precision_prior + precision_obs
        mu_post = (precision_prior * mu_prior + precision_obs * mu_obs) / precision_post
        sigma_post = √(1 / precision_post)
    """
    prec_prior = 1.0 / (prior_sigma**2)
    prec_obs = 1.0 / (obs_sigma**2)
    prec_post = prec_prior + prec_obs

    mu_post = (prec_prior * prior_mu + prec_obs * obs_mu) / prec_post
    sigma_post = math.sqrt(1.0 / prec_post)

    # Clamp mu to valid range
    mu_post = max(1.0, min(5.0, mu_post))

    return mu_post, sigma_post


# ── Trend detection ───────────────────────────────────────────────────

def compute_trend(history: list[EstimateSnapshot], window: int = 5) -> SkillTrend:
    """Detect skill trend from recent history using linear regression slope.

    Uses last `window` snapshots. Slope > +0.1 = rising, < -0.1 = declining.
    """
    recent = history[-window:]
    n = len(recent)
    if n < 2:
        return SkillTrend.STABLE

    # Simple linear regression on mu values (x = index, y = mu)
    x_mean = (n - 1) / 2.0
    y_mean = sum(s.mu for s in recent) / n

    numerator = sum((i - x_mean) * (s.mu - y_mean) for i, s in enumerate(recent))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return SkillTrend.STABLE

    slope = numerator / denominator

    if slope > 0.1:
        return SkillTrend.RISING
    elif slope < -0.1:
        return SkillTrend.DECLINING
    return SkillTrend.STABLE


# ── High-level estimation operations ──────────────────────────────────

def compute_confidence(sigma: float) -> float:
    """Confidence = 1 - (current_sigma / initial_sigma), clamped to [0, 1]."""
    return max(0.0, min(1.0, 1.0 - sigma / SIGMA_INITIAL))


def update_estimate(
    estimate: SkillEstimate,
    result: ProjectResult,
    difficulty: ProjectDifficulty,
    role: ProjectRole,
) -> SkillEstimate:
    """Update a skill estimate with a new project outcome.

    This is the main entry point for Bayesian updating.
    """
    obs_mu = outcome_to_signal(result, difficulty)
    obs_sigma = observation_noise(difficulty, role)

    new_mu, new_sigma = bayesian_update(
        estimate.mu, estimate.sigma,
        obs_mu, obs_sigma,
    )

    # Record history snapshot
    snapshot = EstimateSnapshot(mu=new_mu, sigma=new_sigma, timestamp=datetime.now())
    new_history = [*estimate.history, snapshot]

    # Compute trend from updated history
    trend = compute_trend(new_history)

    return SkillEstimate(
        person_id=estimate.person_id,
        skill_id=estimate.skill_id,
        mu=new_mu,
        sigma=new_sigma,
        confidence=compute_confidence(new_sigma),
        trend=trend,
        update_count=estimate.update_count + 1,
        last_updated=datetime.now(),
        history=new_history,
    )
