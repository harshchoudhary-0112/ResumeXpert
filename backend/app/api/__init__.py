"""API routes package."""

from app.api.auth import router as auth_router
from app.api.resume import router as resume_router
from app.api.jobs import router as jobs_router
from app.api.analysis import router as analysis_router

__all__ = ["auth_router", "resume_router", "jobs_router", "analysis_router"]
