"""
Input validation utilities for email and other fields.
"""
import re
from email_validator import validate_email as email_validate, EmailNotValidError


def validate_email(email: str, normalize: bool = False, check_deliverability: bool = False):
    """
    Validate email address format per RFC 5322.

    Args:
        email: Email address to validate
        normalize: If True, return normalized (lowercase) email
        check_deliverability: If True, check DNS for email deliverability

    Returns:
        bool: True if valid, False if invalid
        str: Normalized email if normalize=True

    Requirements: FR-002 (email validation)
    """
    try:
        validation = email_validate(email, check_deliverability=check_deliverability)
        if normalize:
            return validation.email.lower()
        return True
    except EmailNotValidError:
        return False
