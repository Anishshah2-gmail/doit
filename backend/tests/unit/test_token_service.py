"""
Unit tests for TokenService
Tests secure token generation for email verification and password reset
"""
import pytest
from src.services.token_service import TokenService


def test_generate_token():
    """Test token generation produces valid token"""
    service = TokenService()
    token = service.generate_token()

    assert len(token) == 64  # 32 bytes = 64 hex chars
    assert isinstance(token, str)


def test_generate_token_uniqueness():
    """Test that tokens are unique"""
    service = TokenService()
    token1 = service.generate_token()
    token2 = service.generate_token()

    assert token1 != token2


def test_generate_token_url_safe():
    """Test that tokens are URL-safe (hexadecimal)"""
    service = TokenService()
    token = service.generate_token()

    # Should only contain hex characters (0-9, a-f)
    assert all(c in '0123456789abcdef' for c in token)
