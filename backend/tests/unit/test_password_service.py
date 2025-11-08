"""
Unit tests for PasswordService
Tests password hashing, verification, and strength validation
"""
import pytest
from src.services.password_service import PasswordService


def test_hash_password():
    """Test password hashing with Argon2"""
    service = PasswordService()
    password = "SecurePass123!"
    hashed = service.hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")


def test_verify_password_success():
    """Test password verification with correct password"""
    service = PasswordService()
    password = "SecurePass123!"
    hashed = service.hash_password(password)

    assert service.verify_password(password, hashed) is True


def test_verify_password_failure():
    """Test password verification with wrong password"""
    service = PasswordService()
    password = "SecurePass123!"
    hashed = service.hash_password(password)

    assert service.verify_password("WrongPass", hashed) is False


def test_validate_password_strength_valid():
    """Test valid password that meets all requirements (FR-003)"""
    service = PasswordService()
    assert service.validate_strength("SecurePass123!") is True
    assert service.validate_strength("MyP@ssw0rd") is True
    assert service.validate_strength("C0mpl3x!Pass") is True


def test_validate_password_strength_too_short():
    """Test password too short (< 8 characters)"""
    service = PasswordService()
    assert service.validate_strength("Short1!") is False
    assert service.validate_strength("Abc123!") is False


def test_validate_password_strength_no_uppercase():
    """Test password without uppercase letter"""
    service = PasswordService()
    assert service.validate_strength("securepass123!") is False


def test_validate_password_strength_no_lowercase():
    """Test password without lowercase letter"""
    service = PasswordService()
    assert service.validate_strength("SECUREPASS123!") is False


def test_validate_password_strength_no_digit():
    """Test password without digit"""
    service = PasswordService()
    assert service.validate_strength("SecurePass!") is False


def test_validate_password_strength_no_special():
    """Test password without special character"""
    service = PasswordService()
    assert service.validate_strength("SecurePass123") is False


def test_password_hashing_produces_unique_hashes():
    """Test that same password produces different hashes (salting)"""
    service = PasswordService()
    password = "SecurePass123!"
    hash1 = service.hash_password(password)
    hash2 = service.hash_password(password)

    assert hash1 != hash2
    assert service.verify_password(password, hash1) is True
    assert service.verify_password(password, hash2) is True
