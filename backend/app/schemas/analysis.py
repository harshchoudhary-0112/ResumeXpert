"""Pydantic schemas for analysis results, suggestions, and history."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


class AnalysisRequest(BaseModel):
    """Request body to trigger an analysis."""
    resume_id: int
    job_id: int


class ScoreBreakdown(BaseModel):
    """Individual component score with weight information."""
    component: str
    score: float             # 0–100
    weight: float            # 0–1
    weighted_score: float    # score * weight


class MatchedSkill(BaseModel):
    """A skill found in both resume and JD."""
    skill: str
    category: str
    found_in_resume: bool = True
    found_in_jd: bool = True


class ATSFinding(BaseModel):
    """An ATS compatibility issue."""
    issue: str
    severity: str            # "critical", "warning", "info"
    recommendation: str


class SHAPExplanation(BaseModel):
    """SHAP feature contribution for ML explainability."""
    feature: str
    value: float             # Raw feature value
    contribution: float      # SHAP value (positive = towards match)


class SuggestionResponse(BaseModel):
    """A single improvement suggestion."""
    id: int
    category: str
    suggestion: str
    severity: str
    evidence: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    """Full analysis result returned to the frontend."""
    id: int
    resume_id: int
    job_id: int

    # Scores
    match_score: float
    score_breakdown: List[ScoreBreakdown] = Field(default_factory=list)

    # Classification
    classification: str
    classification_confidence: Optional[float] = None

    # Skill analysis
    matched_skills: List[MatchedSkill] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)

    # ATS
    ats_score: float
    ats_findings: List[ATSFinding] = Field(default_factory=list)

    # Explainability
    shap_explanation: List[SHAPExplanation] = Field(default_factory=list)

    # Suggestions
    suggestions: List[SuggestionResponse] = Field(default_factory=list)

    # Metadata
    resume_name: Optional[str] = None
    job_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisHistoryItem(BaseModel):
    """Lightweight analysis item for history list views."""
    id: int
    match_score: float
    classification: str
    resume_filename: Optional[str] = None
    job_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Aggregated statistics for the user dashboard."""
    total_analyses: int = 0
    total_resumes: int = 0
    total_jobs: int = 0
    average_score: float = 0.0
    highest_score: float = 0.0
    recent_analyses: List[AnalysisHistoryItem] = Field(default_factory=list)
    score_distribution: Dict[str, int] = Field(default_factory=dict)  # e.g. {"0-20": 1, "20-40": 3, ...}
    top_missing_skills: List[Dict[str, Any]] = Field(default_factory=list)
