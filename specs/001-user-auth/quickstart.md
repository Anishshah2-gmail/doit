# Quick Start: User Authentication Implementation

**Feature**: User Authentication with Email and Password
**Branch**: `001-user-auth`
**Updated**: 2025-11-08
**Target Audience**: Developers implementing this feature

## Overview

This guide walks you through implementing the user authentication system from scratch using Test-Driven Development (TDD). Follow the steps in order to build a secure authentication API compliant with the project's constitution.

**Time Estimate**: 8-12 hours for full implementation (P1-P4 user stories)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] PostgreSQL installed and running (for production mode)
- [ ] Git repository cloned and on branch `001-user-auth`
- [ ] Read `spec.md` (understand user stories and requirements)
- [ ] Read `data-model.md` (understand entities and relationships)
- [ ] Read `research.md` (understand technology choices)
- [ ] Reviewed `contracts/auth-api.yaml` (understand API endpoints)

---

## Phase 1: Project Setup (30 minutes)

### Step 1.1: Create Project Structure

```bash
# From repository root
mkdir -p backend/src/{models,services,api/routes,api/middleware,lib}
mkdir -p backend/tests/{unit,integration,contract}
mkdir -p config
mkdir -p docs/api

# Create __init__.py files for Python packages
touch backend/src/__init__.py
touch backend/src/models/__init__.py
touch backend/src/services/__init__.py
touch backend/src/api/__init__.py
touch backend/src/api/routes/__init__.py
touch backend/src/api/middleware/__init__.py
touch backend/src/lib/__init__.py
touch backend/tests/__init__.py
```

### Step 1.2: Install Dependencies

Create `backend/requirements.txt`:

```text
# Web Framework
fastapi[all]>=0.100.0
uvicorn[standard]>=0.23.0

# Database
sqlalchemy>=2.0.0
alembic>=1.11.0
psycopg2-binary>=2.9.0

# Security
passlib[argon2]>=1.7.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6
email-validator>=2.0.0

# Email
aiosmtplib>=2.0.0

# Configuration
python-dotenv>=1.0.0
```

Create `backend/requirements-dev.txt`:

```text
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.24.0
faker>=19.0.0

# Code Quality
black>=23.0.0
flake8>=6.0.0
mypy>=1.4.0
```

Install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Step 1.3: Configure Environment Variables

Create `config/.env.example`:

```env
# Application
APP_NAME=MyApp
ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp_auth
DATABASE_URL_TEST=sqlite:///./test.db

# SMTP Email Configuration
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your-mailtrap-user
SMTP_PASSWORD=your-mailtrap-password
FROM_EMAIL=noreply@myapp.com
FROM_NAME=MyApp

# Security
ARGON2_TIME_COST=2
ARGON2_MEMORY_COST=65536
ARGON2_PARALLELISM=1

# Session
SESSION_EXPIRY_HOURS=24

# Tokens
VERIFICATION_TOKEN_EXPIRY_HOURS=24
RESET_TOKEN_EXPIRY_HOURS=1

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
LOCKOUT_WINDOW_MINUTES=15
```

Copy to actual config:

```bash
cp config/.env.example config/.env
# Edit config/.env with actual values
```

### Step 1.4: Initialize Alembic (Database Migrations)

```bash
cd backend
alembic init alembic

# Edit alembic.ini - set sqlalchemy.url to use environment variable
# sqlalchemy.url = postgresql://user:password@localhost:5432/myapp_auth

# Edit alembic/env.py to load models and env variables
```

---

## Phase 2: Data Models (TDD - 1 hour)

**Remember**: Write tests FIRST, see them FAIL, then implement.

### Step 2.1: Write User Model Tests

Create `backend/tests/unit/test_user_model.py`:

```python
import pytest
from datetime import datetime, timedelta
from src.models.user import User

def test_user_creation():
    """Test User model instantiation"""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    assert user.email == "test@example.com"
    assert user.email_verified == False
    assert user.is_active == True
    assert user.is_locked == False
    assert user.failed_login_attempts == 0

def test_user_email_normalization():
    """Test email is stored in lowercase"""
    user = User(email="Test@Example.COM")
    assert user.email == "test@example.com"

def test_user_lockout():
    """Test account lockout after failed attempts"""
    user = User(email="test@example.com")
    user.failed_login_attempts = 5
    user.is_locked = True
    user.locked_until = datetime.utcnow() + timedelta(minutes=30)

    assert user.is_locked == True
    assert user.locked_until > datetime.utcnow()

# Add more tests based on data-model.md
```

