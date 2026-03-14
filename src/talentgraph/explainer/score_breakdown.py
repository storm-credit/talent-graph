"""Step-by-step score breakdown: traces how a FitScore is computed for a person+role pair."""

from __future__ import annotations

import math
from datetime import date
from uuid import UUID

from talentgraph.explainer.definitions import ScoreBreakdown, ScoreStep
from talentgraph.ontology.models import Company, Person, Role
from talentgraph.scoring.weights import ScoringWeights


def compute_score_breakdown(
    company: Company,
    person_id: UUID,
    role_id: UUID,
    department_id: UUID,
    weights: ScoringWeights | None = None,
    reference_date: date | None = None,
) -> ScoreBreakdown:
    """Build a step-by-step breakdown of how FitScore is computed.

    Returns a ScoreBreakdown with each scoring component traced
    through its formula, inputs, intermediate values, and weighted contribution.
    """
    w = weights or ScoringWeights()
    ref = reference_date or date.today()

    person = _find_person(company, person_id)
    role = _find_role(company, role_id, department_id)
    dept = _find_department(company, department_id)

    skill_lookup = {s.id: s for s in company.skills}

    steps: list[ScoreStep] = []

    # ── Step 1: Skill Match ──
    sm_score, sm_step = _trace_skill_match(person, role, skill_lookup, w.skill_match)
    steps.append(sm_step)

    # ── Step 2: Historical Performance ──
    hp_score, hp_step = _trace_historical(person, role, ref, w.historical_performance)
    steps.append(hp_step)

    # ── Step 3: Level Match ──
    lm_score, lm_step = _trace_level_match(person, role, w.level_match)
    steps.append(lm_step)

    # ── Step 4: Burnout Risk ──
    br_score, br_step = _trace_burnout(person, ref, w.burnout_risk)
    steps.append(br_step)

    # ── Final Calculation ──
    raw = (
        w.skill_match * sm_score
        + w.historical_performance * hp_score
        + w.level_match * lm_score
        - w.burnout_risk * br_score
    )
    fit_score = round(max(0.0, min(1.0, raw)), 4)

    # Predicted performance
    base = 1.0 + fit_score * 4.0
    history_adj = (hp_score - 0.5) * 0.5
    predicted = round(max(1.0, min(5.0, base + history_adj)), 1)

    return ScoreBreakdown(
        person_id=str(person.id),
        person_name=person.name,
        role_id=str(role.id),
        role_title=role.title,
        department_id=str(dept.id),
        department_name=dept.name,
        steps=steps,
        final_fit_score=fit_score,
        final_predicted_performance=predicted,
        summary_ko=_build_summary_ko(person.name, role.title, fit_score, predicted, steps),
        summary_en=_build_summary_en(person.name, role.title, fit_score, predicted, steps),
    )


# ── Component Tracers ──


def _trace_skill_match(
    person: Person,
    role: Role,
    skill_lookup: dict,
    weight: float,
) -> tuple[float, ScoreStep]:
    """Trace skill match calculation step-by-step."""
    if not role.required_skills:
        return 1.0, ScoreStep(
            step_number=1,
            component="skill_match",
            component_ko="스킬 매칭",
            formula_applied="요구 스킬 없음 → 1.0",
            inputs={"required_skills": 0},
            intermediate_value=1.0,
            weight=weight,
            weighted_value=round(weight * 1.0, 4),
            explanation_ko="이 역할에 필수 스킬이 없어 완벽 매칭입니다.",
            explanation_en="No required skills for this role, perfect match by default.",
        )

    person_skills = {ps.skill_id: ps for ps in person.skills}
    details = []
    weighted_sum = 0.0
    max_weighted_sum = 0.0

    for req in role.required_skills:
        skill = skill_lookup.get(req.skill_id)
        skill_name = skill.name if skill else str(req.skill_id)
        max_weighted_sum += req.weight

        ps = person_skills.get(req.skill_id)
        if ps is None:
            details.append({
                "skill": skill_name,
                "person_level": "없음",
                "required_level": req.minimum_level.value,
                "match_ratio": 0.0,
                "weight": req.weight,
                "contribution": 0.0,
            })
            continue

        match_ratio = min(ps.level.numeric / req.minimum_level.numeric, 1.0)
        contribution = match_ratio * req.weight
        weighted_sum += contribution

        details.append({
            "skill": skill_name,
            "person_level": ps.level.value,
            "required_level": req.minimum_level.value,
            "match_ratio": round(match_ratio, 4),
            "weight": req.weight,
            "contribution": round(contribution, 4),
        })

    score = weighted_sum / max_weighted_sum if max_weighted_sum > 0 else 1.0
    score = round(score, 4)

    matched = sum(1 for d in details if d["match_ratio"] > 0)
    total = len(details)

    formula_str = f"sum(contributions) / sum(weights) = {round(weighted_sum, 4)} / {round(max_weighted_sum, 4)} = {score}"

    return score, ScoreStep(
        step_number=1,
        component="skill_match",
        component_ko="스킬 매칭",
        formula_applied=formula_str,
        inputs={"skill_details": details, "matched": matched, "total": total},
        intermediate_value=score,
        weight=weight,
        weighted_value=round(weight * score, 4),
        explanation_ko=f"{total}개 필수 스킬 중 {matched}개 보유. 가중 매칭 점수: {score}",
        explanation_en=f"Has {matched} of {total} required skills. Weighted match score: {score}",
    )


