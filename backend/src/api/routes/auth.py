"""
Authentication API routes.
Handles user registration, email verification, and login endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query, Header
from sqlalchemy.orm import Session
from src.api.schemas import (
    RegisterRequest,
    RegisterResponse,
    VerifyEmailResponse,
    ResendVerificationRequest,
    LoginRequest,
    LoginResponse,
    PasswordResetRequestSchema,
    PasswordResetSchema,
    MessageResponse,
    ErrorResponse
)
from src.services.auth_service import AuthService
from src.lib.database import get_db


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Email already registered"}
    }
)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register new user with email and password.

    Creates a new user account and sends email verification link.

    **User Story**: P1 - New User Registration

    **Requirements**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006

    **Process**:
    1. Validates email format (RFC 5322)
    2. Validates password strength (8+ chars, upper, lower, digit, special)
    3. Checks for duplicate email
    4. Hashes password with Argon2
    5. Creates user account (unverified)
    6. Generates verification token (24h expiry)
    7. Sends verification email

    **Returns**:
    - 201: User created, verification email sent
    - 400: Invalid email or weak password
    - 409: Email already registered
    """
    auth_service = AuthService(db)

    try:
        user = await auth_service.register_user(
            email=request.email,
            password=request.password
        )

        return RegisterResponse(
            message="Registration successful. Please check your email to verify your account.",
            user_id=user.id,
            email=user.email
        )
    except ValueError as e:
        error_msg = str(e)
        if "already registered" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )


@router.get(
    "/verify-email",
    response_model=VerifyEmailResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired token"}
    }
)
async def verify_email(
    token: str = Query(..., description="Email verification token from email link"),
    db: Session = Depends(get_db)
):
    """
    Verify user email address.

    Verifies email using token from verification email.

    **User Story**: P1 - New User Registration (verification step)

    **Requirements**: FR-005, FR-017

    **Process**:
    1. Validates token exists and not used
    2. Checks token not expired (24h limit)
    3. Marks token as used
    4. Sets user.email_verified = True
    5. User can now log in

    **Returns**:
    - 200: Email verified successfully
    - 400: Invalid, expired, or already used token
    """
    auth_service = AuthService(db)

    try:
        await auth_service.verify_email(token)
        return VerifyEmailResponse(
            message="Email verified successfully. You can now log in."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    responses={
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend verification email.

    Sends a new verification email to user (if email not already verified).

    **User Story**: P1 - New User Registration

    **Requirements**: FR-005

    **Security**: Generic response (doesn't reveal if email exists)

    **Process**:
    1. Checks if user exists (but doesn't reveal in response)
    2. If user exists and not verified, generates new token
    3. Sends new verification email
    4. Returns generic success message regardless

    **Returns**:
    - 200: Generic success message (security measure)
    - 429: Too many requests (rate limiting)
    """
    auth_service = AuthService(db)

    try:
        result = await auth_service.resend_verification(request.email)
        return MessageResponse(message=result["message"])
    except Exception as e:
        # Generic error to not reveal information
        return MessageResponse(
            message="If the email exists and is not verified, a new verification email has been sent."
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials or email not verified"},
        401: {"model": ErrorResponse, "description": "Authentication failed"},
        403: {"model": ErrorResponse, "description": "Account locked"}
    }
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and create session.

    Authenticates user with email and password, creates session token.

    **User Story**: P1 - Existing User Login

    **Requirements**: FR-007, FR-008, FR-009, FR-010, FR-011

    **Process**:
    1. Validates email and password
    2. Checks email is verified
    3. Checks account not locked
    4. Verifies password with Argon2
    5. Increments failed attempts on wrong password
    6. Locks account after 5 failed attempts (30min lockout)
    7. Creates session with JWT token
    8. Returns session token (24h expiry)

    **Returns**:
    - 200: Login successful, session token returned
    - 400: Invalid credentials
    - 401: Email not verified
    - 403: Account locked (too many failed attempts)
    """
    auth_service = AuthService(db)

    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password
        )

        return LoginResponse(
            message="Login successful",
            session_token=result["session_token"],
            expires_at=result["expires_at"],
            user=result["user"]
        )
    except ValueError as e:
        error_msg = str(e)

        # Determine appropriate status code
        if "locked" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
        elif "verify your email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )


@router.post(
    "/password/reset-request",
    response_model=MessageResponse
)
async def request_password_reset(
    request: PasswordResetRequestSchema,
    db: Session = Depends(get_db)
):
    """
    Request password reset link.

    Sends password reset email with token (if email exists).

    **User Story**: P2 - Password Reset

    **Requirements**: FR-014

    **Security**: Returns generic message (doesn't reveal if email exists)

    **Returns**:
    - 200: Generic success message
    """
    auth_service = AuthService(db)
    result = await auth_service.request_password_reset(request.email)
    return MessageResponse(message=result["message"])


@router.post(
    "/password/reset",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired token"}
    }
)
async def reset_password(
    request: PasswordResetSchema,
    db: Session = Depends(get_db)
):
    """
    Reset password using token.

    Resets password using token from reset email.

    **User Story**: P2 - Password Reset

    **Requirements**: FR-015

    **Process**:
    1. Validates token exists and not used
    2. Checks token not expired (1h limit)
    3. Validates new password strength
    4. Updates password with Argon2 hash
    5. Marks token as used
    6. Invalidates all existing sessions

    **Returns**:
    - 200: Password reset successful
    - 400: Invalid, expired, or used token
    """
    auth_service = AuthService(db)

    try:
        result = await auth_service.reset_password(
            token=request.token,
            new_password=request.new_password
        )
        return MessageResponse(message=result["message"])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/logout",
    response_model=MessageResponse
)
async def logout(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Logout user by deactivating session.

    Deactivates the current user session.

    **User Story**: P3 - Logout

    **Requirements**: FR-016

    **Process**:
    1. Extracts session token from Authorization header
    2. Finds and deactivates the session
    3. Logs logout event

    **Returns**:
    - 200: Logout successful
    - 401: Invalid or inactive session
    """
    auth_service = AuthService(db)

    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    session_token = authorization.replace("Bearer ", "")

    try:
        result = auth_service.logout(session_token)
        return MessageResponse(message=result["message"])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