Run tests (they should FAIL):

```bash
pytest backend/tests/unit/test_user_model.py
# Expected: ImportError or test failures
```

### Step 2.2: Implement User Model

Create `backend/src/models/user.py`:

```python
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships (add as you create other models)
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_locked', 'is_locked', 'locked_until'),
    )

    def __init__(self, email: str, password_hash: str = None, **kwargs):
        # Normalize email to lowercase
        super().__init__(email=email.lower(), password_hash=password_hash, **kwargs)
```

Run tests again (they should PASS):

```bash
pytest backend/tests/unit/test_user_model.py -v
# Expected: All tests pass
```

### Step 2.3: Repeat for Other Models

Follow same TDD process for:
- Session model (`test_session_model.py` → `src/models/session.py`)
- VerificationToken model (`test_verification_token_model.py` → `src/models/verification_token.py`)
- PasswordResetToken model (`test_password_reset_token_model.py` → `src/models/password_reset_token.py`)

Refer to `data-model.md` for complete model specifications.

---

## Phase 3: Core Services (TDD - 2 hours)

### Step 3.1: Password Service (TDD)

**Test first:**

Create `backend/tests/unit/test_password_service.py`:

```python
import pytest
from src.services.password_service import PasswordService

def test_hash_password():
    """Test password hashing with Argon2"""
    service = PasswordService()
    password = "SecurePass123!"
    hashed = service.hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")

def test_verify_password():
    """Test password verification"""
    service = PasswordService()
    password = "SecurePass123!"
    hashed = service.hash_password(password)

    assert service.verify_password(password, hashed) == True
    assert service.verify_password("WrongPass", hashed) == False

def test_validate_password_strength():
    """Test password strength validation (FR-003)"""
    service = PasswordService()

    # Valid passwords
    assert service.validate_strength("SecurePass123!") == True

    # Invalid: too short
    assert service.validate_strength("Short1!") == False

    # Invalid: no uppercase
    assert service.validate_strength("securepass123!") == False

    # Invalid: no lowercase
    assert service.validate_strength("SECUREPASS123!") == False

    # Invalid: no digit
    assert service.validate_strength("SecurePass!") == False

    # Invalid: no special char
    assert service.validate_strength("SecurePass123") == False
```

Run tests (FAIL):

```bash
pytest backend/tests/unit/test_password_service.py
```

**Then implement:**

Create `backend/src/services/password_service.py`:

```python
from passlib.hash import argon2
import re

class PasswordService:
    """Password hashing and validation service using Argon2"""

    def hash_password(self, password: str) -> str:
        """Hash password using Argon2id"""
        return argon2.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return argon2.verify(plain_password, hashed_password)
        except:
            return False

    def validate_strength(self, password: str) -> bool:
        """
        Validate password meets security requirements (FR-003):
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
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
```

Run tests (PASS):

```bash
pytest backend/tests/unit/test_password_service.py -v
```

### Step 3.2: Email Validation Service

Follow same TDD pattern for email validation (`src/lib/validators.py`).

### Step 3.3: Token Service

Implement token generation for verification and reset tokens.

### Step 3.4: Auth Service

Implement core auth logic (register, login, logout) using TDD.

---

## Phase 4: API Endpoints (TDD - 3 hours)

### Step 4.1: Registration Endpoint (User Story P1)

**Integration test first:**

Create `backend/tests/integration/test_registration.py`:

```python
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration (FR-001)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "user_id" in data
    assert "verification" in data["message"].lower()

@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with existing email (FR-006)"""
    # Create user first
    # Then try to register again with same email
    # Assert 409 Conflict

@pytest.mark.asyncio
async def test_register_weak_password():
    """Test registration with weak password (FR-003)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/v1/auth/register", json={
            "email": "test@example.com",
            "password": "weak"
        })

    assert response.status_code == 400
    assert "password" in response.json()["message"].lower()
```

**Then implement:**

Create `backend/src/api/routes/auth.py`:

```python
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from src.services.auth_service import AuthService
from src.lib.validators import validate_password_strength

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    message: str
    user_id: str
    email: str

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register new user (User Story P1)

    Requirements: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006
    """
    # Validate password strength (FR-003)
    if not validate_password_strength(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )

    # Call auth service to create user
    auth_service = AuthService(db)
    try:
        user = await auth_service.register_user(request.email, request.password)
        return RegisterResponse(
            message="Registration successful. Please check your email to verify your account.",
            user_id=str(user.id),
            email=user.email
        )
    except ValueError as e:
        # Duplicate email (FR-006)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
```

