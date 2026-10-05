"""Schemas package."""

from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse, UserProfile
from app.schemas.resume import ParsedResume, ResumeResponse, ResumeListItem
from app.schemas.job import JobDescriptionCreate, JobDescriptionResponse, JobDescriptionListItem
from app.schemas.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisHistoryItem,
    SuggestionResponse, DashboardStats, ScoreBreakdown,
    MatchedSkill, ATSFinding, SHAPExplanation,
)