def _trace_historical(
    person: Person,
    role: Role,
    ref: date,
    weight: float,
) -> tuple[float, ScoreStep]:
    """Trace historical performance calculation."""
    half_life_days = 730.0

    all_outcomes: list[dict] = []
    for assignment in person.assignments:
        is_same_role = assignment.role_id == role.id
        for outcome in assignment.outcomes:
            days_ago = (ref - outcome.evaluated_at).days
            decay = math.exp(-0.693 * days_ago / half_life_days)
            role_boost = 1.5 if is_same_role else 1.0
            w = decay * role_boost
            normalized = (outcome.rating.numeric - 1) / 4.0

            all_outcomes.append({
                "rating": outcome.rating.value,
                "rating_numeric": outcome.rating.numeric,
                "evaluated_at": str(outcome.evaluated_at),
                "days_ago": days_ago,
                "decay": round(decay, 4),
                "role_boost": role_boost,
                "effective_weight": round(w, 4),
                "normalized_rating": round(normalized, 4),
                "weighted_contribution": round(normalized * w, 4),
            })

    if not all_outcomes:
        score = 0.5
        return score, ScoreStep(
            step_number=2,
            component="historical_performance",
            component_ko="이력 성과",
            formula_applied="이력 없음 → 중립값 0.5",
            inputs={"outcome_count": 0},
            intermediate_value=score,
            weight=weight,
            weighted_value=round(weight * score, 4),
            explanation_ko="과거 평가 이력이 없어 중립값(0.5)을 사용합니다.",
            explanation_en="No historical outcomes available, using neutral prior (0.5).",
        )

    weighted_sum = sum(o["weighted_contribution"] for o in all_outcomes)
    weight_total = sum(o["effective_weight"] for o in all_outcomes)
    score = round(weighted_sum / weight_total, 4) if weight_total > 0 else 0.5

    formula_str = (
        f"sum(normalized × decay × boost) / sum(weights) = "
        f"{round(weighted_sum, 4)} / {round(weight_total, 4)} = {score}"
    )

    return score, ScoreStep(
        step_number=2,
        component="historical_performance",
        component_ko="이력 성과",
        formula_applied=formula_str,
        inputs={
            "outcome_count": len(all_outcomes),
            "half_life_days": half_life_days,
            "outcomes": all_outcomes,
        },
        intermediate_value=score,
        weight=weight,
        weighted_value=round(weight * score, 4),
        explanation_ko=f"{len(all_outcomes)}개 평가 이력, 반감기 2년 적용. 가중 평균: {score}",
        explanation_en=f"{len(all_outcomes)} outcomes with 2-year half-life decay. Weighted average: {score}",
    )


