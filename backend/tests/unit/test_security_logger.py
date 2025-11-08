"""
Unit tests for SecurityLogger
Tests logging of security events for audit trail
"""
import pytest
from unittest.mock import patch, MagicMock, call
from src.lib.security_logger import SecurityLogger, SecurityEvent


def test_security_logger_initialization():
    """Test SecurityLogger can be instantiated"""
    logger = SecurityLogger()
    assert logger is not None


def test_log_registration_attempt():
    """Test logging user registration attempt"""
    logger = SecurityLogger()

    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_registration_attempt(
            email="test@example.com",
            success=True,
            ip_address="192.168.1.1"
        )

        # Verify logging was called
        assert mock_info.called
        call_args = str(mock_info.call_args)
        assert "registration_success" in call_args
        assert "test@example.com" in call_args


def test_log_registration_failure():
    """Test logging failed registration attempt"""
    logger = SecurityLogger()

    with patch.object(logger.logger, 'warning') as mock_warning:
        logger.log_registration_attempt(
            email="test@example.com",
            success=False,
            reason="Email already registered",
            ip_address="192.168.1.1"
        )

        # Verify warning was logged for failure
        assert mock_warning.called
        call_args = str(mock_warning.call_args)
        assert "registration_failure" in call_args
        assert "Email already registered" in call_args


def test_log_email_verification():
    """Test logging email verification event"""
    logger = SecurityLogger()

    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_email_verification(
            user_id="user123",
            email="test@example.com",
            success=True
        )

        assert mock_info.called
        call_args = str(mock_info.call_args)
        assert "email_verification" in call_args


def test_log_login_attempt():
    """Test logging login attempt"""
    logger = SecurityLogger()

    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_login_attempt(
            email="test@example.com",
            success=True,
            ip_address="192.168.1.1"
        )

        assert mock_info.called
        call_args = str(mock_info.call_args)
        assert "login_success" in call_args


def test_log_password_reset_request():
    """Test logging password reset request"""
    logger = SecurityLogger()

    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_password_reset_request(
            email="test@example.com",
            ip_address="192.168.1.1"
        )

        assert mock_info.called
        call_args = str(mock_info.call_args)
        assert "password_reset_request" in call_args
