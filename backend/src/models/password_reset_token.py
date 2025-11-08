"""
PasswordResetToken model for password reset functionality.
Stores tokens for password reset requests with expiry.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timedelta
from src.lib.database import Base
from src.config import settings
import uuid


class PasswordResetToken(Base):
    """
    Password reset token model.

    Stores tokens for password reset requests. Tokens expire after
    configured duration (default 1 hour) and can only be used once.

    Requirements: FR-014, FR-015
    """

    __tablename__ = "password_reset_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(64), nullable=False, unique=True, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, token: str, **kwargs):
        """
        Initialize PasswordResetToken.

        Args:
            user_id: User ID this token belongs to
            token: Reset token string
            **kwargs: Additional fields
        """
        # Set defaults
        kwargs.setdefault('is_used', False)
        kwargs.setdefault('created_at', datetime.utcnow())

        # Set expiry if not provided (1 hour default)
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.utcnow() + timedelta(
                hours=settings.RESET_TOKEN_EXPIRY_HOURS
            )

        super().__init__(user_id=user_id, token=token, **kwargs)

    def is_expired(self) -> bool:
        """
        Check if token has expired.

        Returns:
            bool: True if token is expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.is_used})>"
