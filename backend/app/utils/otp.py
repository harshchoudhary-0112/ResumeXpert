"""
OTP generation, hashing, and password policy validation utilities.
"""

import re
import secrets

from passlib.context import CryptContext

from app.config import settings

# Reuse a dedicated context for OTP hashing (bcrypt with low rounds for speed)
_otp_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_otp() -> str:
    """Generate a cryptographically secure OTP of the configured length."""
    upper = 10 ** settings.OTP_LENGTH
    code = secrets.randbelow(upper)
    return str(code).zfill(settings.OTP_LENGTH)


def hash_otp(otp: str) -> str:
    """Hash an OTP code using bcrypt."""
    return _otp_ctx.hash(otp)


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verify a plain OTP against its bcrypt hash."""
    return _otp_ctx.verify(plain_otp, hashed_otp)


def validate_password(password: str) -> list[str]:
    """
    Validate password against the security policy.

    Returns a list of error messages (empty = valid).

    Policy:
        - Minimum 8 characters
        - At least 1 uppercase letter (A-Z)
        - At least 1 lowercase letter (a-z)
        - At least 1 digit (0-9)
        - At least 1 special character (!@#$%^&*…)
    """
    errors: list[str] = []

    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter (A-Z)")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter (a-z)")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number (0-9)")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password):
        errors.append("Password must contain at least one special character")

    return errors
