"""
Pydantic schemas for API request/response validation.
Provides automatic validation and serialization for FastAPI endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Registration schemas
class RegisterRequest(BaseModel):
    """Registration request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class RegisterResponse(BaseModel):
    """Registration response schema"""
    message: str
    user_id: str
    email: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Registration successful. Please check your email to verify your account.",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com"
            }
        }


# Email verification schemas
class VerifyEmailResponse(BaseModel):
    """Email verification response schema"""
    message: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Email verified successfully. You can now log in."
            }
        }


class ResendVerificationRequest(BaseModel):
    """Resend verification email request schema"""
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


# Login schemas
class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class UserInfo(BaseModel):
    """User information schema"""
    id: str
    email: str
    email_verified: bool

    class Config:
        orm_mode = True


class LoginResponse(BaseModel):
    """Login response schema"""
    message: str
    session_token: str
    expires_at: str
    user: UserInfo

    class Config:
        schema_extra = {
            "example": {
                "message": "Login successful",
                "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_at": "2025-11-09T01:35:00Z",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "email_verified": True
                }
            }
        }


# Password reset schemas
class PasswordResetRequestSchema(BaseModel):
    """Password reset request schema"""
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetSchema(BaseModel):
    """Password reset with token schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    class Config:
        schema_extra = {
            "example": {
                "token": "7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a",
                "new_password": "NewSecurePass456!"
            }
        }


# Generic response schemas
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[list] = None
