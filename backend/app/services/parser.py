"""
Resume parsing service — extract text from PDF/DOCX files,
detect sections, and extract structured information.
"""

import os
import re
import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

# ── Section header patterns ──────────────────────────────────
SECTION_PATTERNS = {
    "summary": r"(?i)\b(summary|objective|profile|about\s*me|professional\s*summary|career\s*objective)\b",
    "experience": r"(?i)\b(experience|work\s*experience|employment|professional\s*experience|work\s*history)\b",
    "education": r"(?i)\b(education|academic|qualification|degree|university|college)\b",
    "skills": r"(?i)\b(skills|technical\s*skills|core\s*competencies|technologies|proficiencies|expertise)\b",
    "projects": r"(?i)\b(projects|personal\s*projects|academic\s*projects|key\s*projects)\b",
    "certifications": r"(?i)\b(certifications?|certificates?|licenses?|accreditations?)\b",
    "achievements": r"(?i)\b(achievements?|awards?|honors?|accomplishments?)\b",
    "languages": r"(?i)\b(languages?|linguistic)\b",
    "interests": r"(?i)\b(interests?|hobbies?|activities)\b",
    "references": r"(?i)\b(references?)\b",
    "publications": r"(?i)\b(publications?|papers?|research)\b",
}

# ── Contact info patterns ────────────────────────────────────
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
)
LINKEDIN_PATTERN = re.compile(r"linkedin\.com/in/[\w-]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"github\.com/[\w-]+", re.IGNORECASE)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Failed to extract text from PDF: {e}")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document

        doc = Document(file_path)
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise ValueError(f"Failed to extract text from DOCX: {e}")


def extract_text_from_file(file_path: str) -> str:
    """Route to the appropriate extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def clean_text(text: str) -> str:
    """Normalize and clean extracted resume text."""
    # Remove excessive whitespace
    text = re.sub(r"\t", " ", text)
    text = re.sub(r" {2,}", " ", text)
    # Remove excessive newlines (keep max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove non-printable characters (keep standard whitespace)
    text = re.sub(r"[^\x20-\x7E\n\r\t]", " ", text)
    return text.strip()


def detect_sections(text: str) -> Dict[str, str]:
    """
    Detect resume sections by scanning for header patterns.
    Returns a dict mapping section_name -> section_content.
    """
    lines = text.split("\n")
    sections: Dict[str, str] = {}
    current_section = "header"  # Content before the first recognized section
    current_lines: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append("")
            continue

        # Check if this line is a section header
        matched_section = None
        for section_name, pattern in SECTION_PATTERNS.items():
            # A section header is typically a short line (< 60 chars) matching the pattern
            if len(stripped) < 60 and re.search(pattern, stripped):
                matched_section = section_name
                break

        if matched_section:
            # Save the previous section
            content = "\n".join(current_lines).strip()
            if content:
                sections[current_section] = content
            current_section = matched_section
            current_lines = []
        else:
            current_lines.append(stripped)

    # Save the last section
    content = "\n".join(current_lines).strip()
    if content:
        sections[current_section] = content

    return sections


def extract_name(text: str, sections: Dict[str, str]) -> Optional[str]:
    """
    Extract candidate name from the header section.
    Heuristic: first non-empty line that doesn't look like an email/phone/URL.
    """
    header = sections.get("header", text[:500])
    for line in header.split("\n"):
        line = line.strip()
        if not line or len(line) < 2:
            continue
        # Skip lines that are clearly contact info
        if EMAIL_PATTERN.search(line):
            continue
        if PHONE_PATTERN.search(line) and len(line) < 20:
            continue
        if "linkedin" in line.lower() or "github" in line.lower():
            continue
        if re.match(r"^[\d\s\-\+\(\)]+$", line):  # Phone-only line
            continue
        # Likely a name if it's short and mostly alphabetic
        if len(line) < 60 and re.match(r"^[A-Za-z\s\.\-\']+$", line):
            return line.title()

    return None


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract email, phone, LinkedIn, and GitHub from text."""
    email_match = EMAIL_PATTERN.search(text)
    phone_match = PHONE_PATTERN.search(text)
    linkedin_match = LINKEDIN_PATTERN.search(text)
    github_match = GITHUB_PATTERN.search(text)

    return {
        "email": email_match.group() if email_match else None,
        "phone": phone_match.group() if phone_match else None,
        "linkedin": linkedin_match.group() if linkedin_match else None,
        "github": github_match.group() if github_match else None,
    }


