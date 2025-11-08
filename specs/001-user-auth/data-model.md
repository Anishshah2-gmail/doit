# Data Model: User Authentication

**Feature**: User Authentication with Email and Password
**Date**: 2025-11-08
**Purpose**: Define data entities, relationships, and validation rules

## Overview

This document defines the four core entities required for user authentication: User, Session, VerificationToken, and PasswordResetToken. All entities are designed for SQLAlchemy ORM with PostgreSQL in production and SQLite for development/testing.

---

## Entity 1: User

### Purpose
Represents a registered user account with authentication credentials and metadata.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique user identifier |
| `email` | String(255) | Unique, Not Null, Index | User's email address (login identifier) |
| `password_hash` | String(255) | Not Null | Argon2 hashed password (never store plain text) |
| `email_verified` | Boolean | Default: False, Not Null | Email verification status |
| `is_active` | Boolean | Default: True, Not Null | Account active status (for soft deletes/bans) |
| `is_locked` | Boolean | Default: False, Not Null | Account lockout status (after failed logins) |
| `locked_until` | DateTime | Nullable | Auto-unlock timestamp (30 min after lockout) |
| `failed_login_attempts` | Integer | Default: 0, Not Null | Counter for failed login attempts |
| `last_failed_login` | DateTime | Nullable | Timestamp of most recent failed login |
| `created_at` | DateTime | Auto-generated, Not Null | Account creation timestamp (UTC) |
| `updated_at` | DateTime | Auto-updated, Not Null | Last modification timestamp (UTC) |
| `last_login_at` | DateTime | Nullable | Most recent successful login timestamp |

### Indexes
- `idx_user_email` on `email` (unique) - Fast login lookups
- `idx_user_locked` on `is_locked`, `locked_until` - Efficient lockout queries

### Validation Rules

**Email** (FR-002):
- Must match RFC 5322 format
- Case-insensitive storage (normalize to lowercase)
- Maximum length: 255 characters
- Cannot be changed after registration (for MVP)

**Password** (FR-003):
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*()-_=+[]{};:,.<>?/)
- Maximum length: 128 characters (before hashing)
- Hashed using Argon2id with Passlib

**Account Lockout Logic** (FR-009, FR-010):
- After 5 failed login attempts within 15 minutes → set `is_locked=True`, `locked_until=now+30min`
- Failed attempts counter reset on successful login
- Auto-unlock when `now > locked_until`

### State Transitions

```
[New User Created]
  ↓
[email_verified=False, is_active=True, is_locked=False]
  ↓ (User clicks verification link)
[email_verified=True] → Can now log in
  ↓ (5 failed logins in 15 min)
[is_locked=True, locked_until=+30min]
  ↓ (Wait 30 minutes OR admin intervention)
[is_locked=False] → Can attempt login again
```

### Relationships
- **One-to-Many** with Session (one user can have multiple active sessions)
- **One-to-Many** with VerificationToken (one user can request multiple verification emails)
- **One-to-Many** with PasswordResetToken (one user can request multiple password resets)

### Example SQLAlchemy Model

```python
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

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

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    verification_tokens = relationship("VerificationToken", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_locked', 'is_locked', 'locked_until'),
    )
```

---

## Entity 2: Session

### Purpose
Represents an authenticated user session after successful login.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique session identifier |
| `user_id` | UUID | Foreign Key (users.id), Not Null, Index | Associated user |
| `session_token` | String(255) | Unique, Not Null, Index | JWT or secure random token |
| `created_at` | DateTime | Auto-generated, Not Null | Session creation timestamp (UTC) |
| `expires_at` | DateTime | Not Null | Session expiration timestamp (created_at + 24 hours) |
| `is_active` | Boolean | Default: True, Not Null | Session validity status |
| `ip_address` | String(45) | Nullable | Client IP address (IPv4/IPv6) |
| `user_agent` | String(255) | Nullable | Client browser/device info |

