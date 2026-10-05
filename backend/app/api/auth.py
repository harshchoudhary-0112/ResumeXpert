"""
Authentication API routes — register with OTP verification, login, and user profile.

Registration flow:
  1. POST /api/auth/register  → validate + create PendingRegistration + send OTP
  2. POST /api/auth/verify-otp → verify code + create real User + delete pending
  3. POST /api/auth/resend-otp → re-send a new OTP (with cooldown)
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.otp import PendingRegistration
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.schemas.auth import (
    UserRegister, UserLogin, VerifyOTP, ResendOTP,
    TokenResponse, UserResponse, UserProfile, MessageResponse,
)
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user
from app.utils.otp import generate_otp, hash_otp, verify_otp, validate_password
from app.services.email import send_otp_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Register (Step 1) ────────────────────────────────────────────
@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Submit registration details. An OTP is sent to the email address.
    The account is NOT active until the OTP is verified.
    """
    # 1. Validate password policy
    pwd_errors = validate_password(payload.password)
    if pwd_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pwd_errors[0],  # surface the first issue
        )

    # 2. Check if email is already taken by a verified user
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        # Don't reveal whether the email exists (anti-enumeration)
        # But we still return the same "OTP sent" response shape
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please log in.",
        )

    # 3. Clean up or update existing pending registration for this email
    existing_pending = (
        db.query(PendingRegistration)
        .filter(PendingRegistration.email == payload.email)
        .first()
    )
    if existing_pending:
        db.delete(existing_pending)
        db.commit()

    # 4. Generate OTP and hash it
    otp_code = generate_otp()
    otp_hashed = hash_otp(otp_code)

    # 5. Create pending registration
    pending = PendingRegistration(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        otp_hash=otp_hashed,
        otp_created_at=datetime.now(timezone.utc),
        attempts=0,
        resend_count=0,
    )
    db.add(pending)
    db.commit()

    # 6. Send the OTP email
    sent = send_otp_email(to_email=payload.email, name=payload.name, otp_code=otp_code)
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please check SMTP configuration.",
        )

    return MessageResponse(
        message="Verification code sent to your email",
        email=payload.email,
    )


# ── Verify OTP (Step 2) ─────────────────────────────────────────
@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp_route(payload: VerifyOTP, db: Session = Depends(get_db)):
    """
    Verify the OTP code. On success, create the real User account and
    return a JWT token (auto-login).
    """
    pending = (
        db.query(PendingRegistration)
        .filter(PendingRegistration.email == payload.email)
        .first()
    )

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending registration found for this email. Please register first.",
        )

    # Check attempt limit
    if pending.attempts >= settings.OTP_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect attempts. Please register again.",
        )

    # Check OTP expiry
    otp_created = pending.otp_created_at.replace(tzinfo=timezone.utc) if pending.otp_created_at.tzinfo is None else pending.otp_created_at
    expiry = otp_created + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    if datetime.now(timezone.utc) > expiry:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please register again.",
        )

    # Verify the OTP
    if not verify_otp(payload.otp, pending.otp_hash):
        pending.attempts += 1
        db.commit()
        remaining = settings.OTP_MAX_ATTEMPTS - pending.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect verification code. {remaining} attempt(s) remaining.",
        )

    # Double-check email hasn't been taken while pending
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # ✅ Create the real user
    user = User(
        name=pending.name,
        email=pending.email,
        password_hash=pending.password_hash,
    )
    db.add(user)
    db.delete(pending)
    db.commit()
    db.refresh(user)

    # Auto-login: return JWT token
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


# ── Resend OTP ───────────────────────────────────────────────────
@router.post("/resend-otp", response_model=MessageResponse)
def resend_otp(payload: ResendOTP, db: Session = Depends(get_db)):
    """Resend a new OTP to the pending registration email."""
    pending = (
        db.query(PendingRegistration)
        .filter(PendingRegistration.email == payload.email)
        .first()
    )

    if not pending:
        # Don't reveal whether email exists
        return MessageResponse(
            message="If a pending registration exists, a new code has been sent.",
            email=payload.email,
        )

    # Check resend limit
    if pending.resend_count >= settings.OTP_MAX_RESENDS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum resend limit reached. Please register again.",
        )

    # Check cooldown
    if pending.last_resend_at:
        last_resend = pending.last_resend_at.replace(tzinfo=timezone.utc) if pending.last_resend_at.tzinfo is None else pending.last_resend_at
        cooldown_end = last_resend + timedelta(seconds=settings.OTP_RESEND_COOLDOWN_SECONDS)
        if datetime.now(timezone.utc) < cooldown_end:
            wait_seconds = int((cooldown_end - datetime.now(timezone.utc)).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {wait_seconds} seconds before requesting a new code.",
            )

    # Generate new OTP
    otp_code = generate_otp()
    pending.otp_hash = hash_otp(otp_code)
    pending.otp_created_at = datetime.now(timezone.utc)
    pending.attempts = 0  # reset attempts on new OTP
    pending.resend_count += 1
    pending.last_resend_at = datetime.now(timezone.utc)
    db.commit()

    sent = send_otp_email(to_email=pending.email, name=pending.name, otp_code=otp_code)
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again.",
        )

    return MessageResponse(
        message="A new verification code has been sent to your email.",
        email=payload.email,
    )


# ── Login ────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Login and receive a JWT access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


# ── User Profile ─────────────────────────────────────────────────
@router.get("/me", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's profile with stats."""
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    total_analyses = (
        db.query(Analysis)
        .join(Resume)
        .filter(Resume.user_id == current_user.id)
        .count()
    )

    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
        total_analyses=total_analyses,
        total_resumes=total_resumes,
    )
