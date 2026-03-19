---
name: codebase-overview
description: TalentGraph 프로젝트 구조와 아키텍처 가이드
---

# TalentGraph 코드베이스 구조

## Backend (Python)

### 핵심 도메인 (수정 금지)
- `src/talentgraph/ontology/` — Person, Role, Department, Skill, Company 모델
- `src/talentgraph/scoring/` — FitScore, PredictedPerf 계산

### 시뮬레이션
- `src/talentgraph/simulation/engine.py` — EnhancedSimulationEngine (분기별 시뮬레이션)
- `src/talentgraph/simulation/quarter.py` — 분기 진행 로직
- `src/talentgraph/simulation/growth.py` — 스킬 성장/감소
- `src/talentgraph/simulation/morale.py` — 사기 시스템
- `src/talentgraph/simulation/random_events.py` — 랜덤 이벤트

### Bayesian 역량 추정
- `src/talentgraph/estimation/bayesian.py` — Normal-Normal conjugate update
- `src/talentgraph/estimation/prior.py` — Dreyfus 기반 초기 prior
- `src/talentgraph/estimation/store.py` — EstimationStore (인메모리)
- `src/talentgraph/estimation/models.py` — Project, SkillEstimate 등
- `src/talentgraph/estimation/csv_import.py` — CSV 임포트 (한/영)

### API
- `src/talentgraph/api/app.py` — FastAPI app, 라우터 등록
- `src/talentgraph/api/deps.py` — 싱글톤 의존성 (engine, estimation_store)
- `src/talentgraph/api/routers/estimation.py` — 프로젝트/추정 API
- `src/talentgraph/api/routers/company_profile.py` — 회사 프로필 API

## Frontend (React + TypeScript)

### 페이지
- `frontend/src/App.tsx` — 라우팅
- `frontend/src/pages/ProjectsPage.tsx` — 프로젝트 관리 + 스카우트 리포트
- `frontend/src/components/AppShell.tsx` — 네비게이션 쉘

### 역량 추정 컴포넌트
- `frontend/src/components/estimation/ScoutReport.tsx` — FM 스타일 스카우트 리포트
- `frontend/src/components/estimation/SkillEstimateBar.tsx` — 역량 막대 그래프
- `frontend/src/components/estimation/DifficultyBadge.tsx` — 난이도 배지
- `frontend/src/components/estimation/TrendArrow.tsx` — 추세 화살표

### 공통
- `frontend/src/api.ts` — API 클라이언트
- `frontend/src/types.ts` — TypeScript 인터페이스
- `frontend/src/i18n/` — 한/영 다국어 (ko.json, en.json)

## 테스트
- `tests/test_estimation/` — Bayesian 엔진 테스트 (54개)
- `tests/test_company/` — 회사 프로필 API 테스트
- `tests/test_simulation/` — 시뮬레이션 테스트
- `tests/test_ontology/` — 온톨로지 모델 테스트
- `tests/test_scoring/` — 스코어링 테스트

## 컨벤션
- Pydantic BaseModel로 모든 도메인 모델 정의
- UUID5 결정적 생성 (시드 데이터)
- FastAPI 라우터는 prefix + tags 사용
- 프론트엔드 다크 테마 (zinc 계열 색상)
