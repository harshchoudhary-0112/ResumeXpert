"""
ResumeXpert — FastAPI Application Entry Point

AI-Powered Resume Screening, Job Matching & Career Optimization System.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api import auth_router, resume_router, jobs_router, analysis_router

# Import all models so SQLAlchemy registers them before create_all
import app.models  # noqa: F401

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Application Lifespan ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")
    yield
    logger.info("Application shutting down.")


# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="ResumeXpert API",
    description=(
        "AI-Powered Resume Screening, Job Matching & Career Optimization System. "
        "Analyzes resumes against job descriptions using NLP, semantic similarity, "
        "ML classification, ATS compatibility checks, and explainable AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ─────────────────────────────────────────
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(jobs_router)
app.include_router(analysis_router)


# ── Health Check ──────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ResumeXpert API",
        "version": "1.0.0",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "service": "ResumeXpert API",
    }
