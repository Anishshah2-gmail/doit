"""
Unit tests for Session model
Tests session creation, expiry, and token management
"""
import pytest
from datetime import datetime, timedelta
from src.models.session import Session
from src.config import settings


def test_session_creation():
    """Test creating a session"""
    session = Session(
        user_id="user123",
        token="session-token-123"
    )

    assert session.user_id == "user123"
    assert session.token == "session-token-123"
    assert session.is_active is True
    assert session.expires_at is not None
    assert session.created_at is not None


def test_session_expiry_default():
    """Test session expires after configured hours"""
    session = Session(
        user_id="user123",
        token="session-token-123"
    )

    # Should expire after SESSION_EXPIRY_HOURS
    expected_expiry = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRY_HOURS)
    # Allow 1 second tolerance for test execution time
    assert abs((session.expires_at - expected_expiry).total_seconds()) < 1


def test_session_is_expired_false():
    """Test session is not expired when within expiry time"""
    session = Session(
        user_id="user123",
        token="session-token-123"
    )

    # Should not be expired
    assert session.is_expired() is False


def test_session_is_expired_true():
    """Test session is expired when past expiry time"""
    session = Session(
        user_id="user123",
        token="session-token-123",
        expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    )

    assert session.is_expired() is True


def test_session_deactivation():
    """Test session can be deactivated"""
    session = Session(
        user_id="user123",
        token="session-token-123"
    )

    assert session.is_active is True

    # Manually deactivate (would be done by logout)
    session.is_active = False
    assert session.is_active is False


def test_session_custom_expiry():
    """Test session can have custom expiry time"""
    custom_expiry = datetime.utcnow() + timedelta(hours=48)
    session = Session(
        user_id="user123",
        token="session-token-123",
        expires_at=custom_expiry
    )

    assert session.expires_at == custom_expiry
