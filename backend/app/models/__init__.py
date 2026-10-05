"""
Models package — import all ORM models so SQLAlchemy can discover them.
"""

from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.analysis import Analysis, Suggestion
from app.models.otp import PendingRegistration

__all__ = ["User", "Resume", "JobDescription", "Analysis", "Suggestion", "PendingRegistration"]
