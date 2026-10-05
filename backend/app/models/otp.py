"""OTP model — stores pending email verification codes for registration."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base


class PendingRegistration(Base):
    """
    Stores temporary registration data and OTP verification state.
    Entries are cleaned up after successful verification or expiry.
    """
    __tablename__ = "pending_registrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # OTP fields — code is stored as a bcrypt hash
    otp_hash = Column(String(255), nullable=False)
    otp_created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Rate-limiting / abuse prevention
    attempts = Column(Integer, default=0)             # incorrect OTP submissions
    resend_count = Column(Integer, default=0)          # how many times OTP was resent
    last_resend_at = Column(DateTime, nullable=True)   # timestamp of last resend

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PendingRegistration(id={self.id}, email='{self.email}')>"
