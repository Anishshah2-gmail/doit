"""
Token generation service for verification and password reset tokens.
Uses cryptographically secure random generation.
"""
import secrets


class TokenService:
    """Service for generating secure random tokens"""

    def generate_token(self, num_bytes: int = 32) -> str:
        """
        Generate a cryptographically secure random token.

        Args:
            num_bytes: Number of random bytes (default: 32 = 64 hex chars)

        Returns:
            str: Hexadecimal token string (URL-safe)

        Requirements: FR-005 (verification tokens), FR-012 (reset tokens)
        """
        return secrets.token_hex(num_bytes)
