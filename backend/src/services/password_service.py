"""
Password hashing and validation service using Argon2.
Implements secure password storage per FR-004 and validation per FR-003.
"""
from passlib.hash import argon2
import re


class PasswordService:
    """Password hashing and validation service using Argon2"""

    def hash_password(self, password: str) -> str:
        """
        Hash password using Argon2id algorithm.

        Args:
            password: Plain text password to hash

        Returns:
            str: Hashed password with Argon2 format

        Requirements: FR-004 (secure password storage)
        """
        return argon2.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify plain password against hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Argon2 hashed password

        Returns:
            bool: True if password matches, False otherwise

        Requirements: FR-007 (login authentication)
        """
        try:
            return argon2.verify(plain_password, hashed_password)
        except Exception:
            return False

    def validate_strength(self, password: str) -> bool:
        """
        Validate password meets security requirements.

        Password requirements (FR-003):
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            password: Password to validate

        Returns:
            bool: True if password meets all requirements, False otherwise

        Requirements: FR-003 (password strength requirements)
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:,.<>?/]', password):
            return False
        return True
