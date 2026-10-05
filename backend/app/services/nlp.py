"""
NLP service — spaCy and Sentence-Transformer based text analysis.
Handles JD parsing, semantic embeddings, and entity extraction.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Lazy-loaded NLP models (loaded once on first use) ────────
_spacy_nlp = None
_sbert_model = None


def get_spacy_model():
    """Lazy-load spaCy model."""
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            from app.config import settings
            try:
                _spacy_nlp = spacy.load(settings.SPACY_MODEL)
            except OSError:
                logger.warning(f"spaCy model '{settings.SPACY_MODEL}' not found. Downloading...")
                spacy.cli.download(settings.SPACY_MODEL)
                _spacy_nlp = spacy.load(settings.SPACY_MODEL)
            logger.info(f"spaCy model loaded: {settings.SPACY_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load spaCy: {e}")
            raise
    return _spacy_nlp


def get_sbert_model():
    """Lazy-load Sentence-Transformer model."""
    global _sbert_model
    if _sbert_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            from app.config import settings
            _sbert_model = SentenceTransformer(settings.SBERT_MODEL)
            logger.info(f"SBERT model loaded: {settings.SBERT_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load SBERT: {e}")
            raise
    return _sbert_model


# ── JD Section Patterns ──────────────────────────────────────
JD_REQUIRED_PATTERNS = [
    r"(?i)required\s*(?:skills?|qualifications?|experience)",
    r"(?i)must\s+have",
    r"(?i)requirements?\s*:",
    r"(?i)you\s+(?:must|should|need\s+to)\s+have",
    r"(?i)minimum\s+qualifications?",
]

JD_PREFERRED_PATTERNS = [
    r"(?i)preferred\s*(?:skills?|qualifications?)",
    r"(?i)nice\s+to\s+have",
    r"(?i)bonus\s*(?:skills?|qualifications?|points?)",
    r"(?i)desired\s*(?:skills?|qualifications?)",
    r"(?i)plus\s*(?:points?)?",
]

JD_EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)",
    r"(?:experience|exp)\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)",
]

JD_EDUCATION_PATTERNS = [
    r"(?i)(bachelor'?s?|master'?s?|phd|ph\.d|doctorate|associate'?s?|mba|b\.?s\.?|m\.?s\.?|b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?)",
    r"(?i)(computer\s*science|information\s*technology|software\s*engineering|electrical\s*engineering|data\s*science|mathematics|statistics)",
]


def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """
    Parse a job description to extract structured information:
    - Required skills
    - Preferred skills
    - Experience requirements
    - Education requirements
    - Job responsibilities
    """
    from app.utils.skills_taxonomy import find_matching_skills

    # Find all skills mentioned in the JD
    skill_matches = find_matching_skills(jd_text)
    all_skills = list(set(s[0] for s in skill_matches))

    # Try to separate required vs preferred
    lines = jd_text.split("\n")
    required_skills = []
    preferred_skills = []
    current_section = "general"

    for line in lines:
        stripped = line.strip()
        # Check if this line is a required section header
        for pattern in JD_REQUIRED_PATTERNS:
            if re.search(pattern, stripped):
                current_section = "required"
                break
        for pattern in JD_PREFERRED_PATTERNS:
            if re.search(pattern, stripped):
                current_section = "preferred"
                break

        # Extract skills from this line and assign to current section
        line_skills = find_matching_skills(stripped)
        for skill, category in line_skills:
            if current_section == "preferred":
                if skill not in preferred_skills:
                    preferred_skills.append(skill)
            else:
                if skill not in required_skills:
                    required_skills.append(skill)

    # If no clear separation, treat all as required
    if not required_skills and not preferred_skills:
        required_skills = all_skills

    # Extract experience requirements
    experience_req = None
    for pattern in JD_EXPERIENCE_PATTERNS:
        match = re.search(pattern, jd_text)
        if match:
            years = match.group(1) if match.group(1) else match.group(0)
            experience_req = f"{years}+ years"
            break

    # Extract education requirements
    education_matches = []
    for pattern in JD_EDUCATION_PATTERNS:
        matches = re.findall(pattern, jd_text)
        education_matches.extend(matches)
    education_req = ", ".join(set(education_matches)) if education_matches else None

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_requirements": experience_req,
        "education_requirements": education_req,
        "all_skills": all_skills,
    }


def compute_semantic_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two text passages using SBERT embeddings.
    Returns a value between 0 and 1.
    """
    try:
        model = get_sbert_model()
        embeddings = model.encode([text1, text2], convert_to_numpy=True)
        # Cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(max(0, min(1, similarity)))  # Clamp to [0, 1]
    except Exception as e:
        logger.error(f"Semantic similarity computation failed: {e}")
        return 0.0


def compute_section_similarities(
    resume_sections: Dict[str, str], jd_text: str
) -> Dict[str, float]:
    """
    Compute semantic similarity between each resume section and the JD.
    Returns a dict mapping section_name -> similarity_score.
    """
    results = {}
    for section_name, section_text in resume_sections.items():
        if section_text and len(section_text) > 20:
            sim = compute_semantic_similarity(section_text, jd_text)
            results[section_name] = sim
    return results


def extract_entities_spacy(text: str) -> Dict[str, List[str]]:
    """
    Use spaCy NER to extract named entities from text.
    Returns entities grouped by type.
    """
    try:
        nlp = get_spacy_model()
        doc = nlp(text[:100000])  # Limit text length for performance
        entities: Dict[str, List[str]] = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            if ent.text not in entities[label]:
                entities[label].append(ent.text)
        return entities
    except Exception as e:
        logger.error(f"spaCy NER failed: {e}")
        return {}


def extract_key_phrases(text: str, top_n: int = 20) -> List[str]:
    """
    Extract key noun phrases from text using spaCy.
    Useful for identifying important concepts in resume/JD.
    """
    try:
        nlp = get_spacy_model()
        doc = nlp(text[:50000])
        phrases = []
        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip().lower()
            if len(phrase) > 2 and phrase not in phrases:
                phrases.append(phrase)
        return phrases[:top_n]
    except Exception as e:
        logger.error(f"Key phrase extraction failed: {e}")
        return []


def compute_keyword_density(text: str, keywords: List[str]) -> float:
    """
    Compute what fraction of the given keywords appear in the text.
    Returns a value between 0 and 1.
    """
    if not keywords:
        return 0.0
    text_lower = text.lower()
    found = sum(1 for kw in keywords if kw.lower() in text_lower)
    return found / len(keywords)
