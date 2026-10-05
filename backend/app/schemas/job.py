"""Pydantic schemas for job description input and responses."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class JobDescriptionCreate(BaseModel):
    """Request body for creating a new job description."""
    title: Optional[str] = Field(None, max_length=255, examples=["Senior Python Developer"])
    company: Optional[str] = Field(None, max_length=255, examples=["TechCorp Inc."])
    description: str = Field(..., min_length=50, examples=[
        "We are looking for a Senior Python Developer with 5+ years of experience..."
    ])


class JobDescriptionResponse(BaseModel):
    """Full job description response with extracted fields."""
    id: int
    title: Optional[str] = None
    company: Optional[str] = None
    description: str
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_requirements: Optional[str] = None
    education_requirements: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobDescriptionListItem(BaseModel):
    """Lightweight JD item for list views."""
    id: int
    title: Optional[str] = None
    company: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
