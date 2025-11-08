"""
Unit tests for VerificationToken model
"""
import pytest
from datetime import datetime, timedelta
from src.models.verification_token import VerificationToken


def test_verification_token_creation():
    """Test VerificationToken model instantiation"""
    token = VerificationToken(
        user_id="user-123",
        token="abc123token"
    )
    assert token.user_id == "user-123"
    assert token.token == "abc123token"
    assert token.is_used is False
    assert token.used_at is None


def test_verification_token_expiry():
    """Test token expiration (24 hours)"""
    token = VerificationToken(
        user_id="user-123",
        token="abc123"
    )
    # Should expire 24 hours from creation
    assert token.expires_at > datetime.utcnow()
    assert token.expires_at <= datetime.utcnow() + timedelta(hours=24, minutes=1)


def test_verification_token_usage():
    """Test marking token as used"""
    token = VerificationToken(
        user_id="user-123",
        token="abc123"
    )
    token.is_used = True
    token.used_at = datetime.utcnow()

    assert token.is_used is True
    assert token.used_at is not None
