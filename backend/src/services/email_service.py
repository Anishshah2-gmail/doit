"""
Email service for sending verification and password reset emails.
Supports async SMTP sending.
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import settings
from typing import Optional


class EmailService:
    """
    Email service for authentication-related emails.

    Sends verification and password reset emails via SMTP.
    Requirements: FR-005, FR-011
    """

    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> dict:
        """
        Send an email via SMTP.

        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (fallback)

        Returns:
            dict: Status information

        Raises:
            Exception: If email sending fails
        """
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to

        # Attach text and HTML parts
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)

        # For development without SMTP server, just log
        if settings.ENV == "development" and self.smtp_host == "localhost" and self.smtp_port == 1025:
            print(f"\n{'='*60}")
            print(f"[EMAIL] To: {to}")
            print(f"[EMAIL] Subject: {subject}")
            print(f"[EMAIL] Body (text):\n{text_body}")
            print(f"{'='*60}\n")
            return {
                "message_id": "dev_mock_message",
                "status": "sent",
                "timestamp": "2025-11-08T00:00:00Z"
            }

        # Send via SMTP
        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user if self.smtp_user else None,
                password=self.smtp_password if self.smtp_password else None,
                use_tls=self.smtp_port == 587,
            )
            return {
                "message_id": "smtp_message",
                "status": "sent",
                "timestamp": "2025-11-08T00:00:00Z"
            }
        except Exception as e:
            print(f"Email sending failed: {e}")
            raise

    async def send_verification_email(self, to: str, token: str, base_url: str = "http://localhost:8000") -> dict:
        """
        Send email verification email.

        Args:
            to: Recipient email
            token: Verification token
            base_url: Application base URL

        Returns:
            dict: Send status

        Requirements: FR-005
        """
        verify_url = f"{base_url}/auth/verify-email?token={token}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Welcome to {settings.APP_NAME}!</h2>
            <p>Please verify your email address to complete registration.</p>
            <p>
                <a href="{verify_url}"
                   style="background-color: #4CAF50; color: white; padding: 10px 20px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify Email Address
                </a>
            </p>
            <p>Or copy and paste this link in your browser:</p>
            <p>{verify_url}</p>
            <p style="color: #666; font-size: 12px;">This link expires in 24 hours.</p>
            <p style="color: #666; font-size: 12px;">
                If you didn't create an account, please ignore this email.
            </p>
        </body>
        </html>
        """

        text_body = f"""
Welcome to {settings.APP_NAME}!

Please verify your email address to complete registration.

Verify your email by visiting this link:
{verify_url}

This link expires in 24 hours.

If you didn't create an account, please ignore this email.
        """

        return await self.send_email(
            to=to,
            subject=f"Verify your {settings.APP_NAME} email address",
            html_body=html_body,
            text_body=text_body
        )

    async def send_password_reset_email(self, to: str, token: str, base_url: str = "http://localhost:8000") -> dict:
        """
        Send password reset email.

        Args:
            to: Recipient email
            token: Password reset token
            base_url: Application base URL

        Returns:
            dict: Send status

        Requirements: FR-011, FR-012
        """
        reset_url = f"{base_url}/password/reset?token={token}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your {settings.APP_NAME} account.</p>
            <p>
                <a href="{reset_url}"
                   style="background-color: #2196F3; color: white; padding: 10px 20px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>Or copy and paste this link in your browser:</p>
            <p>{reset_url}</p>
            <p style="color: #666; font-size: 12px;">This link expires in 1 hour.</p>
            <p style="color: #e53935; font-size: 12px;">
                <strong>Security Notice:</strong> If you didn't request this password reset,
                please ignore this email. Your password will not be changed.
            </p>
        </body>
        </html>
        """

        text_body = f"""
Password Reset Request

You requested a password reset for your {settings.APP_NAME} account.

Reset your password by visiting this link:
{reset_url}

This link expires in 1 hour.

Security Notice: If you didn't request this password reset, please ignore this email.
Your password will not be changed.
        """

        return await self.send_email(
            to=to,
            subject=f"Reset your {settings.APP_NAME} password",
            html_body=html_body,
            text_body=text_body
        )
