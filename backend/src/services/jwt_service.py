"""
JWT Service for session token generation and verification.
Handles encoding and decoding of JWT tokens for user sessions.
"""
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from src.config import settings


class JWTService:
    """
    Service for JWT token operations.

    Handles:
    - Session token generation (FR-011)
    - Token verification (FR-012)
    - Token expiry management (FR-013)
    """

    def __init__(self):
        """Initialize JWTService with algorithm and secret key"""
        self.algorithm = "HS256"
        self.secret_key = settings.SECRET_KEY

    def generate_session_token(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Generate JWT session token for user.

        Args:
            user_id: User ID to encode in token
            email: User email to encode in token
            expires_delta: Custom expiry duration (defaults to SESSION_EXPIRY_HOURS)

        Returns:
            str: Encoded JWT token

        Requirements: FR-011
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.SESSION_EXPIRY_HOURS)

        # Create token payload
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "email": email,
            "iat": now,  # Issued at
            "exp": now + expires_delta  # Expiration
        }

        # Encode token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Dict with token payload if valid, None if invalid or expired

        Requirements: FR-012
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            # Token is invalid or expired
            return None

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """
        Get expiry time from token.

        Args:
            token: JWT token

        Returns:
            datetime: Expiry time if valid token, None otherwise
        """
        payload = self.verify_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None
