"""
VerificationToken model for email verification.
Represents a token sent to users to verify their email address.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.lib.database import Base
from src.config import settings
from datetime import datetime, timedelta
import uuid


class VerificationToken(Base):
    """
    Email verification token model.

    Fields:
        id: Unique token identifier (UUID)
        user_id: Associated user (foreign key)
        token: Secure random token (64-char hex)
        created_at: Token creation timestamp
        expires_at: Token expiration (24 hours from creation)
        is_used: Token usage status
        used_at: When token was used

    Requirements: FR-005 (email verification), FR-017 (prevent unverified login)
    """
    __tablename__ = "verification_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    used_at = Column(DateTime, nullable=True)

    # Relationship (will be configured when User model is updated)
    # user = relationship("User", back_populates="verification_tokens")

    __table_args__ = (
        Index('idx_verification_expires', 'expires_at', 'is_used'),
    )

    def __init__(self, user_id: str, token: str, **kwargs):
        """
        Initialize VerificationToken with expiration.

        Args:
            user_id: Associated user ID
            token: Verification token
            **kwargs: Additional fields
        """
        # Set defaults
        kwargs.setdefault('id', str(uuid.uuid4()))
        kwargs.setdefault('created_at', datetime.utcnow())
        kwargs.setdefault('expires_at',
                         datetime.utcnow() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRY_HOURS))
        kwargs.setdefault('is_used', False)

        super().__init__(user_id=user_id, token=token, **kwargs)

    def is_expired(self) -> bool:
        """Check if token has expired"""
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<VerificationToken(id={self.id}, user_id={self.user_id}, used={self.is_used})>"
