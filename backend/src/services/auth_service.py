"""
Authentication service handling user registration, login, and verification.
Core business logic for user authentication system.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional
from src.models.user import User
from src.models.verification_token import VerificationToken
from src.models.password_reset_token import PasswordResetToken
from src.services.password_service import PasswordService
from src.services.token_service import TokenService
from src.services.email_service import EmailService
from src.services.jwt_service import JWTService
from src.lib.security_logger import SecurityLogger
from src.models.session import Session
from src.config import settings


class AuthService:
    """
    Authentication service for user management.

    Handles:
    - User registration (FR-001)
    - Email verification (FR-005, FR-017)
    - Login authentication (FR-007)
    - Account lockout (FR-009, FR-010)
    """

    def __init__(self, db: Session):
        """
        Initialize AuthService.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.password_service = PasswordService()
        self.token_service = TokenService()
        self.email_service = EmailService()
        self.jwt_service = JWTService()
        self.security_logger = SecurityLogger()

    async def register_user(self, email: str, password: str, base_url: str = "http://localhost:8000") -> User:
        """
        Register a new user with email and password.

        Args:
            email: User email address (will be normalized)
            password: Plain text password
            base_url: Application base URL for verification link

        Returns:
            User: Created user object

        Raises:
            ValueError: If email already exists or validation fails

        Requirements: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006
        """
        # Normalize email
        email = email.lower()

        # Check if user already exists (FR-006)
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            self.security_logger.log_registration_attempt(
                email=email,
                success=False,
                reason="Email already registered"
            )
            raise ValueError("Email address already registered")

        # Validate password strength (FR-003)
        if not self.password_service.validate_strength(password):
            self.security_logger.log_registration_attempt(
                email=email,
                success=False,
                reason="Weak password"
            )
            raise ValueError("Password does not meet security requirements")

        # Hash password (FR-004)
        password_hash = self.password_service.hash_password(password)

        # Create user
        user = User(
            email=email,
            password_hash=password_hash
        )
        self.db.add(user)
        self.db.flush()  # Get user ID without committing

        # Generate verification token (FR-005)
        token = self.token_service.generate_token()
        verification_token = VerificationToken(
            user_id=user.id,
            token=token
        )
        self.db.add(verification_token)
        self.db.commit()
        self.db.refresh(user)

        # Send verification email
        await self.email_service.send_verification_email(
            to=user.email,
            token=token,
            base_url=base_url
        )

        # Log successful registration
        self.security_logger.log_registration_attempt(
            email=user.email,
            success=True
        )

        return user

    async def verify_email(self, token: str) -> User:
        """
        Verify user email address using verification token.

        Args:
            token: Verification token from email

        Returns:
            User: User with verified email

        Raises:
            ValueError: If token is invalid or expired

        Requirements: FR-005, FR-017
        """
        # Find token
        verification_token = self.db.query(VerificationToken).filter(
            VerificationToken.token == token
        ).first()

        if not verification_token:
            self.security_logger.log_email_verification(
                user_id="unknown",
                email="unknown",
                success=False,
                reason="Invalid token"
            )
            raise ValueError("Invalid verification token")

        # Check if already used
        if verification_token.is_used:
            user = self.db.query(User).filter(User.id == verification_token.user_id).first()
            self.security_logger.log_email_verification(
                user_id=verification_token.user_id,
                email=user.email if user else "unknown",
                success=False,
                reason="Token already used"
            )
            raise ValueError("Verification token already used")

        # Check if expired
        if verification_token.is_expired():
            user = self.db.query(User).filter(User.id == verification_token.user_id).first()
            self.security_logger.log_email_verification(
                user_id=verification_token.user_id,
                email=user.email if user else "unknown",
                success=False,
                reason="Token expired"
            )
            raise ValueError("Verification token has expired")

        # Mark token as used
        verification_token.is_used = True
        verification_token.used_at = datetime.utcnow()

        # Update user
        user = self.db.query(User).filter(User.id == verification_token.user_id).first()
        if not user:
            raise ValueError("User not found")

        user.email_verified = True
        self.db.commit()
        self.db.refresh(user)

        # Log successful email verification
        self.security_logger.log_email_verification(
            user_id=user.id,
            email=user.email,
            success=True
        )

        return user

    async def resend_verification(self, email: str, base_url: str = "http://localhost:8000") -> dict:
        """
        Resend verification email to user.

        Args:
            email: User email address
            base_url: Application base URL for verification link

        Returns:
            dict: Status message

        Raises:
            ValueError: If user not found or already verified

        Requirements: FR-005
        """
        email = email.lower()

        # Find user
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Don't reveal if email exists (security)
            return {"message": "If the email exists and is not verified, a new verification email has been sent."}

        # Check if already verified
        if user.email_verified:
            return {"message": "Email already verified"}

        # Generate new token
        token = self.token_service.generate_token()
        verification_token = VerificationToken(
            user_id=user.id,
            token=token
        )
        self.db.add(verification_token)
        self.db.commit()

        # Send verification email
        await self.email_service.send_verification_email(
            to=user.email,
            token=token,
            base_url=base_url
        )

        return {"message": "Verification email sent"}

    async def login(self, email: str, password: str, ip_address: Optional[str] = None) -> dict:
        """
        Authenticate user and create session.

        Args:
            email: User email address
            password: Plain text password
            ip_address: Client IP address for logging

        Returns:
            dict: Session token and user info

        Raises:
            ValueError: If authentication fails

        Requirements: FR-007, FR-008, FR-009, FR-010
        """
        email = email.lower()

        # Find user
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Generic error to not reveal if email exists (security)
            self.security_logger.log_login_attempt(
                email=email,
                success=False,
                reason="Invalid credentials",
                ip_address=ip_address
            )
            raise ValueError("Invalid email or password")

        # Check if email is verified (FR-008)
        if not user.email_verified:
            self.security_logger.log_login_attempt(
                email=email,
                success=False,
                reason="Email not verified",
                ip_address=ip_address,
                user_id=user.id
            )
            raise ValueError("Please verify your email before logging in")

        # Check if account is locked (FR-010)
        if user.is_locked:
            # Check if lockout period has expired
            if user.locked_until and datetime.utcnow() < user.locked_until:
                self.security_logger.log_login_attempt(
                    email=email,
                    success=False,
                    reason="Account locked",
                    ip_address=ip_address,
                    user_id=user.id
                )
                raise ValueError(f"Account is locked until {user.locked_until.isoformat()}Z")
            else:
                # Unlock account
                user.is_locked = False
                user.locked_until = None
                user.failed_login_attempts = 0
                self.db.commit()

        # Verify password
        if not self.password_service.verify_password(password, user.password_hash):
            # Increment failed attempts (FR-009)
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.utcnow()

            # Lock account if max attempts reached
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.is_locked = True
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
                self.db.commit()

                self.security_logger.log_account_locked(
                    user_id=user.id,
                    email=user.email,
                    reason=f"Max login attempts ({settings.MAX_LOGIN_ATTEMPTS}) exceeded",
                    ip_address=ip_address
                )
                raise ValueError(f"Account locked due to too many failed login attempts. Try again after {user.locked_until.isoformat()}Z")

            self.db.commit()

            self.security_logger.log_login_attempt(
                email=email,
                success=False,
                reason="Invalid password",
                ip_address=ip_address,
                user_id=user.id
            )
            raise ValueError("Invalid email or password")

        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()

        # Generate session token (FR-011)
        session_token = self.jwt_service.generate_session_token(
            user_id=user.id,
            email=user.email
        )

        # Create session record
        session = Session(
            user_id=user.id,
            token=session_token
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        # Log successful login
        self.security_logger.log_login_attempt(
            email=user.email,
            success=True,
            ip_address=ip_address,
            user_id=user.id
        )

        return {
            "session_token": session_token,
            "expires_at": session.expires_at.isoformat() + "Z",
            "user": {
                "id": user.id,
                "email": user.email,
                "email_verified": user.email_verified
            }
        }

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email address

        Returns:
            User or None
        """
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User or None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    async def request_password_reset(self, email: str, base_url: str = "http://localhost:8000") -> dict:
        """
        Request password reset and send reset email.

        Args:
            email: User email address
            base_url: Application base URL for reset link

        Returns:
            dict: Status message (generic for security)

        Requirements: FR-014
        """
        email = email.lower()

        # Find user
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Don't reveal if email exists (security)
            self.security_logger.log_password_reset_request(email=email)
            return {"message": "If the email exists, a password reset link has been sent."}

        # Generate reset token
        token = self.token_service.generate_token()
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token
        )
        self.db.add(reset_token)
        self.db.commit()

        # Send reset email
        await self.email_service.send_password_reset_email(
            to=user.email,
            token=token,
            base_url=base_url
        )

        # Log request
        self.security_logger.log_password_reset_request(
            email=user.email
        )

        return {"message": "If the email exists, a password reset link has been sent."}

    async def reset_password(self, token: str, new_password: str) -> dict:
        """
        Reset user password using reset token.

        Args:
            token: Password reset token
            new_password: New password (plain text)

        Returns:
            dict: Success message

        Raises:
            ValueError: If token is invalid, expired, or used

        Requirements: FR-015
        """
        # Find token
        reset_token = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()

        if not reset_token:
            raise ValueError("Invalid password reset token")

        # Check if already used
        if reset_token.is_used:
            raise ValueError("Password reset token already used")

        # Check if expired
        if reset_token.is_expired():
            raise ValueError("Password reset token has expired")

        # Validate new password strength
        if not self.password_service.validate_strength(new_password):
            raise ValueError("Password does not meet security requirements")

        # Get user
        user = self.db.query(User).filter(User.id == reset_token.user_id).first()
        if not user:
            raise ValueError("User not found")

        # Hash new password
        new_password_hash = self.password_service.hash_password(new_password)

        # Update user password
        user.password_hash = new_password_hash

        # Mark token as used
        reset_token.is_used = True
        reset_token.used_at = datetime.utcnow()

        # Invalidate all existing sessions for security
        from src.models.session import Session
        self.db.query(Session).filter(Session.user_id == user.id).update(
            {"is_active": False}
        )

        self.db.commit()

        # Log successful password reset
        self.security_logger.log_password_reset_success(
            user_id=user.id,
            email=user.email
        )

        return {"message": "Password reset successful. Please log in with your new password."}
