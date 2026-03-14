"""Registry of all algorithm formulas and glossary entries.

Each formula includes theoretical basis from IO psychology, HR analytics,
and organizational behavior research.
"""

from __future__ import annotations

from talentgraph.explainer.definitions import (
    ConstantDefinition,
    FormulaDefinition,
    GlossaryEntry,
    VariableDefinition,
)


def get_all_formulas() -> list[FormulaDefinition]:
    """Return all algorithm formula definitions with academic references."""
    return [
        # ── 1. Fit Score (Overall) ──
        FormulaDefinition(
            id="fit_score",
            name_ko="적합도 점수",
            name_en="Fit Score",
            formula_plain="FitScore = w_sm × SkillMatch + w_hp × Historical + w_lm × LevelMatch − w_br × BurnoutRisk",
            description_ko=(
                "사람이 특정 역할에 얼마나 적합한지를 0~1 사이 점수로 나타냅니다. "
                "스킬 매칭(40%), 과거 성과(30%), 레벨 매칭(15%), 번아웃 리스크(15%) "
                "네 가지 요소를 가중 합산합니다."
            ),
            description_en=(
                "Measures how well a person fits a specific role on a 0-1 scale. "
                "Combines skill matching (40%), historical performance (30%), "
                "level matching (15%), and burnout risk (15%) as a weighted sum."
            ),
            variables=[
                VariableDefinition(
                    symbol="SM",
                    name_ko="스킬 매칭",
                    name_en="Skill Match",
                    range="[0.0, 1.0]",
                    description_ko="사람의 스킬이 역할 요구사항에 얼마나 부합하는지",
                    description_en="How well the person's skills match role requirements",
                ),
                VariableDefinition(
                    symbol="HP",
                    name_ko="과거 성과",
                    name_en="Historical Performance",
                    range="[0.0, 1.0]",
                    description_ko="과거 업무 평가 결과의 가중 평균 (최근일수록 가중치 높음)",
                    description_en="Weighted average of past performance reviews (recent = higher weight)",
                ),
                VariableDefinition(
                    symbol="LM",
                    name_ko="레벨 매칭",
                    name_en="Level Match",
                    range="[0.0, 1.0]",
                    description_ko="사람의 경력 레벨이 역할 레벨에 얼마나 맞는지",
                    description_en="How well the person's career level matches the role level",
                ),
                VariableDefinition(
                    symbol="BR",
                    name_ko="번아웃 리스크",
                    name_en="Burnout Risk",
                    range="[0.0, 1.0]",
                    description_ko="현재 역할에서의 정체감과 성과 하락으로 인한 소진 위험도",
                    description_en="Risk of burnout from role stagnation and performance decline",
                ),
            ],
            constants=[
                ConstantDefinition(
                    symbol="w_sm",
                    name_en="Skill Match Weight",
                    value="0.40",
                    description_ko="스킬 매칭 가중치 (40%)",
                    description_en="Skill match weight (40%)",
                    source="Schmidt & Hunter (1998): skill/ability tests are strongest validity predictors",
                ),
                ConstantDefinition(
                    symbol="w_hp",
                    name_en="Historical Performance Weight",
                    value="0.30",
                    description_ko="과거 성과 가중치 (30%)",
                    description_en="Historical performance weight (30%)",
                    source="Past performance is second-best predictor of future performance",
                ),
                ConstantDefinition(
                    symbol="w_lm",
                    name_en="Level Match Weight",
                    value="0.15",
                    description_ko="레벨 매칭 가중치 (15%)",
                    description_en="Level match weight (15%)",
                    source="Benson et al. (2019): Peter Principle research on promotion fit",
                ),
                ConstantDefinition(
                    symbol="w_br",
                    name_en="Burnout Risk Weight",
                    value="0.15",
                    description_ko="번아웃 리스크 가중치 (15%, 감산)",
                    description_en="Burnout risk weight (15%, subtracted)",
                    source="Maslach & Leiter (2016): burnout as predictor of performance decline",
                ),
            ],
            theoretical_basis="Schmidt & Hunter (1998) meta-analysis of personnel selection validity",
            theoretical_basis_ko=(
                "Schmidt & Hunter (1998) 인사 선발 타당도 메타분석: "
                "능력 테스트(스킬)가 가장 높은 예측력, 과거 성과가 두 번째"
            ),
            category="scoring",
            related_formulas=["skill_match", "historical_performance", "level_match", "burnout_risk"],
        ),
        # ── 2. Predicted Performance ──
        FormulaDefinition(
            id="predicted_performance",
            name_ko="예측 성과",
            name_en="Predicted Performance",
            formula_plain="PredPerf = 1.0 + FitScore × 4.0 + (Historical − 0.5) × 0.5  [clamped 1-5]",
            description_ko=(
                "적합도를 기반으로 1~5점 사이의 예측 성과를 계산합니다. "
                "적합도가 높을수록 성과 예측치가 높고, 과거 이력이 추가 보정합니다."
            ),
            description_en=(
                "Predicts performance on a 1-5 scale based on fit score. "
                "Higher fit = higher predicted performance, with historical bias adjustment."
            ),
            variables=[
                VariableDefinition(
                    symbol="FitScore",
                    name_ko="적합도 점수",
                    name_en="Fit Score",
                    range="[0.0, 1.0]",
                    description_ko="위에서 계산된 종합 적합도",
                    description_en="Overall fit score calculated above",
                ),
            ],
            constants=[
                ConstantDefinition(
                    symbol="4.0",
                    name_en="Fit Scaling Factor",
                    value="4.0",
                    description_ko="적합도를 1-5 스케일로 변환하는 계수",
                    description_en="Scaling factor to convert fit to 1-5 scale",
                    source="Linear scaling: fit=0 → perf=1, fit=1 → perf=5",
                ),
                ConstantDefinition(
                    symbol="0.5",
                    name_en="History Bias",
                    value="0.5",
                    description_ko="과거 성과의 추가 보정 강도 (베이지안 사전확률)",
                    description_en="Historical performance adjustment strength (Bayesian prior)",
                    source="Bayesian reasoning: past performance as informative prior",
                ),
            ],
            theoretical_basis="Linear prediction with Bayesian prior adjustment",
            theoretical_basis_ko="선형 예측 모델 + 베이지안 사전확률 보정 (과거 성과 = 사전 믿음)",
            category="scoring",
            related_formulas=["fit_score"],
        ),
        # ── 3. Skill Match ──
        FormulaDefinition(
            id="skill_match",
            name_ko="스킬 매칭",
            name_en="Skill Match",
            formula_plain="SM = Σ(min(person_level / required_level, 1.0) × weight) / Σ(weight)",
            description_ko=(
                "역할이 요구하는 각 스킬에 대해 사람의 레벨을 비교합니다. "
                "레벨이 요구치 이상이면 1.0 (만점), 부족하면 비율만큼 감점됩니다. "
                "각 스킬의 중요도(가중치)에 따라 가중 평균을 냅니다."
            ),
            description_en=(
                "Compares person's skill levels against each role requirement. "
                "Meeting or exceeding = 1.0, below = proportional ratio. "
                "Weighted average by skill importance."
            ),
            variables=[
                VariableDefinition(
                    symbol="person_level",
                    name_ko="보유 스킬 레벨",
                    name_en="Person's Skill Level",
                    range="1-5 (Novice-Expert)",
                    description_ko="사람이 해당 스킬에서 보유한 등급",
                    description_en="Person's proficiency level in the skill",
                ),
                VariableDefinition(
                    symbol="required_level",
                    name_ko="요구 스킬 레벨",
                    name_en="Required Skill Level",
                    range="1-5 (Novice-Expert)",
                    description_ko="역할이 요구하는 최소 등급",
                    description_en="Minimum level required by the role",
                ),
            ],
            constants=[],
            theoretical_basis="Boyatzis (1982) Competency-Based HR Model",
            theoretical_basis_ko="Boyatzis (1982) 역량 기반 인사 모델: 역할별 핵심 역량 매칭",
            category="scoring",
            related_formulas=["fit_score"],
        ),
        # ── 4. Historical Performance ──
        FormulaDefinition(
            id="historical_performance",
            name_ko="과거 성과",
            name_en="Historical Performance",
            formula_plain="HP = Σ(normalized_rating × decay × role_boost) / Σ(decay × role_boost)",
            description_ko=(
                "과거 업무 평가 결과를 시간 감쇠 가중 평균으로 계산합니다. "
                "최근 성과에 더 높은 비중을 두고 (반감기 2년), "
                "현재 지원하는 역할과 같은 직무 경험은 1.5배 가산합니다."
            ),
            description_en=(
                "Time-weighted average of past performance reviews. "
                "Recent reviews weighted more (half-life 2 years), "
                "same-role experience gets 1.5x bonus."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="T½",
                    name_en="Half-life",
                    value="730 days (~2 years)",
                    description_ko="시간 감쇠 반감기: 2년 전 성과는 50% 가중치",
                    description_en="Exponential decay half-life: 2-year old reviews = 50% weight",
                    source="Murphy & Cleveland (1995): recency effects in performance appraisal",
                ),
                ConstantDefinition(
                    symbol="role_boost",
                    name_en="Same-Role Boost",
                    value="1.5",
                    description_ko="동일 직무 경험 가산 배수 (50% 추가)",
                    description_en="Multiplier for experience in the same role",
                    source="Role-specific experience is more predictive than general experience",
                ),
            ],
            theoretical_basis="Murphy & Cleveland (1995) Performance Appraisal literature",
            theoretical_basis_ko="Murphy & Cleveland (1995) 성과 평가 문헌: 최신효과 보정",
            category="scoring",
            related_formulas=["fit_score"],
        ),
        # ── 5. Level Match ──
        FormulaDefinition(
            id="level_match",
            name_ko="레벨 매칭",
            name_en="Level Match",
            formula_plain="LM = 1.0 if gap ≤ 1 else max(0, 1.0 − (gap−1) × 0.2)",
            description_ko=(
                "사람의 경력 레벨과 역할 레벨의 차이를 측정합니다. "
                "1단계 이내 차이는 만점(1.0), 그 이상은 단계당 0.2씩 감점합니다. "
                "예: 레벨 3인 사람이 레벨 7 역할에 지원하면 0.4 (큰 갭 = 위험)."
            ),
            description_en=(
                "Measures gap between person's career level and role level. "
                "±1 level gap = perfect (1.0), beyond that = 0.2 penalty per level."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="0.2",
                    name_en="Gap Penalty",
                    value="0.2 per level",
                    description_ko="1단계 초과시 단계당 감점",
                    description_en="Penalty per level beyond ±1 gap",
                    source="Benson et al. (2019): Peter Principle — promotion beyond competence hurts performance",
                ),
            ],
            theoretical_basis="Benson, Li & Shue (2019) 'Promotions and the Peter Principle'",
            theoretical_basis_ko="Benson et al. (2019) 피터의 법칙 연구: 과도한 승진은 성과를 떨어뜨림",
            category="scoring",
            related_formulas=["fit_score"],
        ),
        # ── 6. Burnout Risk ──
        FormulaDefinition(
            id="burnout_risk",
            name_ko="번아웃 리스크",
            name_en="Burnout Risk",
            formula_plain="BR = 0.6 × Staleness + 0.4 × PerformanceDecline",
            description_ko=(
                "현재 역할에서의 소진 위험도를 측정합니다. "
                "정체감(60%)과 성과 하락 추세(40%)를 결합합니다. "
                "같은 역할에 오래 있을수록, 성과가 떨어질수록 번아웃 위험이 높아집니다."
            ),
            description_en=(
                "Measures risk of burnout in current role. "
                "Combines role staleness (60%) and performance decline trend (40%)."
            ),
            variables=[
                VariableDefinition(
                    symbol="Staleness",
                    name_ko="정체감",
                    name_en="Role Staleness",
                    range="[0.0, 1.0]",
                    description_ko="같은 역할 재직 기간에 따른 정체 리스크",
                    description_en="Stagnation risk based on time in same role",
                ),
                VariableDefinition(
                    symbol="Decline",
                    name_ko="성과 하락",
                    name_en="Performance Decline",
                    range="[0.0, 1.0]",
                    description_ko="최근 성과가 이전보다 하락하는 추세",
                    description_en="Trend of declining performance ratings",
                ),
            ],
            constants=[
                ConstantDefinition(
                    symbol="thresholds",
                    name_en="Staleness Thresholds",
                    value="≤2y: 0.0, 2-3y: 0.2, 3-5y: 0.5, >5y: 0.8",
                    description_ko="재직 기간별 정체 리스크 단계",
                    description_en="Staleness risk by years in role",
                    source="Maslach & Leiter (2016): Maslach Burnout Inventory framework",
                ),
            ],
            theoretical_basis="Maslach & Leiter (2016) Maslach Burnout Inventory (MBI)",
            theoretical_basis_ko="Maslach & Leiter (2016) 번아웃 인벤토리: 정체감이 소진의 주요 원인",
            category="scoring",
            related_formulas=["fit_score"],
        ),
        # ── 7. Skill Growth ──
        FormulaDefinition(
            id="skill_growth",
            name_ko="스킬 성장",
            name_en="Skill Growth",
            formula_plain="P(growth) = base_prob[gap] × learning_rate × morale_mod × tenure_mod",
            description_ko=(
                "매 분기, 활발히 사용하는 스킬이 한 단계 성장할 확률입니다. "
                "현재 레벨과 잠재력(PA) 사이의 갭이 클수록 성장 확률이 높고, "
                "학습속도, 사기, 재직기간이 확률을 조절합니다."
            ),
            description_en=(
                "Each quarter, probability that an active skill levels up. "
                "Larger gap to potential = higher probability, "
                "modified by learning rate, morale, and tenure."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="base_prob",
                    name_en="Growth Probability by Gap",
                    value="gap 0: 0%, 1: 15%, 2: 25%, 3: 35%, 4: 40%",
                    description_ko="잠재력과의 갭에 따른 기본 성장 확률",
                    description_en="Base growth probability by gap to potential",
                    source="Dreyfus Skill Acquisition Model: novice→expert progression",
                ),
                ConstantDefinition(
                    symbol="morale_mod",
                    name_en="Morale Modifier",
                    value="1.0 + max(0, (morale-0.5)) × 0.6  → [1.0, 1.3]",
                    description_ko="사기가 0.5 이상이면 성장 확률 최대 30% 가산",
                    description_en="High morale (>0.5) boosts growth probability up to 30%",
                    source="Motivation-learning link from Self-Determination Theory (Deci & Ryan)",
                ),
            ],
            theoretical_basis="Dreyfus Model of Skill Acquisition + Self-Determination Theory",
            theoretical_basis_ko="Dreyfus 스킬 습득 모델 (초보→전문가 5단계) + 자기결정이론 (동기부여↔학습)",
            category="growth",
            related_formulas=["skill_decay"],
        ),
        # ── 8. Skill Decay ──
        FormulaDefinition(
            id="skill_decay",
            name_ko="스킬 감퇴",
            name_en="Skill Decay",
            formula_plain="if quarters_idle ≥ 4: P(decay) = 10% per quarter",
            description_ko=(
                "4분기(1년) 이상 사용하지 않은 스킬은 매 분기 10% 확률로 한 단계 하락합니다. "
                "자주 쓰지 않으면 실력이 녹스는 '망각 곡선' 효과입니다."
            ),
            description_en=(
                "Skills unused for 4+ quarters have a 10% chance per quarter of dropping one level. "
                "Models the 'forgetting curve' effect."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="DECAY_IDLE_THRESHOLD",
                    name_en="Idle Threshold",
                    value="4 quarters (1 year)",
                    description_ko="감퇴가 시작되는 유휴 기간",
                    description_en="Quarters of inactivity before decay risk",
                    source="Ebbinghaus (1885) forgetting curve approximation",
                ),
                ConstantDefinition(
                    symbol="DECAY_PROBABILITY",
                    name_en="Decay Probability",
                    value="0.10 (10%) per quarter",
                    description_ko="유휴 스킬의 분기당 감퇴 확률",
                    description_en="Quarterly decay probability for idle skills",
                    source="Simplified spaced repetition model",
                ),
            ],
            theoretical_basis="Ebbinghaus (1885) Forgetting Curve",
            theoretical_basis_ko="Ebbinghaus (1885) 망각 곡선: 사용하지 않으면 기억/능력이 감쇠",
            category="growth",
            related_formulas=["skill_growth"],
        ),
        # ── 9. Morale System ──
        FormulaDefinition(
            id="morale_system",
            name_ko="사기 시스템",
            name_en="Morale System",
            formula_plain=(
                "Δ morale = outcome_delta + placement_boost + burnout_drag "
                "+ stagnation_penalty + mean_reversion + noise"
            ),
            description_ko=(
                "매 분기 사기(0~1)가 여러 요인에 의해 변합니다: "
                "좋은 성과 → 사기↑, 나쁜 성과 → 사기↓, "
                "새 역할 배치 → +0.10, 번아웃 높으면 → 지속 하락, "
                "3년 이상 같은 역할 → 정체감 패널티, "
                "극단적 사기는 자연스럽게 0.5(중간)로 회귀합니다."
            ),
            description_en=(
                "Morale (0-1) changes each quarter based on: "
                "performance outcomes, new placement boost, burnout drag, "
                "stagnation penalty, and natural mean reversion toward 0.5."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="outcome_delta",
                    name_en="Outcome Morale Deltas",
                    value="Exceptional: +0.08, Exceeds: +0.04, Meets: 0, Below: −0.05, Unsatisfactory: −0.10",
                    description_ko="성과 등급에 따른 사기 변화량",
                    description_en="Morale change per outcome rating",
                    source="Hackman & Oldham (1976) Job Characteristics Model: feedback → satisfaction",
                ),
                ConstantDefinition(
                    symbol="MEAN_REVERSION",
                    name_en="Mean Reversion Rate",
                    value="0.05 toward 0.5",
                    description_ko="극단적 사기가 중간(0.5)으로 자연 회귀하는 속도",
                    description_en="Speed at which extreme morale naturally reverts to 0.5",
                    source="Hedonic Adaptation Theory: people return to baseline happiness over time",
                ),
                ConstantDefinition(
                    symbol="BURNOUT_DRAG",
                    name_en="Burnout Morale Drag",
                    value="−0.03 per 0.1 burnout above 0.3",
                    description_ko="번아웃이 0.3 이상이면 사기가 지속적으로 하락",
                    description_en="Persistent morale drain when burnout > 0.3",
                    source="Maslach (2003): burnout-morale negative feedback loop",
                ),
                ConstantDefinition(
                    symbol="PLACEMENT_BOOST",
                    name_en="Placement Morale Boost",
                    value="+0.10",
                    description_ko="새 역할 배치 시 사기 +10%",
                    description_en="Morale boost from being placed in a new role",
                    source="Job rotation literature: novelty improves engagement",
                ),
                ConstantDefinition(
                    symbol="STAGNATION",
                    name_en="Stagnation Penalty",
                    value="−0.02 per quarter after 3 years",
                    description_ko="3년 이상 같은 역할 시 분기당 사기 −2%",
                    description_en="Morale penalty per quarter when in same role >3 years",
                    source="Career plateau research: prolonged stagnation reduces engagement",
                ),
            ],
            theoretical_basis="Hackman & Oldham (1976) Job Characteristics Model + Hedonic Adaptation",
            theoretical_basis_ko="Hackman & Oldham (1976) 직무 특성 모델 + 쾌락 적응 이론",
            category="morale",
            related_formulas=["burnout_risk", "attrition"],
        ),
        # ── 10. Attrition Model ──
        FormulaDefinition(
            id="attrition",
            name_ko="이직 모델",
            name_en="Attrition Model",
            formula_plain="P(leave) = (base + burnout_factor + morale_factor) × tenure_multiplier  [max 30%]",
            description_ko=(
                "매 분기 직원이 퇴사할 확률을 계산합니다. "
                "기본 이직률(2%) + 번아웃 위험 가산 + 저사기 가산에 "
                "재직기간 U자 곡선을 곱합니다. "
                "신입(1년 미만)과 장기 재직자(8년+)의 이직 위험이 높습니다."
            ),
            description_en=(
                "Calculates quarterly probability of departure. "
                "Base rate (2%) + burnout factor + low morale factor, "
                "multiplied by U-shaped tenure curve."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="BASE_RATE",
                    name_en="Base Attrition Rate",
                    value="0.02 (2% per quarter ≈ 8% annually)",
                    description_ko="기본 분기 이직률",
                    description_en="Baseline quarterly turnover rate",
                    source="BLS average separation rate for professional/technical roles",
                ),
                ConstantDefinition(
                    symbol="tenure_curve",
                    name_en="Tenure U-Curve",
                    value="<1y: 1.5×, 1-5y: 1.0×, 5-8y: ramp to 1.2×, >8y: 1.5×",
                    description_ko="재직기간별 이직 위험 배수 (U자형)",
                    description_en="Tenure-based attrition multiplier (U-shaped)",
                    source="March & Simon (1958) Organizational Equilibrium Theory + labor market data",
                ),
                ConstantDefinition(
                    symbol="BURNOUT_FACTOR",
                    name_en="Burnout Factor",
                    value="0.15 × max(0, burnout − 0.3)",
                    description_ko="번아웃이 30% 이상이면 이직 확률 증가",
                    description_en="Attrition increase when burnout exceeds 30%",
                    source="Burnout-turnover link from organizational psychology literature",
                ),
                ConstantDefinition(
                    symbol="MAX",
                    name_en="Maximum Quarterly Attrition",
                    value="0.30 (30%)",
                    description_ko="분기 최대 이직 확률 상한",
                    description_en="Hard cap on quarterly departure probability",
                    source="Design constraint: prevents entire team from leaving at once",
                ),
            ],
            theoretical_basis="March & Simon (1958) Organizational Equilibrium Theory",
            theoretical_basis_ko="March & Simon (1958) 조직 균형 이론: 이탈 동기 = 불만족 + 대안 가용성",
            category="attrition",
            related_formulas=["morale_system", "burnout_risk"],
        ),
        # ── 11. Outcome Distribution ──
        FormulaDefinition(
            id="outcome_distribution",
            name_ko="성과 분포",
            name_en="Outcome Distribution",
            formula_plain="Rating ~ Categorical(probs[bucket(PredictedPerf)])",
            description_ko=(
                "예측 성과를 5개 버킷(1~5)으로 나누고, 각 버킷에서 "
                "확률 분포에 따라 실제 성과 등급을 무작위로 결정합니다. "
                "예측이 높아도 운이 나쁘면 낮은 등급이 나올 수 있고, "
                "예측이 낮아도 좋은 등급이 나올 수 있습니다."
            ),
            description_en=(
                "Maps predicted performance to a probability distribution "
                "and randomly samples the actual outcome rating. "
                "Higher prediction = higher probability of good outcomes, but not guaranteed."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="probs",
                    name_en="Outcome Probability Table",
                    value=(
                        "Bucket 1: [40%, 35%, 20%, 5%, 0%], "
                        "Bucket 3: [5%, 15%, 50%, 25%, 5%], "
                        "Bucket 5: [0%, 5%, 15%, 35%, 45%]"
                    ),
                    description_ko="예측 성과 버킷별 [최하, 하, 보통, 상, 최상] 확률",
                    description_en="Probability of each rating per predicted performance bucket",
                    source="Empirical distribution modeling performance variance",
                ),
            ],
            theoretical_basis="Stochastic performance modeling with variance",
            theoretical_basis_ko="확률적 성과 모델링: 예측 ≠ 확정, 실제 결과에는 편차(분산)가 존재",
            category="simulation",
            related_formulas=["predicted_performance"],
        ),
        # ── 12. Random Events ──
        FormulaDefinition(
            id="random_events",
            name_ko="랜덤 이벤트",
            name_en="Random Events",
            formula_plain="P(event) per quarter: company-wide + individual",
            description_ko=(
                "매 분기 회사 전체 또는 개인에게 랜덤 이벤트가 발생할 수 있습니다. "
                "시장 호황/불황(각 5%), 조직 개편(3%), "
                "개인: 자격증 취득(8%), 개인 사정(5%), 멘토링(6%)."
            ),
            description_en=(
                "Random events can occur each quarter at company or individual level. "
                "Market boom/downturn (5% each), reorg (3%), "
                "certification (8%), personal issue (5%), mentoring (6%)."
            ),
            variables=[],
            constants=[
                ConstantDefinition(
                    symbol="company_probs",
                    name_en="Company Event Probabilities",
                    value="Market Boom: 5%, Market Downturn: 5%, Reorg: 3%",
                    description_ko="회사 전체에 영향을 미치는 이벤트 확률",
                    description_en="Probabilities of company-wide events",
                    source="Industry event frequency estimates",
                ),
                ConstantDefinition(
                    symbol="individual_probs",
                    name_en="Individual Event Probabilities",
                    value="Certification: 8%, Personal Issue: 5%, Mentoring: 6%",
                    description_ko="개인별 이벤트 발생 확률",
                    description_en="Per-person event probabilities per quarter",
                    source="HR event frequency benchmarks",
                ),
            ],
            theoretical_basis="Stochastic event modeling for organizational dynamics",
            theoretical_basis_ko="조직 역학의 확률적 이벤트 모델링: 예측 불가능한 상황 시뮬레이션",
            category="events",
            related_formulas=["morale_system"],
        ),
    ]