def extract_education(sections: Dict[str, str]) -> List[str]:
    """Extract education entries from the education section."""
    edu_text = sections.get("education", "")
    if not edu_text:
        return []

    entries = []
    # Split by double newlines or bullet points
    blocks = re.split(r"\n\n|\n(?=[-•●▪])", edu_text)
    for block in blocks:
        block = block.strip().lstrip("-•●▪ ")
        if block and len(block) > 5:
            # Collapse to single line
            entry = re.sub(r"\s+", " ", block).strip()
            entries.append(entry)

    return entries if entries else [edu_text.strip()]


def extract_experience(sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """Extract experience entries from the experience section."""
    exp_text = sections.get("experience", "")
    if not exp_text:
        return []

    entries = []
    # Split by double newlines (each block = one role)
    blocks = re.split(r"\n\n+", exp_text)
    for block in blocks:
        block = block.strip()
        if not block or len(block) < 10:
            continue
        lines = block.split("\n")
        entry = {
            "title": lines[0].strip() if lines else "",
            "details": "\n".join(lines[1:]).strip() if len(lines) > 1 else "",
        }
        entries.append(entry)

    return entries


def extract_projects(sections: Dict[str, str]) -> List[str]:
    """Extract project names/descriptions from the projects section."""
    proj_text = sections.get("projects", "")
    if not proj_text:
        return []

    projects = []
    blocks = re.split(r"\n\n|\n(?=[-•●▪])", proj_text)
    for block in blocks:
        block = block.strip().lstrip("-•●▪ ")
        if block and len(block) > 5:
            entry = re.sub(r"\s+", " ", block).strip()
            projects.append(entry)

    return projects if projects else [proj_text.strip()]


def extract_certifications(sections: Dict[str, str]) -> List[str]:
    """Extract certifications from the certifications section."""
    cert_text = sections.get("certifications", "")
    if not cert_text:
        return []

    certs = []
    for line in cert_text.split("\n"):
        line = line.strip().lstrip("-•●▪ ")
        if line and len(line) > 3:
            certs.append(line)

    return certs


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Full resume parsing pipeline:
    1. Extract text from PDF/DOCX
    2. Clean and normalize
    3. Detect sections
    4. Extract structured fields
    
    Returns a dict suitable for storing as parsed_data JSON.
    """
    # Step 1: Extract raw text
    raw_text = extract_text_from_file(file_path)

    # Step 2: Clean
    cleaned_text = clean_text(raw_text)

    # Step 3: Detect sections
    sections = detect_sections(cleaned_text)

    # Step 4: Extract structured info
    contact = extract_contact_info(cleaned_text)
    name = extract_name(cleaned_text, sections)

    # Step 5: Extract skills using taxonomy
    from app.utils.skills_taxonomy import find_matching_skills
    skill_matches = find_matching_skills(cleaned_text)
    skills = list(set(s[0] for s in skill_matches))
    skills_with_categories = [
        {"skill": s[0], "category": s[1]} for s in skill_matches
    ]

    parsed = {
        "name": name,
        "email": contact.get("email"),
        "phone": contact.get("phone"),
        "linkedin": contact.get("linkedin"),
        "github": contact.get("github"),
        "skills": sorted(skills),
        "skills_with_categories": skills_with_categories,
        "education": extract_education(sections),
        "experience": extract_experience(sections),
        "projects": extract_projects(sections),
        "certifications": extract_certifications(sections),
        "summary": sections.get("summary", ""),
        "raw_sections": sections,
    }

    return raw_text, cleaned_text, parsed
