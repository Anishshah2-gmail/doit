"""
Unit tests for email and input validators
"""
import pytest
from src.lib.validators import validate_email


def test_validate_email_valid():
    """Test valid email addresses (FR-002)"""
    assert validate_email("user@example.com") is True
    assert validate_email("test.user@domain.co.uk") is True
    assert validate_email("name+tag@company.org") is True


def test_validate_email_invalid():
    """Test invalid email addresses"""
    assert validate_email("not-an-email") is False
    assert validate_email("missing@domain") is False
    assert validate_email("@nodomain.com") is False
    assert validate_email("spaces in@email.com") is False


def test_validate_email_normalization():
    """Test email is normalized to lowercase"""
    email = "Test@Example.COM"
    normalized = validate_email(email, normalize=True)
    assert normalized == "test@example.com"
