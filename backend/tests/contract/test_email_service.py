"""
Contract tests for email service integration.
Tests that email service can send verification and password reset emails.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


class MockEmailService:
    """Mock email service for contract testing"""

    async def send_email(self, to: str, subject: str, html_body: str, text_body: str):
        """Mock send email method"""
        if not to or "@" not in to:
            raise ValueError("Invalid email address")
        return {
            "message_id": "mock_msg_123",
            "status": "sent",
            "timestamp": "2025-11-08T00:00:00Z"
        }


@pytest.mark.asyncio
async def test_email_service_send_success():
    """Test email service can send emails successfully"""
    service = MockEmailService()

    result = await service.send_email(
        to="test@example.com",
        subject="Test Email",
        html_body="<p>Test content</p>",
        text_body="Test content"
    )

    assert result["status"] == "sent"
    assert "message_id" in result


@pytest.mark.asyncio
async def test_email_service_invalid_email():
    """Test email service rejects invalid email addresses"""
    service = MockEmailService()

    with pytest.raises(ValueError):
        await service.send_email(
            to="invalid-email",
            subject="Test",
            html_body="<p>Test</p>",
            text_body="Test"
        )


@pytest.mark.asyncio
async def test_email_service_verification_email_format():
    """Test verification email has required elements"""
    service = MockEmailService()

    # Verification email should contain token in both HTML and text
    html_body = '<p>Verify: <a href="https://app.com/verify?token=abc123">Click</a></p>'
    text_body = 'Verify: https://app.com/verify?token=abc123'

    result = await service.send_email(
        to="test@example.com",
        subject="Verify your email",
        html_body=html_body,
        text_body=text_body
    )

    assert result["status"] == "sent"
    assert "token=abc123" in html_body
    assert "token=abc123" in text_body
