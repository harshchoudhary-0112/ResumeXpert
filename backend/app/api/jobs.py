"""
Job Description API routes — create, list, and retrieve JDs.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.job import JobDescription
from app.schemas.job import JobDescriptionCreate, JobDescriptionResponse, JobDescriptionListItem
from app.utils.auth import get_current_user
from app.services.nlp import parse_job_description

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["Job Descriptions"])


@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    payload: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create and parse a new job description."""
    # Parse the JD to extract structured info
    parsed = parse_job_description(payload.description)

    jd = JobDescription(
        user_id=current_user.id,
        title=payload.title,
        company=payload.company,
        description=payload.description,
        required_skills=parsed.get("required_skills", []),
        preferred_skills=parsed.get("preferred_skills", []),
        experience_requirements=parsed.get("experience_requirements"),
        education_requirements=parsed.get("education_requirements"),
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    return jd


@router.get("/", response_model=List[JobDescriptionListItem])
def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all job descriptions created by the current user."""
    jobs = (
        db.query(JobDescription)
        .filter(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )
    return jobs


@router.get("/{job_id}", response_model=JobDescriptionResponse)
def get_job_description(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific job description by ID."""
    jd = (
        db.query(JobDescription)
        .filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id)
        .first()
    )
    if not jd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return jd


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_description(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a job description and its associated analyses."""
    jd = (
        db.query(JobDescription)
        .filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id)
        .first()
    )
    if not jd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    db.delete(jd)
    db.commit()
