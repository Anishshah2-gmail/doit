"""
Unit tests for JWT Service
Tests JWT token generation and validation
"""
import pytest
from datetime import datetime, timedelta
from src.services.jwt_service import JWTService


def test_jwt_service_initialization():
    """Test JWTService can be instantiated"""
    service = JWTService()
    assert service is not None


def test_generate_session_token():
    """Test generating session token"""
    service = JWTService()
    token = service.generate_session_token(
        user_id="user123",
        email="test@example.com"
    )

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid():
    """Test verifying valid token"""
    service = JWTService()
    token = service.generate_session_token(
        user_id="user123",
        email="test@example.com"
    )

    payload = service.verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "user123"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload
    assert "iat" in payload


def test_verify_token_invalid():
    """Test verifying invalid token returns None"""
    service = JWTService()
    payload = service.verify_token("invalid-token-123")

    assert payload is None


def test_verify_token_expired():
    """Test verifying expired token returns None"""
    service = JWTService()

    # Generate token that expires immediately
    token = service.generate_session_token(
        user_id="user123",
        email="test@example.com",
        expires_delta=timedelta(seconds=-1)  # Already expired
    )

    payload = service.verify_token(token)
    assert payload is None


def test_token_contains_user_info():
    """Test token contains user information"""
    service = JWTService()
    token = service.generate_session_token(
        user_id="user789",
        email="another@example.com"
    )

    payload = service.verify_token(token)
    assert payload["user_id"] == "user789"
    assert payload["email"] == "another@example.com"


def test_custom_expiry_time():
    """Test token with custom expiry time"""
    service = JWTService()
    custom_delta = timedelta(hours=48)
    token = service.generate_session_token(
        user_id="user123",
        email="test@example.com",
        expires_delta=custom_delta
    )

    payload = service.verify_token(token)
    assert payload is not None

    # Check expiry is approximately correct (within 5 second tolerance)
    expected_exp = datetime.utcnow() + custom_delta
    actual_exp = datetime.utcfromtimestamp(payload["exp"])
    assert abs((actual_exp - expected_exp).total_seconds()) < 5
