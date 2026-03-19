---
name: tdd-workflow
description: TalentGraph용 TDD 워크플로우 — pytest + FastAPI TestClient
---

# TDD 워크플로우

## 원칙
1. 실패하는 테스트 먼저 작성 (RED)
2. 최소한의 코드로 통과시키기 (GREEN)
3. 리팩토링 (REFACTOR)
4. 커버리지 확인

## Python 테스트 패턴

### 단위 테스트
```python
import pytest
from talentgraph.estimation.bayesian import bayesian_update

class TestBayesianUpdate:
    def test_posterior_moves_toward_observation(self):
        mu, sigma = bayesian_update(2.0, 1.0, 4.0, 1.0)
        assert 2.0 < mu < 4.0
```

### API 테스트
```python
import pytest
from fastapi.testclient import TestClient
from talentgraph.api.app import app

@pytest.fixture
def client():
    return TestClient(app)

class TestEstimationAPI:
    def test_create_project(self, client):
        resp = client.post("/api/estimation/projects", json={...})
        assert resp.status_code == 200
```

## 실행
```bash
# 전체
pytest -v

# 특정 모듈
pytest tests/test_estimation/ -v

# 특정 테스트
pytest tests/test_estimation/test_bayesian.py::TestBayesianUpdate -v

# 커버리지
pytest --cov=talentgraph --cov-report=term-missing
```

## 주의사항
- ontology/scoring 테스트는 기존 것 수정 금지
- 새 모듈 추가 시 `tests/test_<module>/` 디렉토리 생성
- conftest.py에 공통 fixture 정의
- API 테스트는 httpx TestClient 사용
