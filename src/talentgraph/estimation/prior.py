"""Dreyfus-model skill prior initialization.

Maps job title + years of experience → initial skill estimate (mu, sigma).
Based on the Dreyfus model of skill acquisition (Novice → Expert).
"""

from __future__ import annotations

import math
import re

# ── Title → base skill level mapping ──────────────────────────────────
# Normalized title keywords → expected skill level (1.0-5.0)
_TITLE_KEYWORDS: list[tuple[list[str], float]] = [
    (["intern", "인턴"], 1.2),
    (["junior", "jr", "주니어", "사원"], 2.0),
    (["associate", "대리"], 2.5),
    (["mid", "과장"], 3.0),
    (["senior", "sr", "시니어", "차장"], 4.0),
    (["lead", "principal", "리드", "수석", "부장"], 4.5),
    (["director", "이사", "head", "헤드"], 4.7),
    (["vp", "cto", "ceo", "cfo", "coo", "임원", "상무", "전무"], 4.8),
]

# Default if no title keyword matches
_DEFAULT_BASE = 3.0

# Initial uncertainty (high — we don't know much yet)
SIGMA_INITIAL = 1.5


def _normalize(title: str) -> str:
    """Lowercase, strip whitespace and punctuation."""
    return re.sub(r"[^a-z0-9가-힣\s]", "", title.lower()).strip()


def title_to_base_level(title: str) -> float:
    """Map a job title string to a base skill level estimate."""
    normed = _normalize(title)
    for keywords, level in _TITLE_KEYWORDS:
        for kw in keywords:
            if kw in normed:
                return level
    return _DEFAULT_BASE


def dreyfus_prior(title: str, years_experience: float) -> tuple[float, float]:
    """Compute (mu, sigma) prior for a person given title + experience.

    Returns:
        (mu, sigma) where mu is in [1.0, 5.0] and sigma starts at SIGMA_INITIAL
        but decreases slightly with more experience (we're more certain about
        veterans).

    The Dreyfus model predicts asymptotic growth:
    - Early years: rapid improvement
    - Later years: diminishing returns approaching ceiling
    """
    base = title_to_base_level(title)

    # Asymptotic experience adjustment (logarithmic growth)
    # max +1.0 level from experience alone, with diminishing returns
    if years_experience > 0:
        exp_adj = min(1.0, 0.5 * math.log1p(years_experience / 3.0))
    else:
        exp_adj = 0.0

    mu = max(1.0, min(5.0, base + exp_adj))

    # Slightly reduce uncertainty for very experienced people
    # (we're a bit more confident in our prior for a 15-year veteran)
    sigma = SIGMA_INITIAL * max(0.7, 1.0 - years_experience * 0.02)

    return mu, sigma