Repeat for all endpoints in `contracts/auth-api.yaml`.

---

## Phase 5: Testing & Validation (1 hour)

### Step 5.1: Run All Tests

```bash
# Unit tests
pytest backend/tests/unit/ -v

# Integration tests
pytest backend/tests/integration/ -v

# Contract tests
pytest backend/tests/contract/ -v

# Coverage report
pytest backend/tests/ --cov=backend/src --cov-report=html
# Open htmlcov/index.html to see coverage
# Ensure >=80% coverage (constitutional requirement)
```

### Step 5.2: Lint and Format

```bash
# Format code
black backend/src backend/tests

# Check style
flake8 backend/src backend/tests

# Type checking
mypy backend/src
```

---

## Phase 6: Manual Testing (30 minutes)

### Step 6.1: Run Development Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### Step 6.2: Test with API Documentation

Visit `http://localhost:8000/docs` (FastAPI auto-generated Swagger UI)

### Step 6.3: Test User Flows

1. **Register new user**:
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

2. **Check email** (Mailtrap or configured SMTP)

3. **Verify email** (click link or GET request)

4. **Login**:
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

5. **Test password reset flow**

6. **Test logout**

---

## Phase 7: Documentation (30 minutes)

### Step 7.1: Add Docstrings

Ensure all public functions have docstrings:

```python
def register_user(email: str, password: str) -> User:
    """
    Register a new user with email and password.

    Args:
        email: User email address (unique identifier)
        password: Plain text password (will be hashed)

    Returns:
        User: Created user object with email_verified=False

    Raises:
        ValueError: If email already exists or validation fails

    Requirements: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006
    """
```

### Step 7.2: Update API Documentation

Create `docs/api/authentication.md` with:
- API endpoints overview
- Authentication flow diagrams
- Example requests/responses
- Error codes reference

---

## Phase 8: Commit & Push (15 minutes)

### Step 8.1: Review Changes

```bash
git status
git diff
```

### Step 8.2: Run Pre-commit Checks

```bash
# All tests pass
pytest backend/tests/ -v

# Code quality
black --check backend/src backend/tests
flake8 backend/src backend/tests

# Coverage meets requirement
pytest backend/tests/ --cov=backend/src --cov-report=term
# Ensure >= 80%
```

### Step 8.3: Commit

```bash
git add backend/ config/ docs/
git commit -m "feat: implement user authentication with email/password

Implements P1-P4 user stories:
- User registration with email verification
- User login with session management
- Password reset flow
- User logout

Features:
- Argon2 password hashing
- Account lockout after 5 failed attempts
- JWT session tokens (24h expiry)
- Email verification (24h token)
- Password reset (1h token)
- OWASP security compliance

Testing:
- 80%+ code coverage
- Unit, integration, and contract tests
- All acceptance scenarios validated

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 8.4: Push to Remote

```bash
git push origin 001-user-auth
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Create database
createdb myapp_auth

# Run migrations
alembic upgrade head
```

### Email Not Sending

- Check SMTP credentials in `.env`
- Use Mailtrap for testing (free tier: https://mailtrap.io/)
- Check email service logs

### Tests Failing

```bash
# Run specific test with verbose output
pytest backend/tests/unit/test_password_service.py::test_hash_password -vv

# Check test database
pytest backend/tests/ --verbose --capture=no
```

---

## Next Steps

After implementation complete:

1. Create pull request from `001-user-auth` to `main`
2. Run `/speckit.tasks` to generate detailed task breakdown (if not done)
3. Proceed to code review (constitutional requirement)
4. Deploy to staging environment for manual QA
5. Update documentation with deployment instructions

---

## Reference Documents

- **Specification**: `spec.md` - User stories and requirements
- **Technical Decisions**: `research.md` - Framework and database choices
- **Data Models**: `data-model.md` - Entity schemas and relationships
- **API Contracts**: `contracts/auth-api.yaml` - OpenAPI specification
- **Implementation Plan**: `plan.md` - Architecture and structure
- **Constitution**: `.specify/memory/constitution.md` - Project principles

---

## Need Help?

- **API Documentation**: http://localhost:8000/docs (when server running)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Passlib Docs**: https://passlib.readthedocs.io/
- **pytest Docs**: https://docs.pytest.org/

---

**Remember**: Follow TDD strictly. Write tests first, see them fail, then implement. This is a NON-NEGOTIABLE constitutional requirement.
