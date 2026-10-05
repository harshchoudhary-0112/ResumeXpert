"""
ATS compatibility analyzer — checks structural and content issues
that commonly cause problems with Applicant Tracking Systems.
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def check_ats_compatibility(
    raw_text: str,
    parsed_data: Dict[str, Any],
    file_extension: str = ".pdf",
) -> tuple:
    """
    Run ATS compatibility checks on a parsed resume.
    
    Returns:
        - ats_score (0–100): overall ATS compatibility score
        - findings: list of {issue, severity, recommendation}
    """
    findings = []
    deductions = 0
    max_score = 100

    # ── 1. Contact Information ────────────────────────────────
    if not parsed_data.get("email"):
        findings.append({
            "issue": "Missing email address",
            "severity": "critical",
            "recommendation": "Add a professional email address at the top of your resume."
        })
        deductions += 10

    if not parsed_data.get("phone"):
        findings.append({
            "issue": "Missing phone number",
            "severity": "warning",
            "recommendation": "Add a phone number for recruiter contact."
        })
        deductions += 5

    if not parsed_data.get("name"):
        findings.append({
            "issue": "Name not clearly identifiable",
            "severity": "critical",
            "recommendation": "Place your full name prominently at the top of your resume."
        })
        deductions += 8

    # ── 2. Standard Sections ──────────────────────────────────
    sections = parsed_data.get("raw_sections", {})
    required_sections = ["experience", "education", "skills"]
    
    for section in required_sections:
        if section not in sections or not sections[section].strip():
            findings.append({
                "issue": f"Missing '{section.title()}' section",
                "severity": "critical",
                "recommendation": f"Add a clearly labeled '{section.title()}' section. ATS systems look for standard section headers."
            })
            deductions += 10

    # ── 3. Skills Section ─────────────────────────────────────
    skills = parsed_data.get("skills", [])
    if len(skills) < 3:
        findings.append({
            "issue": "Very few skills detected",
            "severity": "warning",
            "recommendation": "List at least 8-10 relevant technical skills. Use standard skill names that match job descriptions."
        })
        deductions += 7

    # ── 4. Text Length ────────────────────────────────────────
    word_count = len(raw_text.split())
    if word_count < 100:
        findings.append({
            "issue": "Resume appears too short",
            "severity": "critical",
            "recommendation": "Your resume has very little text. This might indicate image-only content that ATS cannot parse. Ensure all content is in selectable text."
        })
        deductions += 15
    elif word_count < 200:
        findings.append({
            "issue": "Resume text is brief",
            "severity": "warning",
            "recommendation": "Consider adding more detail to your experience and skills sections."
        })
        deductions += 5

    # ── 5. Special Characters & Formatting ────────────────────
    unusual_chars = re.findall(r"[^\x20-\x7E\n\r\t]", raw_text)
    if len(unusual_chars) > 20:
        findings.append({
            "issue": f"Contains {len(unusual_chars)} unusual/special characters",
            "severity": "warning",
            "recommendation": "Avoid decorative symbols, icons, or special characters. Use standard bullets (•, -, *) instead."
        })
        deductions += 5

    # ── 6. Table Detection ────────────────────────────────────
    table_indicators = ["|", "├", "┤", "┬", "┴", "┼", "─", "│"]
    table_count = sum(1 for char in raw_text if char in table_indicators)
    if table_count > 10:
        findings.append({
            "issue": "Complex table formatting detected",
            "severity": "warning",
            "recommendation": "Many ATS systems struggle with tables. Use simple layouts with clear section headers instead."
        })
        deductions += 8

    # ── 7. Column Detection ───────────────────────────────────
    lines = raw_text.split("\n")
    multi_column_lines = 0
    for line in lines:
        # Lines with large gaps might indicate multi-column layout
        if re.search(r"\S\s{8,}\S", line):
            multi_column_lines += 1
    
    if multi_column_lines > 5:
        findings.append({
            "issue": "Possible multi-column layout detected",
            "severity": "warning",
            "recommendation": "Multi-column layouts can confuse ATS parsers. Use a single-column layout for better compatibility."
        })
        deductions += 7

    # ── 8. Header/Footer Content ──────────────────────────────
    # Check if important content might be only in early/late lines
    if len(lines) > 10:
        first_5_skills = 0
        last_5_skills = 0
        from app.utils.skills_taxonomy import find_matching_skills
        
        first_text = "\n".join(lines[:5])
        last_text = "\n".join(lines[-5:])
        
        first_5_skills = len(find_matching_skills(first_text))
        last_5_skills = len(find_matching_skills(last_text))

        if last_5_skills > first_5_skills and last_5_skills > 5:
            findings.append({
                "issue": "Key skills concentrated in footer area",
                "severity": "info",
                "recommendation": "Some ATS systems may not parse footer content well. Consider moving important skills higher in the document."
            })
            deductions += 3

    # ── 9. Keyword Stuffing ───────────────────────────────────
    if skills:
        # Check for repeated skill mentions (possible stuffing)
        text_lower = raw_text.lower()
        for skill in skills[:10]:
            count = text_lower.count(skill.lower())
            if count > 10:
                findings.append({
                    "issue": f"Skill '{skill}' appears {count} times — possible keyword stuffing",
                    "severity": "warning",
                    "recommendation": "Mention skills naturally in context rather than repeating them excessively. ATS may flag keyword stuffing."
                })
                deductions += 5
                break  # Only flag once

    # ── 10. File Format ───────────────────────────────────────
    if file_extension.lower() == ".pdf":
        findings.append({
            "issue": "PDF format detected",
            "severity": "info",
            "recommendation": "PDF is generally ATS-friendly. Ensure the PDF has selectable text (not scanned images)."
        })
    elif file_extension.lower() == ".docx":
        findings.append({
            "issue": "DOCX format detected",
            "severity": "info",
            "recommendation": "DOCX is the most ATS-compatible format. Good choice."
        })

    # ── 11. Date Formatting ───────────────────────────────────
    date_patterns = re.findall(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}\b",
        raw_text,
        re.IGNORECASE,
    )
    numeric_dates = re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", raw_text)
    
    if not date_patterns and not numeric_dates:
        experience = parsed_data.get("experience", [])
        if experience:
            findings.append({
                "issue": "No clear date formatting found in experience section",
                "severity": "warning",
                "recommendation": "Use consistent date formatting (e.g., 'Jan 2020 - Present') for work experience."
            })
            deductions += 3

    # ── 12. Action Verbs ──────────────────────────────────────
    action_verbs = [
        "developed", "managed", "led", "designed", "implemented",
        "created", "built", "improved", "reduced", "increased",
        "achieved", "delivered", "established", "optimized", "launched",
        "analyzed", "coordinated", "executed", "generated", "maintained",
    ]
    text_lower = raw_text.lower()
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    if verb_count < 3:
        findings.append({
            "issue": "Few action verbs detected in resume",
            "severity": "info",
            "recommendation": "Start bullet points with strong action verbs (e.g., 'Developed', 'Led', 'Optimized') to improve ATS scoring and readability."
        })
        deductions += 2

    # ── Calculate Final Score ─────────────────────────────────
    ats_score = max(0, min(100, max_score - deductions))

    # Add a positive finding if score is high
    if ats_score >= 80:
        findings.insert(0, {
            "issue": "Good ATS compatibility",
            "severity": "info",
            "recommendation": "Your resume structure appears to be ATS-friendly overall."
        })

    return round(ats_score, 2), findings
