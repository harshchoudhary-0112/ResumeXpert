"""
Application configuration using pydantic-settings.
All settings can be overridden via environment variables or a .env file.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./resumexpert.db"

    # ── JWT Authentication ────────────────────────────────────
    SECRET_KEY: str = "resumexpert-dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── File Upload ───────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]

    # ── Matching Weights (configurable) ───────────────────────
    SKILL_MATCH_WEIGHT: float = 0.40
    SEMANTIC_SIMILARITY_WEIGHT: float = 0.25
    EXPERIENCE_MATCH_WEIGHT: float = 0.15
    EDUCATION_MATCH_WEIGHT: float = 0.10
    ATS_COMPATIBILITY_WEIGHT: float = 0.05
    PROJECT_RELEVANCE_WEIGHT: float = 0.05

    # ── NLP Model Config ─────────────────────────────────────
    SPACY_MODEL: str = "en_core_web_sm"
    SBERT_MODEL: str = "all-MiniLM-L6-v2"

    # ── ML Model Paths ────────────────────────────────────────
    TRAINED_MODEL_DIR: str = "models"

    # ── Email / SMTP ─────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "harshchoudhar6268y@gmail.com"          # e.g. "yourapp@gmail.com"
    SMTP_PASSWORD: str = "wngt yhze wwoy kgji"      # App Password (not your login password)
    SMTP_FROM_NAME: str = "ResumeXpert"
    SMTP_USE_TLS: bool = True

    # ── OTP Configuration ────────────────────────────────────
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60   # Minimum gap between resends
    OTP_MAX_RESENDS: int = 5                # Max resend requests per registration

    # ── Password Policy ──────────────────────────────────────
    PASSWORD_MIN_LENGTH: int = 8

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TRAINED_MODEL_DIR, exist_ok=True)
