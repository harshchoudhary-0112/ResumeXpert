"""Analysis and Suggestion models — resume-JD match results and improvements."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)

    # ── Component Scores ──────────────────────────────────────
    match_score = Column(Float, nullable=True)          # Overall composite score (0–100)
    skill_score = Column(Float, nullable=True)           # Keyword skill match (0–100)
    semantic_score = Column(Float, nullable=True)        # SBERT cosine similarity (0–100)
    experience_score = Column(Float, nullable=True)      # Experience alignment (0–100)
    education_score = Column(Float, nullable=True)       # Education alignment (0–100)
    ats_score = Column(Float, nullable=True)             # ATS compatibility (0–100)
    project_score = Column(Float, nullable=True)         # Project relevance (0–100)

    # ── Classification ────────────────────────────────────────
    classification = Column(String(50), nullable=True)   # "Strong Match", "Moderate Match", "Weak Match"
    classification_confidence = Column(Float, nullable=True)

    # ── Detailed Results (JSON) ───────────────────────────────
    matched_skills = Column(JSON, nullable=True)         # List of matched skills
    missing_skills = Column(JSON, nullable=True)         # List of missing required skills
    ats_findings = Column(JSON, nullable=True)           # List of ATS issues found
    shap_explanation = Column(JSON, nullable=True)       # SHAP feature contributions
    feature_values = Column(JSON, nullable=True)         # Raw feature vector used for ML

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    job_description = relationship("JobDescription", back_populates="analyses")
    suggestions = relationship("Suggestion", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Analysis(id={self.id}, score={self.match_score})>"


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)   # "skills", "formatting", "content", "ats", "experience"
    suggestion = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)    # "high", "medium", "low"
    evidence = Column(Text, nullable=True)           # Supporting evidence from resume/JD

    # Relationship
    analysis = relationship("Analysis", back_populates="suggestions")

    def __repr__(self):
        return f"<Suggestion(id={self.id}, category='{self.category}', severity='{self.severity}')>"
