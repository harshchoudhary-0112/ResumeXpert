"""
Resume API routes — upload, parse, list, and retrieve resumes.
"""

import os
import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeListItem, ParsedResume
from app.utils.auth import get_current_user
from app.services.parser import parse_resume

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and parse a resume file (PDF or DOCX)."""
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Supported formats: {settings.ALLOWED_EXTENSIONS}",
        )

    # Read and validate file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Save file to disk
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        # Parse the resume
        raw_text, cleaned_text, parsed_data = parse_resume(file_path)

        # Store in database
        resume = Resume(
            user_id=current_user.id,
            filename=file.filename,
            raw_text=cleaned_text,
            parsed_data=parsed_data,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        return ResumeResponse(
            id=resume.id,
            filename=resume.filename,
            parsed_data=ParsedResume(**parsed_data) if parsed_data else None,
            created_at=resume.created_at,
        )

    except Exception as e:
        # Clean up the file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Resume parsing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume: {str(e)}",
        )


@router.get("/", response_model=List[ResumeListItem])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all resumes uploaded by the current user."""
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )

    result = []
    for r in resumes:
        name = None
        if r.parsed_data and isinstance(r.parsed_data, dict):
            name = r.parsed_data.get("name")
        result.append(ResumeListItem(
            id=r.id,
            filename=r.filename,
            created_at=r.created_at,
            name=name,
        ))

    return result


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific resume by ID."""
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    return ResumeResponse(
        id=resume.id,
        filename=resume.filename,
        parsed_data=ParsedResume(**resume.parsed_data) if resume.parsed_data else None,
        created_at=resume.created_at,
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a resume and its associated analyses."""
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    db.delete(resume)
    db.commit()
