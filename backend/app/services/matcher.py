"""
Resume–JD matching service — combines keyword overlap with
semantic similarity and structured field matching to produce
a composite match score.
"""

import re
import logging
from typing import Dict, List, Any, Tuple

from app.config import settings
from app.utils.skills_taxonomy import find_matching_skills, get_skill_category

logger = logging.getLogger(__name__)


def compute_skill_match(
    resume_skills: List[str],
    jd_required_skills: List[str],
    jd_preferred_skills: List[str] = None,
) -> Tuple[float, List[Dict], List[str]]:
    """
    Compute keyword-based skill overlap between resume and JD.
    
    Returns:
        - score (0–100)
        - matched_skills: list of {skill, category, required}
        - missing_skills: list of required skills not found in resume
    """
    if not jd_required_skills:
        return 0.0, [], []

    resume_skills_lower = set(s.lower().strip() for s in resume_skills)
    jd_preferred_skills = jd_preferred_skills or []

    matched = []
    missing = []

    # Check required skills
    required_found = 0
    for skill in jd_required_skills:
        skill_lower = skill.lower().strip()
        if skill_lower in resume_skills_lower:
            matched.append({
                "skill": skill,
                "category": get_skill_category(skill),
                "required": True,
            })
            required_found += 1
        else:
            missing.append(skill)

    # Check preferred skills
    preferred_found = 0
    for skill in jd_preferred_skills:
        skill_lower = skill.lower().strip()
        if skill_lower in resume_skills_lower:
            matched.append({
                "skill": skill,
                "category": get_skill_category(skill),
                "required": False,
            })
            preferred_found += 1

    # Score: 80% weight on required, 20% on preferred
    total_required = len(jd_required_skills)
    total_preferred = len(jd_preferred_skills)

    required_ratio = required_found / total_required if total_required > 0 else 0
    preferred_ratio = preferred_found / total_preferred if total_preferred > 0 else 0

    if total_preferred > 0:
        score = (required_ratio * 0.8 + preferred_ratio * 0.2) * 100
    else:
        score = required_ratio * 100

    return round(score, 2), matched, missing


def compute_experience_match(
    resume_experience: List[Dict],
    resume_text: str,
    jd_experience_req: str,
) -> float:
    """
    Estimate how well the candidate's experience matches the JD requirement.
    Returns a score from 0–100.
    """
    if not jd_experience_req:
        return 70.0  # Neutral score when JD doesn't specify

    # Extract required years from JD
    match = re.search(r"(\d+)", jd_experience_req)
    if not match:
        return 70.0
    required_years = int(match.group(1))

    # Estimate candidate's years from resume
    # Look for date ranges like "2019 - 2023" or "2019 - Present"
    year_pattern = re.compile(
        r"(20\d{2}|19\d{2})\s*[-–—to]+\s*(20\d{2}|19\d{2}|present|current)",
        re.IGNORECASE,
    )
    matches = year_pattern.findall(resume_text)

    if matches:
        total_years = 0
        for start_str, end_str in matches:
            start_year = int(start_str)
            if end_str.lower() in ("present", "current"):
                import datetime
                end_year = datetime.datetime.now().year
            else:
                end_year = int(end_str)
            total_years += max(0, end_year - start_year)

        if total_years >= required_years:
            return 100.0
        elif total_years >= required_years * 0.7:
            return 80.0
        elif total_years >= required_years * 0.5:
            return 60.0
        else:
            return max(20.0, (total_years / required_years) * 100)
    else:
        # Fallback: check number of experience entries
        num_entries = len(resume_experience)
        if num_entries >= 3:
            return 70.0
        elif num_entries >= 1:
            return 50.0
        else:
            return 20.0


