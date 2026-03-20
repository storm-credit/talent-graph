# ── Backend: FastAPI ──────────────────────────────────────────────────
FROM python:3.12-slim AS backend

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

EXPOSE 8004

CMD ["uvicorn", "talentgraph.api.app:app", "--host", "0.0.0.0", "--port", "8004"]
