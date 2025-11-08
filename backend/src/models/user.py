"""
User model for authentication system.
Represents a registered user account with authentication credentials.
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Index
from sqlalchemy.orm import relationship
from src.lib.database import Base
from datetime import datetime
import uuid


class User(Base):
    """
    User model representing authenticated user accounts.

    Fields:
        id: Unique user identifier (UUID)
        email: User email (unique, normalized to lowercase)
        password_hash: Argon2 hashed password
        email_verified: Email verification status
        is_active: Account active status
        is_locked: Account lockout status (after failed logins)
        locked_until: Auto-unlock timestamp
        failed_login_attempts: Failed login counter
        last_failed_login: Most recent failed login timestamp
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
        last_login_at: Most recent successful login

    Requirements: FR-001, FR-004, FR-006, FR-009, FR-010, FR-017
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships (will be added as other models are created)
    # sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    # verification_tokens = relationship("VerificationToken", back_populates="user", cascade="all, delete-orphan")
    # password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_locked', 'is_locked', 'locked_until'),
    )

    def __init__(self, email: str, password_hash: str, **kwargs):
        """
        Initialize User with normalized email and defaults.

        Args:
            email: User email address (will be normalized to lowercase)
            password_hash: Argon2 hashed password
            **kwargs: Additional fields
        """
        # Set defaults if not provided
        kwargs.setdefault('id', str(uuid.uuid4()))
        kwargs.setdefault('email_verified', False)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_locked', False)
        kwargs.setdefault('failed_login_attempts', 0)
        kwargs.setdefault('created_at', datetime.utcnow())
        kwargs.setdefault('updated_at', datetime.utcnow())

        super().__init__(email=email.lower(), password_hash=password_hash, **kwargs)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, verified={self.email_verified})>"