### Indexes
- `idx_session_token` on `session_token` (unique) - Fast session lookups
- `idx_session_user` on `user_id` - User's sessions queries
- `idx_session_expires` on `expires_at`, `is_active` - Cleanup expired sessions

### Validation Rules

**Session Token**:
- JWT with HS256 signature (using secret key from environment)
- Payload: `{user_id, email, exp, iat}`
- Alternative: Secure random 128-char string (if not using JWT)

**Expiration** (FR-020):
- Default: 24 hours from creation
- Extended by user activity (optional for future enhancement)
- Cleanup job to delete expired sessions daily

**Invalidation** (FR-014):
- When user changes password → set all user's sessions `is_active=False`
- When user logs out → set specific session `is_active=False`

### State Transitions

```
[Session Created on Login]
  ↓
[is_active=True, expires_at=+24h]
  ↓ (User logs out)
[is_active=False] → Cannot be reused
  ↓ (24 hours pass)
[expires_at < now] → Cleanup job deletes
```

### Relationships
- **Many-to-One** with User (many sessions belong to one user)

### Example SQLAlchemy Model

```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index('idx_session_expires', 'expires_at', 'is_active'),
    )
```

---

## Entity 3: VerificationToken

### Purpose
Represents an email verification token sent to users after registration.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique token identifier |
| `user_id` | UUID | Foreign Key (users.id), Not Null, Index | Associated user |
| `token` | String(255) | Unique, Not Null, Index | Secure random verification token |
| `created_at` | DateTime | Auto-generated, Not Null | Token creation timestamp (UTC) |
| `expires_at` | DateTime | Not Null | Token expiration (created_at + 24 hours) |
| `is_used` | Boolean | Default: False, Not Null | Token usage status |
| `used_at` | DateTime | Nullable | When token was used (if applicable) |

### Indexes
- `idx_verification_token` on `token` (unique) - Fast token lookups
- `idx_verification_user` on `user_id` - User's tokens queries
- `idx_verification_expires` on `expires_at`, `is_used` - Cleanup expired tokens

### Validation Rules

**Token Generation**:
- Secure random 64-character hexadecimal string (using `secrets` module)
- URL-safe (no special characters)
- One-time use only (set `is_used=True` after verification)

**Expiration**:
- Valid for 24 hours after creation
- Expired tokens cannot be used (even if not marked as used)
- User can request new verification email (generates new token)

**Email Content**:
- Verification link format: `https://example.com/verify-email?token={token}`
- Include user's email in email for context
- Clear expiration notice (24 hours)

### State Transitions

```
[Token Created on Registration]
  ↓
[is_used=False, expires_at=+24h]
  ↓ (User clicks link within 24h)
[is_used=True, used_at=now] → User.email_verified=True
  ↓ (24 hours pass without use)
[expires_at < now] → Cannot be used, cleanup job deletes
```

### Relationships
- **Many-to-One** with User (many tokens can belong to one user)

### Example SQLAlchemy Model

```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta

class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="verification_tokens")

    __table_args__ = (
        Index('idx_verification_expires', 'expires_at', 'is_used'),
    )
```

---

## Entity 4: PasswordResetToken

### Purpose
Represents a password reset token sent to users who forgot their password.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique token identifier |
| `user_id` | UUID | Foreign Key (users.id), Not Null, Index | Associated user |
| `token` | String(255) | Unique, Not Null, Index | Secure random reset token |
| `created_at` | DateTime | Auto-generated, Not Null | Token creation timestamp (UTC) |
| `expires_at` | DateTime | Not Null | Token expiration (created_at + 1 hour) |
| `is_used` | Boolean | Default: False, Not Null | Token usage status |
| `used_at` | DateTime | Nullable | When token was used (if applicable) |

### Indexes
- `idx_reset_token` on `token` (unique) - Fast token lookups
- `idx_reset_user` on `user_id` - User's tokens queries
- `idx_reset_expires` on `expires_at`, `is_used` - Cleanup expired tokens

