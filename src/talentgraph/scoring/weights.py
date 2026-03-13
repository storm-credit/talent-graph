from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    skill_match: float = Field(default=0.40, ge=0.0, le=1.0)
    historical_performance: float = Field(default=0.30, ge=0.0, le=1.0)
    level_match: float = Field(default=0.15, ge=0.0, le=1.0)
    burnout_risk: float = Field(default=0.15, ge=0.0, le=1.0)
