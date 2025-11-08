"""
Unit tests for User model
Tests user creation, email normalization, and lockout logic
"""
import pytest
from datetime import datetime, timedelta
from src.models.user import User


def test_user_creation():
    """Test User model instantiation with defaults"""
    user = User(
        email="test@example.com",
        password_hash="hashed_password_here"
    )
    assert user.email == "test@example.com"
    assert user.email_verified is False
    assert user.is_active is True
    assert user.is_locked is False
    assert user.failed_login_attempts == 0


def test_user_email_normalization():
    """Test email is normalized to lowercase"""
    user = User(email="Test@Example.COM", password_hash="hash")
    assert user.email == "test@example.com"


def test_user_lockout_status():
    """Test account lockout tracking (FR-009, FR-010)"""
    user = User(email="test@example.com", password_hash="hash")
    user.is_locked = True
    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
    user.failed_login_attempts = 5

    assert user.is_locked is True
    assert user.failed_login_attempts == 5
    assert user.locked_until > datetime.utcnow()
