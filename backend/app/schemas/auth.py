"""Pydantic schemas for authentication requests and responses."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserRegister(BaseModel):
    """Registration request body — step 1: submit details and receive OTP."""
    name: str = Field(..., min_length=2, max_length=100, examples=["John Doe"])
    email: str = Field(..., min_length=5, max_length=255, examples=["john@example.com"])
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Strict email format validation."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Ensure confirm_password matches password."""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class VerifyOTP(BaseModel):
    """OTP verification request body — step 2: submit the code."""
    email: str = Field(..., examples=["john@example.com"])
    otp: str = Field(..., min_length=6, max_length=6, examples=["123456"])


class ResendOTP(BaseModel):
    """Resend OTP request body."""
    email: str = Field(..., examples=["john@example.com"])


class UserLogin(BaseModel):
    """Login request body."""
    email: str = Field(..., examples=["john@example.com"])
    password: str = Field(...)


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    email: str | None = None


class UserResponse(BaseModel):
    """User profile response (excludes password)."""
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Extended user profile with stats."""
    id: int
    name: str
    email: str
    created_at: datetime
    total_analyses: int = 0
    total_resumes: int = 0

    class Config:
        from_attributes = True