def compute_education_match(
    resume_education: List[str],
    jd_education_req: str,
) -> float:
    """
    Check if the candidate's education meets JD requirements.
    Returns a score from 0–100.
    """
    if not jd_education_req:
        return 70.0  # Neutral when JD doesn't specify

    if not resume_education:
        return 20.0

    edu_text = " ".join(resume_education).lower()
    jd_edu_lower = jd_education_req.lower()

    # Education level hierarchy
    levels = {
        "phd": 5, "ph.d": 5, "doctorate": 5,
        "master": 4, "m.s": 4, "m.tech": 4, "m.e": 4, "mba": 4,
        "bachelor": 3, "b.s": 3, "b.tech": 3, "b.e": 3, "b.sc": 3,
        "associate": 2, "diploma": 2,
    }

    # Find candidate's highest education level
    candidate_level = 0
    for keyword, level in levels.items():
        if keyword in edu_text:
            candidate_level = max(candidate_level, level)

    # Find required education level
    required_level = 0
    for keyword, level in levels.items():
        if keyword in jd_edu_lower:
            required_level = max(required_level, level)

    if required_level == 0:
        return 70.0  # Can't determine requirement

    if candidate_level >= required_level:
        score = 100.0
    elif candidate_level == required_level - 1:
        score = 70.0
    else:
        score = max(20.0, (candidate_level / required_level) * 100)

    # Bonus for relevant field match
    field_keywords = [
        "computer science", "software", "information technology",
        "data science", "engineering", "mathematics", "statistics",
    ]
    for field in field_keywords:
        if field in jd_edu_lower and field in edu_text:
            score = min(100.0, score + 10)
            break

    return round(score, 2)


def compute_project_relevance(
    resume_projects: List[str],
    jd_text: str,
) -> float:
    """
    Estimate project relevance by checking keyword overlap between
    project descriptions and JD.
    Returns a score from 0–100.
    """
    if not resume_projects:
        return 30.0  # Low but not zero — projects are optional

    project_text = " ".join(resume_projects).lower()
    jd_lower = jd_text.lower()

    # Find JD skills in projects
    jd_skills = find_matching_skills(jd_text)
    jd_skill_names = set(s[0] for s in jd_skills)

    if not jd_skill_names:
        return 50.0

    project_skills = find_matching_skills(project_text)
    project_skill_names = set(s[0] for s in project_skills)

    overlap = jd_skill_names & project_skill_names
    if not jd_skill_names:
        return 50.0

    ratio = len(overlap) / len(jd_skill_names)
    return round(min(100.0, ratio * 120), 2)  # Slight bonus cap at 100


def compute_composite_score(
    skill_score: float,
    semantic_score: float,
    experience_score: float,
    education_score: float,
    ats_score: float,
    project_score: float,
) -> Tuple[float, List[Dict]]:
    """
    Compute the weighted composite match score.
    Returns the overall score and a breakdown list.
    """
    breakdown = [
        {
            "component": "Skill Match",
            "score": round(skill_score, 2),
            "weight": settings.SKILL_MATCH_WEIGHT,
            "weighted_score": round(skill_score * settings.SKILL_MATCH_WEIGHT, 2),
        },
        {
            "component": "Semantic Similarity",
            "score": round(semantic_score, 2),
            "weight": settings.SEMANTIC_SIMILARITY_WEIGHT,
            "weighted_score": round(semantic_score * settings.SEMANTIC_SIMILARITY_WEIGHT, 2),
        },
        {
            "component": "Experience Match",
            "score": round(experience_score, 2),
            "weight": settings.EXPERIENCE_MATCH_WEIGHT,
            "weighted_score": round(experience_score * settings.EXPERIENCE_MATCH_WEIGHT, 2),
        },
        {
            "component": "Education Match",
            "score": round(education_score, 2),
            "weight": settings.EDUCATION_MATCH_WEIGHT,
            "weighted_score": round(education_score * settings.EDUCATION_MATCH_WEIGHT, 2),
        },
        {
            "component": "ATS Compatibility",
            "score": round(ats_score, 2),
            "weight": settings.ATS_COMPATIBILITY_WEIGHT,
            "weighted_score": round(ats_score * settings.ATS_COMPATIBILITY_WEIGHT, 2),
        },
        {
            "component": "Project Relevance",
            "score": round(project_score, 2),
            "weight": settings.PROJECT_RELEVANCE_WEIGHT,
            "weighted_score": round(project_score * settings.PROJECT_RELEVANCE_WEIGHT, 2),
        },
    ]

    overall = sum(item["weighted_score"] for item in breakdown)
    return round(overall, 2), breakdown


def classify_match(score: float) -> Tuple[str, float]:
    """
    Classify the match into a human-readable label based on the composite score.
    Returns (classification, confidence).
    This is a rule-based fallback used when no ML model is available.
    """
    if score >= 75:
        return "Strong Match", min(0.95, score / 100)
    elif score >= 50:
        return "Moderate Match", 0.5 + (score - 50) / 100
    elif score >= 30:
        return "Weak Match", 0.3 + (score - 30) / 100
    else:
        return "Poor Match", max(0.1, score / 100)
