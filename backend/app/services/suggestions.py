"""
Suggestion engine — generates evidence-based resume improvement
recommendations from analysis results. Never invents skills,
experience, achievements, or certifications.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def generate_suggestions(
    parsed_resume: Dict[str, Any],
    jd_data: Dict[str, Any],
    matched_skills: List[Dict],
    missing_skills: List[str],
    ats_findings: List[Dict],
    scores: Dict[str, float],
    jd_text: str = "",
) -> List[Dict[str, Any]]:
    """
    Generate evidence-based improvement suggestions.
    
    All suggestions are grounded in actual resume content and detected gaps.
    Nothing is fabricated — only gaps and improvements are highlighted.
    
    Returns a list of {category, suggestion, severity, evidence}.
    """
    suggestions = []

    # ── 1. Missing Skills Suggestions ─────────────────────────
    if missing_skills:
        # Prioritize: more than 5 missing = high severity
        severity = "high" if len(missing_skills) > 5 else "medium" if len(missing_skills) > 2 else "low"

        # Group missing skills by category
        from app.utils.skills_taxonomy import get_skill_category
        categorized_missing = {}
        for skill in missing_skills:
            cat = get_skill_category(skill)
            if cat not in categorized_missing:
                categorized_missing[cat] = []
            categorized_missing[cat].append(skill)

        for category, skills in categorized_missing.items():
            skill_list = ", ".join(skills[:8])
            cat_label = category.replace("_", " ").title()

            suggestions.append({
                "category": "skills",
                "suggestion": f"Add these {cat_label} skills to your resume if you have experience with them: {skill_list}",
                "severity": severity,
                "evidence": f"These skills are required in the job description but not found in your resume.",
            })

    # ── 2. Skill Match Score Suggestions ──────────────────────
    skill_score = scores.get("skill_score", 0)
    if skill_score < 40:
        suggestions.append({
            "category": "skills",
            "suggestion": "Your skill match is low. Review the job description carefully and ensure all relevant skills are explicitly listed in your Skills section.",
            "severity": "high",
            "evidence": f"Skill match score: {skill_score:.0f}%. Many required skills were not found in your resume.",
        })
    elif skill_score < 60:
        suggestions.append({
            "category": "skills",
            "suggestion": "Consider adding a dedicated 'Technical Skills' section that clearly lists your competencies matching the job requirements.",
            "severity": "medium",
            "evidence": f"Skill match score: {skill_score:.0f}%. Some required skills may be present but not clearly visible.",
        })

    # ── 3. Experience Suggestions ─────────────────────────────
    experience_score = scores.get("experience_score", 0)
    experience = parsed_resume.get("experience", [])

    if experience_score < 50:
        if not experience:
            suggestions.append({
                "category": "experience",
                "suggestion": "Add a Work Experience section with your relevant roles, responsibilities, and achievements.",
                "severity": "high",
                "evidence": "No experience section was detected in your resume.",
            })
        else:
            suggestions.append({
                "category": "experience",
                "suggestion": "Strengthen your experience descriptions with quantifiable achievements and relevant keywords from the job description.",
                "severity": "medium",
                "evidence": f"Experience match score: {experience_score:.0f}%. Your experience may not align closely with the role requirements.",
            })

    # Check for weak bullet points (too short or lacking metrics)
    for exp_entry in experience:
        details = exp_entry.get("details", "")
        if details and len(details) < 50:
            suggestions.append({
                "category": "content",
                "suggestion": f"Expand the description for '{exp_entry.get('title', 'a role')}'. Use the STAR method (Situation, Task, Action, Result) to describe your achievements.",
                "severity": "low",
                "evidence": "Short experience descriptions may not demonstrate your impact effectively.",
            })
            break  # Only flag once

    # Check for metrics in experience
    import re
    all_exp_text = " ".join(
        exp.get("details", "") for exp in experience
    )
    has_metrics = bool(re.search(r"\d+%|\$\d+|\d+\s*(?:users|clients|projects|team|members)", all_exp_text, re.IGNORECASE))
    if experience and not has_metrics:
        suggestions.append({
            "category": "content",
            "suggestion": "Add quantifiable metrics to your experience (e.g., 'Improved performance by 30%', 'Managed team of 5', 'Reduced costs by $10K').",
            "severity": "medium",
            "evidence": "No quantifiable achievements detected in your experience descriptions.",
        })

    # ── 4. Education Suggestions ──────────────────────────────
    education_score = scores.get("education_score", 0)
    education = parsed_resume.get("education", [])

    if not education:
        suggestions.append({
            "category": "content",
            "suggestion": "Add an Education section with your degree(s), institution(s), and graduation year(s).",
            "severity": "high",
            "evidence": "No education section was detected in your resume.",
        })
    elif education_score < 50:
        jd_edu_req = jd_data.get("education_requirements", "")
        if jd_edu_req:
            suggestions.append({
                "category": "content",
                "suggestion": f"The job requires: {jd_edu_req}. Ensure your education section highlights any relevant degrees or coursework.",
                "severity": "medium",
                "evidence": f"Education match score: {education_score:.0f}%.",
            })

    # ── 5. Project Suggestions ────────────────────────────────
    project_score = scores.get("project_score", 0)
    projects = parsed_resume.get("projects", [])

    if project_score < 40 and missing_skills:
        suggestions.append({
            "category": "content",
            "suggestion": "Consider adding projects that demonstrate your experience with the missing required skills. Describe what you built, technologies used, and outcomes.",
            "severity": "medium",
            "evidence": f"Project relevance score: {project_score:.0f}%. Adding relevant projects can strengthen your application.",
        })

    if not projects:
        suggestions.append({
            "category": "content",
            "suggestion": "Adding a Projects section can showcase practical experience, especially if work experience is limited.",
            "severity": "low",
            "evidence": "No projects section was detected in your resume.",
        })

    # ── 6. ATS Suggestions ────────────────────────────────────
    ats_score = scores.get("ats_score", 0)
    if ats_score < 60:
        # Pull the most critical ATS findings
        critical_findings = [f for f in ats_findings if f.get("severity") == "critical"]
        for finding in critical_findings[:3]:
            suggestions.append({
                "category": "ats",
                "suggestion": finding["recommendation"],
                "severity": "high",
                "evidence": finding["issue"],
            })

    warning_findings = [f for f in ats_findings if f.get("severity") == "warning"]
    for finding in warning_findings[:2]:
        suggestions.append({
            "category": "ats",
            "suggestion": finding["recommendation"],
            "severity": "medium",
            "evidence": finding["issue"],
        })

    # ── 7. Semantic Similarity Suggestions ────────────────────
    semantic_score = scores.get("semantic_score", 0)
    if semantic_score < 40:
        suggestions.append({
            "category": "content",
            "suggestion": "Your resume's overall language doesn't closely match the job description. Try incorporating key phrases and terminology from the JD into your experience descriptions.",
            "severity": "medium",
            "evidence": f"Semantic similarity score: {semantic_score:.0f}%. The language in your resume diverges significantly from the JD.",
        })

    # ── 8. Summary/Objective Suggestions ──────────────────────
    summary = parsed_resume.get("summary", "")
    if not summary:
        suggestions.append({
            "category": "formatting",
            "suggestion": "Consider adding a Professional Summary at the top of your resume (2-3 sentences) highlighting your most relevant qualifications for this role.",
            "severity": "low",
            "evidence": "No summary or objective section was detected.",
        })

    # ── 9. Certifications Suggestions ─────────────────────────
    certifications = parsed_resume.get("certifications", [])
    if not certifications and missing_skills:
        suggestions.append({
            "category": "content",
            "suggestion": "If you have any relevant certifications (e.g., AWS, Azure, Google Cloud, PMP), add a Certifications section to strengthen your application.",
            "severity": "low",
            "evidence": "No certifications section was detected. Relevant certifications can help bridge skill gaps.",
        })

    # ── Sort by severity ──────────────────────────────────────
    severity_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: severity_order.get(x["severity"], 3))

    # Limit to top 15 most impactful suggestions
    return suggestions[:15]
