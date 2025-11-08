"""
Session model for user authentication.
Stores active user sessions with JWT tokens.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timedelta
from src.lib.database import Base
from src.config import settings
import uuid


class Session(Base):
    """
    Session model for authenticated users.

    Tracks active user sessions with JWT tokens for authentication.
    Sessions expire after configured duration and can be deactivated.

    Requirements: FR-011, FR-012, FR-013
    """

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(512), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, token: str, **kwargs):
        """
        Initialize Session.

        Args:
            user_id: User ID this session belongs to
            token: JWT session token
            **kwargs: Additional fields
        """
        # Set defaults
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('created_at', datetime.utcnow())

        # Set expiry if not provided
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.utcnow() + timedelta(
                hours=settings.SESSION_EXPIRY_HOURS
            )

        super().__init__(user_id=user_id, token=token, **kwargs)

    def is_expired(self) -> bool:
        """
        Check if session has expired.

        Returns:
            bool: True if session is expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