def _trace_level_match(
    person: Person,
    role: Role,
    weight: float,
) -> tuple[float, ScoreStep]:
    """Trace level match calculation."""
    if not person.assignments:
        score = 0.5
        return score, ScoreStep(
            step_number=3,
            component="level_match",
            component_ko="레벨 매칭",
            formula_applied="배정 이력 없음 → 중립값 0.5",
            inputs={"person_level": None, "role_level": role.level},
            intermediate_value=score,
            weight=weight,
            weighted_value=round(weight * score, 4),
            explanation_ko="이전 배정 이력이 없어 중립값(0.5)을 사용합니다.",
            explanation_en="No assignment history, using neutral value (0.5).",
        )

    latest = max(person.assignments, key=lambda a: a.start_date)
    person_level = getattr(latest, "_role_level", None)

    if person_level is None:
        score = 0.5
        return score, ScoreStep(
            step_number=3,
            component="level_match",
            component_ko="레벨 매칭",
            formula_applied="레벨 정보 없음 → 중립값 0.5",
            inputs={"person_level": None, "role_level": role.level},
            intermediate_value=score,
            weight=weight,
            weighted_value=round(weight * score, 4),
            explanation_ko="역할 레벨 정보를 추론할 수 없어 중립값(0.5)을 사용합니다.",
            explanation_en="Cannot infer person level, using neutral value (0.5).",
        )

    gap = abs(role.level - person_level)

    if gap <= 1:
        score = 1.0
        formula_str = f"|{role.level} - {person_level}| = {gap} (≤ 1) → 1.0"
    else:
        penalty = (gap - 1) * 0.2
        score = round(max(0.0, 1.0 - penalty), 4)
        formula_str = f"|{role.level} - {person_level}| = {gap}, penalty = ({gap}-1) × 0.2 = {penalty} → {score}"

    gap_direction = "over" if person_level > role.level else "under" if person_level < role.level else "exact"

    return score, ScoreStep(
        step_number=3,
        component="level_match",
        component_ko="레벨 매칭",
        formula_applied=formula_str,
        inputs={
            "person_level": person_level,
            "role_level": role.level,
            "gap": gap,
            "gap_direction": gap_direction,
        },
        intermediate_value=score,
        weight=weight,
        weighted_value=round(weight * score, 4),
        explanation_ko=_level_explanation_ko(person_level, role.level, gap, gap_direction, score),
        explanation_en=_level_explanation_en(person_level, role.level, gap, gap_direction, score),
    )


def _trace_burnout(
    person: Person,
    ref: date,
    weight: float,
) -> tuple[float, ScoreStep]:
    """Trace burnout risk calculation."""
    if not person.assignments:
        score = 0.1
        return score, ScoreStep(
            step_number=4,
            component="burnout_risk",
            component_ko="번아웃 리스크",
            formula_applied="배정 이력 없음 → 기본 리스크 0.1",
            inputs={"has_assignments": False},
            intermediate_value=score,
            weight=weight,
            weighted_value=round(-weight * score, 4),
            explanation_ko="배정 이력이 없어 기본 낮은 리스크(0.1)를 적용합니다.",
            explanation_en="No assignments, applying base low risk (0.1).",
        )

    # Staleness
    latest = max(person.assignments, key=lambda a: a.start_date)
    years_in_role = round((ref - latest.start_date).days / 365.25, 2)

    if years_in_role <= 2.0:
        staleness = 0.0
    elif years_in_role <= 3.0:
        staleness = 0.2
    elif years_in_role <= 5.0:
        staleness = 0.5
    else:
        staleness = 0.8

    # Decline
    all_outcomes = []
    for assignment in person.assignments:
        for outcome in assignment.outcomes:
            all_outcomes.append(outcome)

    if len(all_outcomes) < 2:
        decline = 0.0
        decline_detail = "평가 이력 2개 미만"
    else:
        sorted_outcomes = sorted(all_outcomes, key=lambda o: o.evaluated_at)
        mid = len(sorted_outcomes) // 2
        first_half_avg = round(sum(o.rating.numeric for o in sorted_outcomes[:mid]) / mid, 4)
        second_half_avg = round(
            sum(o.rating.numeric for o in sorted_outcomes[mid:]) / (len(sorted_outcomes) - mid),
            4,
        )
        raw_decline = first_half_avg - second_half_avg
        decline = round(min(1.0, max(0.0, raw_decline / 2.0)), 4)
        decline_detail = f"전반 평균 {first_half_avg} → 후반 평균 {second_half_avg}, 감소폭 {round(raw_decline, 4)}"

    score = round(min(1.0, max(0.0, 0.6 * staleness + 0.4 * decline)), 4)
    formula_str = f"0.6 × {staleness} + 0.4 × {decline} = {score}"

    return score, ScoreStep(
        step_number=4,
        component="burnout_risk",
        component_ko="번아웃 리스크",
        formula_applied=formula_str,
        inputs={
            "years_in_role": years_in_role,
            "staleness_risk": staleness,
            "decline_risk": decline,
            "decline_detail": decline_detail,
            "outcome_count": len(all_outcomes),
        },
        intermediate_value=score,
        weight=weight,
        weighted_value=round(-weight * score, 4),
        explanation_ko=f"재직 {years_in_role}년 (정체 {staleness}), 성과 하락 리스크 {decline}. 번아웃 위험: {score}",
        explanation_en=f"{years_in_role}yr tenure (staleness {staleness}), decline risk {decline}. Burnout: {score}",
    )