def get_glossary() -> list[GlossaryEntry]:
    """Return all glossary entries."""
    return [
        # Core concepts
        GlossaryEntry(
            id="fit_score",
            term_ko="적합도 점수",
            term_en="Fit Score",
            definition_ko="사람이 특정 역할에 얼마나 적합한지를 0~1(0~100%) 사이로 나타낸 종합 점수",
            definition_en="Overall score (0-1) measuring how well a person matches a specific role",
            category="core",
        ),
        GlossaryEntry(
            id="predicted_performance",
            term_ko="예측 성과",
            term_en="Predicted Performance",
            definition_ko="적합도를 기반으로 예측한 업무 수행 능력 (1~5점)",
            definition_en="Predicted job performance score (1-5) based on fit",
            category="core",
        ),
        GlossaryEntry(
            id="ca",
            term_ko="현재 능력 (CA)",
            term_en="Current Ability (CA)",
            definition_ko="사람이 현재 보유한 스킬 레벨. Novice(1) → Expert(5)",
            definition_en="Person's current skill level, from Novice (1) to Expert (5)",
            category="skill",
        ),
        GlossaryEntry(
            id="pa",
            term_ko="잠재 능력 (PA)",
            term_en="Potential Ability (PA)",
            definition_ko="스킬이 성장할 수 있는 최대 천장 레벨. CA가 PA에 도달하면 더 이상 성장하지 않음",
            definition_en="Maximum ceiling level a skill can grow to. Growth stops when CA reaches PA",
            category="skill",
        ),
        GlossaryEntry(
            id="morale",
            term_ko="사기",
            term_en="Morale",
            definition_ko="직원의 전반적인 만족도와 의욕 (0~1). 성과, 번아웃, 배치 등에 의해 변동",
            definition_en="Employee's overall satisfaction and motivation (0-1). Changes based on performance, burnout, placement",
            category="core",
        ),
        GlossaryEntry(
            id="burnout_risk",
            term_ko="번아웃 리스크",
            term_en="Burnout Risk",
            definition_ko="현재 역할에서의 소진 위험도 (0~1). 오래 같은 역할 + 성과 하락 = 높은 번아웃",
            definition_en="Risk of burnout (0-1). Long tenure in same role + declining performance = high burnout",
            category="core",
        ),
        GlossaryEntry(
            id="tenure",
            term_ko="재직기간",
            term_en="Tenure",
            definition_ko="현재 회사에서 일한 총 기간 (년 단위). 분기마다 0.25년씩 증가",
            definition_en="Total years worked at the company. Increases 0.25 per quarter",
            category="core",
        ),
        GlossaryEntry(
            id="learning_rate",
            term_ko="학습속도",
            term_en="Learning Rate",
            definition_ko="스킬 성장 속도를 조절하는 개인 특성 (기본 1.0). 높을수록 빠르게 성장",
            definition_en="Personal trait that modifies skill growth speed (default 1.0). Higher = faster growth",
            category="skill",
        ),
        GlossaryEntry(
            id="potential",
            term_ko="잠재력",
            term_en="Potential",
            definition_ko="직원의 전반적인 성장 가능성 (0~1). 높을수록 다양한 역할에서 성장 여지가 큼",
            definition_en="Overall growth potential (0-1). Higher = more room for growth across roles",
            category="core",
        ),
        GlossaryEntry(
            id="skill_match",
            term_ko="스킬 매칭",
            term_en="Skill Match",
            definition_ko="사람의 스킬이 역할이 요구하는 스킬에 얼마나 부합하는지 (0~1)",
            definition_en="How well a person's skills match role requirements (0-1)",
            category="scoring",
        ),
        GlossaryEntry(
            id="historical_perf",
            term_ko="과거 성과",
            term_en="Historical Performance",
            definition_ko="과거 업무 평가 결과의 가중 평균. 최근 평가일수록 더 높은 가중치",
            definition_en="Weighted average of past reviews. More recent reviews have higher weight",
            category="scoring",
        ),
        GlossaryEntry(
            id="level_match",
            term_ko="레벨 매칭",
            term_en="Level Match",
            definition_ko="경력 레벨과 역할 레벨의 적합도. 갭이 클수록 점수 하락",
            definition_en="Career level vs role level fit. Larger gap = lower score",
            category="scoring",
        ),
        GlossaryEntry(
            id="outcome_rating",
            term_ko="성과 등급",
            term_en="Outcome Rating",
            definition_ko="분기별 업무 평가 결과 (최하/하/보통/상/최상 5단계)",
            definition_en="Quarterly performance rating (Unsatisfactory/Below/Meets/Exceeds/Exceptional)",
            category="simulation",
        ),
        GlossaryEntry(
            id="attrition",
            term_ko="이직",
            term_en="Attrition",
            definition_ko="직원이 회사를 떠나는 것. 번아웃, 낮은 사기, 재직기간에 따라 확률 결정",
            definition_en="Employee departure. Probability based on burnout, low morale, and tenure curve",
            category="simulation",
        ),
        GlossaryEntry(
            id="quarter",
            term_ko="분기",
            term_en="Quarter",
            definition_ko="시뮬레이션의 기본 시간 단위. 1년 = 4분기 (Q1~Q4)",
            definition_en="Basic time unit of simulation. 1 year = 4 quarters (Q1-Q4)",
            category="simulation",
        ),
        GlossaryEntry(
            id="mean_reversion",
            term_ko="평균 회귀",
            term_en="Mean Reversion",
            definition_ko="극단적인 사기가 시간이 지나면 자연스럽게 중간(0.5)으로 돌아가는 현상",
            definition_en="Tendency for extreme morale to naturally return to the middle (0.5) over time",
            category="simulation",
        ),
        GlossaryEntry(
            id="stagnation",
            term_ko="정체감",
            term_en="Stagnation",
            definition_ko="같은 역할에 오래 있어 성장이 멈추고 의욕이 떨어지는 상태",
            definition_en="State of no growth when staying too long in the same role",
            category="simulation",
        ),
        GlossaryEntry(
            id="placement",
            term_ko="배치",
            term_en="Placement",
            definition_ko="사람을 특정 역할/부서에 배정하는 것. 새 배치는 사기를 올림",
            definition_en="Assigning a person to a role/department. New placements boost morale",
            category="core",
        ),
        GlossaryEntry(
            id="department",
            term_ko="부서",
            term_en="Department",
            definition_ko="조직 내 기능 단위 (예: 데이터 엔지니어링, 재무). 각 부서에 역할들이 속함",
            definition_en="Functional unit within the organization. Contains multiple roles",
            category="core",
        ),
        GlossaryEntry(
            id="role",
            term_ko="역할",
            term_en="Role",
            definition_ko="직무 포지션 (예: Sr Data Engineer L6). 필요 스킬과 레벨 요구사항이 정의됨",
            definition_en="Job position (e.g., Sr Data Engineer L6). Has defined skill requirements",
            category="core",
        ),
        GlossaryEntry(
            id="enhanced_mode",
            term_ko="강화 모드",
            term_en="Enhanced Mode",
            definition_ko="스킬 성장, 사기, 이직, 랜덤 이벤트가 모두 활성화된 시뮬레이션 모드",
            definition_en="Simulation mode with all systems active: skill growth, morale, attrition, events",
            category="simulation",
        ),
        GlossaryEntry(
            id="skill_level",
            term_ko="스킬 레벨",
            term_en="Skill Level",
            definition_ko="5단계: Novice(초보) → Beginner(초급) → Intermediate(중급) → Advanced(고급) → Expert(전문가)",
            definition_en="5 levels: Novice → Beginner → Intermediate → Advanced → Expert",
            category="skill",
        ),
        GlossaryEntry(
            id="critical_skill",
            term_ko="핵심 스킬",
            term_en="Critical Skill",
            definition_ko="역할 수행에 필수적인 스킬. 이 스킬이 없으면 적합도가 크게 감점됨",
            definition_en="Essential skill for a role. Missing it causes major fit score penalty",
            category="scoring",
        ),
        GlossaryEntry(
            id="culture_fit",
            term_ko="문화 적합도",
            term_en="Culture Fit",
            definition_ko="개인의 성향/특성이 부서 문화에 얼마나 맞는지 (강화 모드 전용)",
            definition_en="How well a person's traits match department culture (enhanced mode only)",
            category="scoring",
        ),
    ]
