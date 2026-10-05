"""Pydantic schemas for resume upload and parsed data."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


class ParsedResume(BaseModel):
    """Structured data extracted from a resume."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    skills_with_categories: List[Dict[str, str]] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_sections: Dict[str, str] = Field(default_factory=dict)


class ResumeResponse(BaseModel):
    """Response after uploading and parsing a resume."""
    id: int
    filename: str
    parsed_data: Optional[ParsedResume] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeListItem(BaseModel):
    """Lightweight resume item for list views."""
    id: int
    filename: str
    created_at: datetime
    name: Optional[str] = None

    class Config:
        from_attributes = True