# ── Helpers ──


def _find_person(company: Company, person_id: UUID) -> Person:
    for p in company.people:
        if p.id == person_id:
            return p
    raise ValueError(f"Person not found: {person_id}")


def _find_role(company: Company, role_id: UUID, department_id: UUID) -> Role:
    # Verify the role belongs to this department
    dept = _find_department(company, department_id)
    if role_id not in dept.roles:
        raise ValueError(f"Role {role_id} not in department {department_id}")

    for role in company.roles:
        if role.id == role_id:
            return role
    raise ValueError(f"Role not found: {role_id}")


def _find_department(company: Company, department_id: UUID):
    for dept in company.departments:
        if dept.id == department_id:
            return dept
    raise ValueError(f"Department not found: {department_id}")


def _level_explanation_ko(p_level: int, r_level: int, gap: int, direction: str, score: float) -> str:
    if direction == "exact":
        return f"현재 레벨({p_level})과 역할 레벨({r_level})이 동일하여 완벽 매칭입니다."
    elif direction == "under" and gap <= 1:
        return f"현재 레벨({p_level})에서 한 단계 승진({r_level})으로, 적절한 도전입니다."
    elif direction == "under":
        return f"현재 레벨({p_level})이 역할 레벨({r_level})보다 {gap}단계 낮아 페널티({round(1-score, 2)})가 적용됩니다."
    elif gap <= 1:
        return f"현재 레벨({p_level})이 역할 레벨({r_level})보다 1단계 높지만 허용 범위입니다."
    else:
        return f"현재 레벨({p_level})이 역할 레벨({r_level})보다 {gap}단계 높아 과잉 자격 페널티가 적용됩니다."


def _level_explanation_en(p_level: int, r_level: int, gap: int, direction: str, score: float) -> str:
    if direction == "exact":
        return f"Person level ({p_level}) matches role level ({r_level}) exactly."
    elif direction == "under" and gap <= 1:
        return f"One level promotion ({p_level}→{r_level}), appropriate stretch."
    elif direction == "under":
        return f"Person level ({p_level}) is {gap} levels below role ({r_level}), penalty applied."
    elif gap <= 1:
        return f"Person level ({p_level}) is 1 above role ({r_level}), within tolerance."
    else:
        return f"Person level ({p_level}) is {gap} levels above role ({r_level}), overqualified penalty."


def _build_summary_ko(
    name: str, title: str, fit: float, predicted: float, steps: list[ScoreStep]
) -> str:
    best = max(steps[:3], key=lambda s: s.weighted_value)
    worst = min(steps, key=lambda s: s.weighted_value)

    return (
        f"{name}의 {title} 적합도는 {fit:.1%}이며, "
        f"예측 성과는 {predicted}/5.0입니다. "
        f"가장 강한 요소는 {best.component_ko}({best.intermediate_value:.2f}), "
        f"가장 약한 요소는 {worst.component_ko}({worst.intermediate_value:.2f})입니다."
    )


def _build_summary_en(
    name: str, title: str, fit: float, predicted: float, steps: list[ScoreStep]
) -> str:
    best = max(steps[:3], key=lambda s: s.weighted_value)
    worst = min(steps, key=lambda s: s.weighted_value)

    return (
        f"{name}'s fit for {title} is {fit:.1%} with predicted performance {predicted}/5.0. "
        f"Strongest factor: {best.component}({best.intermediate_value:.2f}), "
        f"weakest: {worst.component}({worst.intermediate_value:.2f})."
    )
