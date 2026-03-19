"""FastAPI application for TalentGraph."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from talentgraph.api.routers import company, company_profile, estimation, explainer, game, graph, people, recommendations, simulation, weights

app = FastAPI(
    title="TalentGraph API",
    description="FM-style HR simulation engine API",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(company.router)
app.include_router(people.router)
app.include_router(simulation.router)
app.include_router(graph.router)
app.include_router(weights.router)
app.include_router(explainer.router)
app.include_router(company_profile.router)
app.include_router(recommendations.router)
app.include_router(game.router)
app.include_router(estimation.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