### Validation Rules

**Token Generation** (FR-012):
- Secure random 64-character hexadecimal string (using `secrets` module)
- URL-safe (no special characters)
- One-time use only (set `is_used=True` after password reset)

**Expiration** (FR-012, SC-008):
- Valid for exactly 1 hour after creation (stricter than verification tokens)
- Expired tokens cannot be used
- Multiple active tokens allowed (user can request multiple resets)

**Security** (FR-019):
- When non-existent email requests reset → show generic success message
- Don't reveal whether email exists in system
- Log all reset requests for security audit

**Email Content**:
- Reset link format: `https://example.com/reset-password?token={token}`
- Clear expiration notice (1 hour)
- Security warning (didn't request this? contact support)

### State Transitions

```
[Token Created on Reset Request]
  ↓
[is_used=False, expires_at=+1h]
  ↓ (User clicks link within 1h and sets new password)
[is_used=True, used_at=now] → User.password_hash updated, all sessions invalidated
  ↓ (1 hour passes without use)
[expires_at < now] → Cannot be used, cleanup job deletes
```

### Relationships
- **Many-to-One** with User (many tokens can belong to one user)

### Example SQLAlchemy Model

```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")

    __table_args__ = (
        Index('idx_reset_expires', 'expires_at', 'is_used'),
    )
```

---

## Entity Relationships Diagram

```
┌──────────────┐
│     User     │
│ (id, email,  │
│  password)   │
└──────┬───────┘
       │
       │ 1:N
       ├─────────────┬────────────────┬─────────────────┐
       │             │                │                 │
       ▼             ▼                ▼                 ▼
┌────────────┐  ┌──────────────────┐ ┌──────────────────┐
│  Session   │  │ VerificationToken│ │PasswordResetToken│
│ (token,    │  │ (token, exp)     │ │ (token, exp)     │
│  expires)  │  └──────────────────┘ └──────────────────┘
└────────────┘
```

## Database Migrations Plan

Using Alembic for schema migrations:

1. **Migration 001**: Create users table
2. **Migration 002**: Create sessions table with foreign key to users
3. **Migration 003**: Create verification_tokens table with foreign key to users
4. **Migration 004**: Create password_reset_tokens table with foreign key to users

Each migration should include:
- UP: CREATE TABLE with all columns, constraints, indexes
- DOWN: DROP TABLE (rollback)
- Data migrations (if needed for production data)

---

## Security Considerations

1. **Password Storage**: Never store plain-text passwords, always hash with Argon2
2. **Token Generation**: Use `secrets.token_urlsafe()` for cryptographically secure tokens
3. **Email Enumeration**: Don't reveal whether email exists during password reset (FR-019)
4. **SQL Injection**: SQLAlchemy ORM provides protection via parameterized queries
5. **Timing Attacks**: Use constant-time comparison for token validation
6. **Cleanup Jobs**: Regularly delete expired tokens and sessions to prevent database bloat

---

## Performance Considerations

1. **Indexes**: All foreign keys and frequently queried columns have indexes
2. **Token Lookups**: O(1) via unique index on token columns
3. **Session Validation**: Fast lookup via indexed session_token
4. **Lockout Queries**: Compound index on (is_locked, locked_until) for efficient lockout checks
5. **Pagination**: For admin views of users/sessions, implement offset/limit queries

---

## Testing Data Model

### Unit Tests Required
- User model validation (email format, password strength)
- Token generation uniqueness
- Relationship integrity (cascade deletes)
- State transitions (lockout, expiration)

### Test Fixtures
- Valid user with verified email
- Locked user account
- Expired verification token
- Expired password reset token
- Active session
- Expired session

---

## Next Steps

1. Generate Alembic migrations for all four entities
2. Create Pydantic schemas for API request/response validation
3. Define API contracts in OpenAPI format (see contracts/ directory)
4. Implement repository pattern for database operations (if needed)
