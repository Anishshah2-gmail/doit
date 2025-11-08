"""
Unit tests for PasswordResetToken model
Tests password reset token creation, expiry, and usage tracking
"""
import pytest
from datetime import datetime, timedelta
from src.models.password_reset_token import PasswordResetToken
from src.config import settings


def test_password_reset_token_creation():
    """Test creating a password reset token"""
    token = PasswordResetToken(
        user_id="user123",
        token="reset-token-abc123"
    )

    assert token.user_id == "user123"
    assert token.token == "reset-token-abc123"
    assert token.is_used is False
    assert token.expires_at is not None
    assert token.created_at is not None


def test_password_reset_token_expiry_default():
    """Test token expires after configured hours (1 hour default)"""
    token = PasswordResetToken(
        user_id="user123",
        token="reset-token-abc123"
    )

    # Should expire after RESET_TOKEN_EXPIRY_HOURS (1 hour)
    expected_expiry = datetime.utcnow() + timedelta(hours=settings.RESET_TOKEN_EXPIRY_HOURS)
    # Allow 1 second tolerance
    assert abs((token.expires_at - expected_expiry).total_seconds()) < 1


def test_password_reset_token_is_expired_false():
    """Test token is not expired when within expiry time"""
    token = PasswordResetToken(
        user_id="user123",
        token="reset-token-abc123"
    )

    assert token.is_expired() is False


def test_password_reset_token_is_expired_true():
    """Test token is expired when past expiry time"""
    token = PasswordResetToken(
        user_id="user123",
        token="reset-token-abc123",
        expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    )

    assert token.is_expired() is True


def test_password_reset_token_usage_tracking():
    """Test token usage can be tracked"""
    token = PasswordResetToken(
        user_id="user123",
        token="reset-token-abc123"
    )

    assert token.is_used is False
    assert token.used_at is None

    # Mark as used
    token.is_used = True
    token.used_at = datetime.utcnow()

    assert token.is_used is True
    assert token.used_at is not None


def test_password_reset_token_custom_expiry():
    """Test token can have custom expiry time"""
    custom_expiry = datetime.utcnow() + timedelta(hours=2)
    token = PasswordResetToken(
        user_id="user123",
        token="reset-token-abc123",
        expires_at=custom_expiry
    )

    assert token.expires_at == custom_expiry
