"""
Analysis API routes — run resume-JD analysis, retrieve results,
get suggestions, view history, and dashboard stats.
"""

import logging
from typing import List
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.analysis import Analysis, Suggestion
from app.schemas.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisHistoryItem,
    SuggestionResponse, DashboardStats, ScoreBreakdown,
    MatchedSkill, ATSFinding, SHAPExplanation,
)
from app.utils.auth import get_current_user
from app.services.nlp import compute_semantic_similarity, compute_keyword_density
from app.services.matcher import (
    compute_skill_match, compute_experience_match,
    compute_education_match, compute_project_relevance,
    compute_composite_score, classify_match,
)
from app.services.ats import check_ats_compatibility
from app.services.classifier import engineer_features, predict, explain_prediction
from app.services.suggestions import generate_suggestions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def run_analysis(
    payload: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Run a full resume-JD analysis pipeline:
    1. Retrieve resume and JD from DB
    2. Compute skill match (keyword overlap)
    3. Compute semantic similarity (SBERT)
    4. Compute experience, education, project scores
    5. Run ATS compatibility checks
    6. Compute composite score
    7. ML classification + SHAP explanation
    8. Generate improvement suggestions
    9. Store everything in DB
    """
    # ── 1. Retrieve resume and JD ─────────────────────────────
    resume = (
        db.query(Resume)
        .filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    jd = (
        db.query(JobDescription)
        .filter(JobDescription.id == payload.job_id, JobDescription.user_id == current_user.id)
        .first()
    )
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    parsed = resume.parsed_data or {}
    resume_text = resume.raw_text or ""

    # ── 2. Skill match ────────────────────────────────────────
    resume_skills = parsed.get("skills", [])
    jd_required = jd.required_skills or []
    jd_preferred = jd.preferred_skills or []

    skill_score, matched_skills_data, missing_skills = compute_skill_match(
        resume_skills, jd_required, jd_preferred
    )

    # ── 3. Semantic similarity ────────────────────────────────
    semantic_raw = compute_semantic_similarity(resume_text, jd.description)
    semantic_score = round(semantic_raw * 100, 2)

    # ── 4. Experience match ───────────────────────────────────
    experience_score = compute_experience_match(
        parsed.get("experience", []),
        resume_text,
        jd.experience_requirements or "",
    )

    # ── 5. Education match ────────────────────────────────────
    education_score = compute_education_match(
        parsed.get("education", []),
        jd.education_requirements or "",
    )

    # ── 6. Project relevance ──────────────────────────────────
    project_score = compute_project_relevance(
        parsed.get("projects", []),
        jd.description,
    )

    # ── 7. ATS compatibility ─────────────────────────────────
    file_ext = "." + resume.filename.rsplit(".", 1)[-1] if "." in resume.filename else ".pdf"
    ats_score, ats_findings_data = check_ats_compatibility(resume_text, parsed, file_ext)

    # ── 8. Composite score ────────────────────────────────────
    match_score, score_breakdown_data = compute_composite_score(
        skill_score, semantic_score, experience_score,
        education_score, ats_score, project_score,
    )

    # ── 9. ML Classification ─────────────────────────────────
    keyword_density = compute_keyword_density(resume_text, jd_required)
    features = engineer_features(
        skill_score, semantic_score, experience_score,
        education_score, project_score, ats_score,
        len(missing_skills), keyword_density,
    )

    classification, confidence = predict(features)
    shap_data = explain_prediction(features)

    # ── 10. Suggestions ───────────────────────────────────────
    jd_data = {
        "required_skills": jd_required,
        "preferred_skills": jd_preferred,
        "experience_requirements": jd.experience_requirements,
        "education_requirements": jd.education_requirements,
    }
    scores_dict = {
        "skill_score": skill_score,
        "semantic_score": semantic_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "project_score": project_score,
        "ats_score": ats_score,
    }
    suggestions_data = generate_suggestions(
        parsed, jd_data, matched_skills_data,
        missing_skills, ats_findings_data, scores_dict, jd.description,
    )

    # ── 11. Store in DB ───────────────────────────────────────
    analysis = Analysis(
        resume_id=resume.id,
        job_id=jd.id,
        match_score=match_score,
        skill_score=skill_score,
        semantic_score=semantic_score,
        experience_score=experience_score,
        education_score=education_score,
        ats_score=ats_score,
        project_score=project_score,
        classification=classification,
        classification_confidence=confidence,
        matched_skills=matched_skills_data,
        missing_skills=missing_skills,
        ats_findings=ats_findings_data,
        shap_explanation=shap_data,
        feature_values=features.tolist(),
    )
    db.add(analysis)
    db.flush()  # Get the analysis ID

    # Store suggestions
    for s in suggestions_data:
        suggestion = Suggestion(
            analysis_id=analysis.id,
            category=s["category"],
            suggestion=s["suggestion"],
            severity=s["severity"],
            evidence=s.get("evidence"),
        )
        db.add(suggestion)

    db.commit()
    db.refresh(analysis)

    # ── 12. Build response ────────────────────────────────────
    return _build_analysis_response(analysis, resume, jd, score_breakdown_data)


@router.get("/history", response_model=List[AnalysisHistoryItem])
def get_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analysis history for the current user."""
    analyses = (
        db.query(Analysis)
        .join(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(50)
        .all()
    )

    result = []
    for a in analyses:
        result.append(AnalysisHistoryItem(
            id=a.id,
            match_score=a.match_score or 0,
            classification=a.classification or "Unknown",
            resume_filename=a.resume.filename if a.resume else None,
            job_title=a.job_description.title if a.job_description else None,
            created_at=a.created_at,
        ))

    return result


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get aggregated dashboard statistics for the current user."""
    # Count totals
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    total_jobs = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).count()

    # Get all user analyses
    analyses = (
        db.query(Analysis)
        .join(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    total_analyses = len(analyses)
    scores = [a.match_score for a in analyses if a.match_score is not None]
    average_score = sum(scores) / len(scores) if scores else 0
    highest_score = max(scores) if scores else 0

    # Score distribution
    distribution = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    for s in scores:
        if s < 20:
            distribution["0-20"] += 1
        elif s < 40:
            distribution["20-40"] += 1
        elif s < 60:
            distribution["40-60"] += 1
        elif s < 80:
            distribution["60-80"] += 1
        else:
            distribution["80-100"] += 1

    # Top missing skills across all analyses
    all_missing = []
    for a in analyses:
        if a.missing_skills:
            all_missing.extend(a.missing_skills)
    missing_counter = Counter(all_missing)
    top_missing = [
        {"skill": skill, "count": count}
        for skill, count in missing_counter.most_common(10)
    ]

    # Recent analyses
    recent = []
    for a in analyses[:5]:
        recent.append(AnalysisHistoryItem(
            id=a.id,
            match_score=a.match_score or 0,
            classification=a.classification or "Unknown",
            resume_filename=a.resume.filename if a.resume else None,
            job_title=a.job_description.title if a.job_description else None,
            created_at=a.created_at,
        ))

    return DashboardStats(
        total_analyses=total_analyses,
        total_resumes=total_resumes,
        total_jobs=total_jobs,
        average_score=round(average_score, 2),
        highest_score=round(highest_score, 2),
        recent_analyses=recent,
        score_distribution=distribution,
        top_missing_skills=top_missing,
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific analysis result by ID."""
    analysis = (
        db.query(Analysis)
        .join(Resume)
        .filter(Analysis.id == analysis_id, Resume.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    resume = analysis.resume
    jd = analysis.job_description

    # Reconstruct score breakdown
    from app.config import settings
    breakdown_data = [
        {"component": "Skill Match", "score": analysis.skill_score or 0,
         "weight": settings.SKILL_MATCH_WEIGHT,
         "weighted_score": round((analysis.skill_score or 0) * settings.SKILL_MATCH_WEIGHT, 2)},
        {"component": "Semantic Similarity", "score": analysis.semantic_score or 0,
         "weight": settings.SEMANTIC_SIMILARITY_WEIGHT,
         "weighted_score": round((analysis.semantic_score or 0) * settings.SEMANTIC_SIMILARITY_WEIGHT, 2)},
        {"component": "Experience Match", "score": analysis.experience_score or 0,
         "weight": settings.EXPERIENCE_MATCH_WEIGHT,
         "weighted_score": round((analysis.experience_score or 0) * settings.EXPERIENCE_MATCH_WEIGHT, 2)},
        {"component": "Education Match", "score": analysis.education_score or 0,
         "weight": settings.EDUCATION_MATCH_WEIGHT,
         "weighted_score": round((analysis.education_score or 0) * settings.EDUCATION_MATCH_WEIGHT, 2)},
        {"component": "ATS Compatibility", "score": analysis.ats_score or 0,
         "weight": settings.ATS_COMPATIBILITY_WEIGHT,
         "weighted_score": round((analysis.ats_score or 0) * settings.ATS_COMPATIBILITY_WEIGHT, 2)},
        {"component": "Project Relevance", "score": analysis.project_score or 0,
         "weight": settings.PROJECT_RELEVANCE_WEIGHT,
         "weighted_score": round((analysis.project_score or 0) * settings.PROJECT_RELEVANCE_WEIGHT, 2)},
    ]

    return _build_analysis_response(analysis, resume, jd, breakdown_data)


@router.get("/{analysis_id}/suggestions", response_model=List[SuggestionResponse])
def get_analysis_suggestions(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get improvement suggestions for a specific analysis."""
    analysis = (
        db.query(Analysis)
        .join(Resume)
        .filter(Analysis.id == analysis_id, Resume.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    suggestions = (
        db.query(Suggestion)
        .filter(Suggestion.analysis_id == analysis_id)
        .all()
    )

    return [
        SuggestionResponse(
            id=s.id,
            category=s.category,
            suggestion=s.suggestion,
            severity=s.severity,
            evidence=s.evidence,
        )
        for s in suggestions
    ]


def _build_analysis_response(
    analysis: Analysis,
    resume: Resume,
    jd: JobDescription,
    score_breakdown_data: list,
) -> AnalysisResponse:
    """Helper to build a full AnalysisResponse from DB objects."""
    # Convert matched skills
    matched_skills_list = []
    if analysis.matched_skills:
        for ms in analysis.matched_skills:
            matched_skills_list.append(MatchedSkill(
                skill=ms.get("skill", ""),
                category=ms.get("category", "other"),
                found_in_resume=True,
                found_in_jd=True,
            ))

    # Convert ATS findings
    ats_findings_list = []
    if analysis.ats_findings:
        for af in analysis.ats_findings:
            ats_findings_list.append(ATSFinding(
                issue=af.get("issue", ""),
                severity=af.get("severity", "info"),
                recommendation=af.get("recommendation", ""),
            ))

    # Convert SHAP explanations
    shap_list = []
    if analysis.shap_explanation:
        for se in analysis.shap_explanation:
            shap_list.append(SHAPExplanation(
                feature=se.get("feature", ""),
                value=se.get("value", 0),
                contribution=se.get("contribution", 0),
            ))

    # Convert score breakdown
    breakdown_list = [ScoreBreakdown(**sb) for sb in score_breakdown_data]

    # Get suggestions
    suggestions_list = []
    if analysis.suggestions:
        for s in analysis.suggestions:
            suggestions_list.append(SuggestionResponse(
                id=s.id,
                category=s.category,
                suggestion=s.suggestion,
                severity=s.severity,
                evidence=s.evidence,
            ))

    return AnalysisResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_id=analysis.job_id,
        match_score=analysis.match_score or 0,
        score_breakdown=breakdown_list,
        classification=analysis.classification or "Unknown",
        classification_confidence=analysis.classification_confidence,
        matched_skills=matched_skills_list,
        missing_skills=analysis.missing_skills or [],
        ats_score=analysis.ats_score or 0,
        ats_findings=ats_findings_list,
        shap_explanation=shap_list,
        suggestions=suggestions_list,
        resume_name=resume.parsed_data.get("name") if resume.parsed_data else None,
        job_title=jd.title,
        created_at=analysis.created_at,
    )
