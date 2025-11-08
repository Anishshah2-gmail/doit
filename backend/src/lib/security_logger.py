"""
Security logging for audit trail of authentication events.
Logs all security-relevant events (registration, login, password reset, etc.)
"""
import logging
from enum import Enum
from typing import Optional
from datetime import datetime


# Configure security logger
logger = logging.getLogger("security")
logger.setLevel(logging.INFO)

# Create console handler if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class SecurityEvent(Enum):
    """Security event types for logging"""
    REGISTRATION_ATTEMPT = "registration_attempt"
    REGISTRATION_SUCCESS = "registration_success"
    REGISTRATION_FAILURE = "registration_failure"
    EMAIL_VERIFICATION = "email_verification"
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"


class SecurityLogger:
    """
    Security event logger for authentication system.

    Provides structured logging for security events to enable:
    - Audit trails
    - Security monitoring
    - Incident investigation
    - Compliance requirements
    """

    def __init__(self):
        """Initialize SecurityLogger"""
        self.logger = logger

    def _log(self, level: str, event: SecurityEvent, **kwargs):
        """
        Internal method to log security events.

        Args:
            level: Log level (info, warning, error)
            event: Security event type
            **kwargs: Additional event data
        """
        timestamp = datetime.utcnow().isoformat()
        log_data = {
            "timestamp": timestamp,
            "event": event.value,
            **kwargs
        }

        # Format log message
        message = f"SecurityEvent: {event.value}"
        for key, value in kwargs.items():
            message += f" | {key}={value}"

        # Log at appropriate level
        if level == "info":
            self.logger.info(message, extra=log_data)
        elif level == "warning":
            self.logger.warning(message, extra=log_data)
        elif level == "error":
            self.logger.error(message, extra=log_data)

    def log_registration_attempt(
        self,
        email: str,
        success: bool,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log user registration attempt.

        Args:
            email: User email address
            success: Whether registration succeeded
            reason: Failure reason if unsuccessful
            ip_address: Client IP address
        """
        event = SecurityEvent.REGISTRATION_SUCCESS if success else SecurityEvent.REGISTRATION_FAILURE
        level = "info" if success else "warning"

        log_kwargs = {"email": email, "success": success}
        if reason:
            log_kwargs["reason"] = reason
        if ip_address:
            log_kwargs["ip_address"] = ip_address

        self._log(level, event, **log_kwargs)

    def log_email_verification(
        self,
        user_id: str,
        email: str,
        success: bool,
        reason: Optional[str] = None
    ):
        """
        Log email verification event.

        Args:
            user_id: User ID
            email: User email address
            success: Whether verification succeeded
            reason: Failure reason if unsuccessful
        """
        event = SecurityEvent.EMAIL_VERIFICATION
        level = "info" if success else "warning"

        log_kwargs = {"user_id": user_id, "email": email, "success": success}
        if reason:
            log_kwargs["reason"] = reason

        self._log(level, event, **log_kwargs)

    def log_login_attempt(
        self,
        email: str,
        success: bool,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Log login attempt.

        Args:
            email: User email address
            success: Whether login succeeded
            reason: Failure reason if unsuccessful
            ip_address: Client IP address
            user_id: User ID if successful
        """
        event = SecurityEvent.LOGIN_SUCCESS if success else SecurityEvent.LOGIN_FAILURE
        level = "info" if success else "warning"

        log_kwargs = {"email": email, "success": success}
        if reason:
            log_kwargs["reason"] = reason
        if ip_address:
            log_kwargs["ip_address"] = ip_address
        if user_id:
            log_kwargs["user_id"] = user_id

        self._log(level, event, **log_kwargs)

    def log_logout(self, user_id: str, email: str):
        """
        Log user logout.

        Args:
            user_id: User ID
            email: User email address
        """
        self._log("info", SecurityEvent.LOGOUT, user_id=user_id, email=email)

    def log_password_reset_request(
        self,
        email: str,
        ip_address: Optional[str] = None
    ):
        """
        Log password reset request.

        Args:
            email: User email address
            ip_address: Client IP address
        """
        log_kwargs = {"email": email}
        if ip_address:
            log_kwargs["ip_address"] = ip_address

        self._log("info", SecurityEvent.PASSWORD_RESET_REQUEST, **log_kwargs)

    def log_password_reset_success(
        self,
        user_id: str,
        email: str,
        ip_address: Optional[str] = None
    ):
        """
        Log successful password reset.

        Args:
            user_id: User ID
            email: User email address
            ip_address: Client IP address
        """
        log_kwargs = {"user_id": user_id, "email": email}
        if ip_address:
            log_kwargs["ip_address"] = ip_address

        self._log("info", SecurityEvent.PASSWORD_RESET_SUCCESS, **log_kwargs)

    def log_account_locked(
        self,
        user_id: str,
        email: str,
        reason: str,
        ip_address: Optional[str] = None
    ):
        """
        Log account lockout event.

        Args:
            user_id: User ID
            email: User email address
            reason: Lockout reason
            ip_address: Client IP address
        """
        log_kwargs = {"user_id": user_id, "email": email, "reason": reason}
        if ip_address:
            log_kwargs["ip_address"] = ip_address

        self._log("warning", SecurityEvent.ACCOUNT_LOCKED, **log_kwargs)
