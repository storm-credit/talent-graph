# TalentGraph

## 프로젝트 개요
FM식 HR 시뮬레이터. Ontology 기반 workforce simulation engine.
사람(Person) + 역할(Role) + 부서(Department) + 성과(Outcome) + 시간(Time) 5축 중심 관계 기반 시뮬레이션.
Bayesian 역량 추정 엔진으로 프로젝트 결과 기반 객관적 인재 평가.

## 기술 스택
- Backend: Python 3.14, Pydantic 2, NetworkX, FastAPI, NumPy
- Frontend: React 19, Vite, Tailwind CSS, shadcn/ui, Nivo, React Flow, Framer Motion
- Test: pytest (Python), Vitest (TS)

## 핵심 규칙
- 기존 ontology/scoring 코드 변경 금지 (확장만 허용)
- 모든 도메인 모델은 Pydantic BaseModel 사용
- UUID는 uuid5(NS, key)로 결정적 생성 (시드 데이터)
- 테스트 없는 코드 머지 금지
- Python은 ruff 포맷, TS는 prettier 포맷
- .env 파일 수정/커밋 금지
- 최소 diff 우선 — 불필요한 리팩토링 금지
- 한글 주석은 기존에 있는 경우만 유지
- 새 기능은 반드시 테스트와 함께 구현

## 디렉토리 구조
- `src/talentgraph/ontology/` — 핵심 도메인 모델 (수정 금지)
- `src/talentgraph/scoring/` — 스코어링 엔진 (수정 금지)
- `src/talentgraph/simulation/` — 시뮬레이션 엔진
- `src/talentgraph/estimation/` — Bayesian 역량 추정 엔진
- `src/talentgraph/api/` — FastAPI 백엔드
- `src/talentgraph/api/routers/` — API 라우터 (estimation, company_profile)
- `src/talentgraph/data/` — 시드 데이터 + JSON 로더
- `src/talentgraph/cli/` — CLI (Typer)
- `frontend/src/pages/` — 페이지 컴포넌트
- `frontend/src/components/` — 공통 컴포넌트
- `frontend/src/components/estimation/` — 역량 추정 UI 컴포넌트

## 스코어링 공식
```
FitScore = 0.40*SkillMatch + 0.30*HistoricalPerf + 0.15*LevelMatch - 0.15*BurnoutRisk
PredictedPerf = 1.0 + fit*4.0 + (history-0.5)*0.5  (clamped 1-5)
```

## Bayesian 추정 공식
```
Prior: dreyfus_prior(title, years) → (mu, sigma)
Update: precision-weighted Normal-Normal conjugate
Signal: IRT difficulty × result → observed skill level
Noise: TrueSkill role-based observation sigma
Confidence: 1.0 - sigma / SIGMA_INITIAL
```

## 실행 방법
```bash
# 백엔드
pip install -e ".[dev]"
uvicorn talentgraph.api.app:app --reload --port 8004

# 프론트엔드
cd frontend && npm run dev

# 테스트
pytest -v
```

## 워크플로우
- UI 변경 시: 관련 컴포넌트 먼저 확인 → 수정 → 브라우저 확인
- 백엔드 변경 시: 스키마 + 테스트 함께 확인
- 새 API 추가 시: router → deps → app.py include → 테스트 순서
