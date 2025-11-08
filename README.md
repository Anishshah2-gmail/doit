# DoIt - Secure Authentication System

A production-ready Python backend authentication system built with FastAPI, featuring comprehensive user account management, email verification, password reset, and session handling with enterprise-grade security.

## Features

- **User Registration** - Secure account creation with email verification
- **Email Verification** - Required email confirmation with expiring tokens (24-hour validity)
- **User Login** - Session-based authentication with JWT tokens
- **Password Reset** - Secure password recovery flow with single-use tokens
- **Session Management** - 24-hour session expiry with automatic cleanup
- **Account Security** - Lockout mechanism after 5 failed login attempts
- **Security Logging** - Comprehensive audit trail for all authentication events
- **Password Security** - Argon2 hashing with configurable strength parameters

## Technology Stack

### Core Framework
- **FastAPI 0.100+** - Modern async web framework
- **Uvicorn 0.23+** - ASGI web server
- **Python 3.11+** - Required Python version

### Database & ORM
- **SQLAlchemy 2.0+** - SQL toolkit and ORM
- **Alembic 1.11+** - Database migrations
- **PostgreSQL/SQLite** - Database options

### Security
- **Passlib (Argon2)** - Secure password hashing
- **python-jose** - JWT token handling
- **email-validator** - RFC 5322 email validation

### Email
- **aiosmtplib 2.0+** - Async email delivery

### Testing & Quality
- **pytest 7.4+** - Testing framework with async support
- **pytest-cov** - Code coverage reporting
- **black** - Code formatter
- **ruff** - Fast Python linter
- **mypy** - Static type checker

## Project Structure

```
doit/
├── backend/
│   ├── src/
│   │   ├── api/              # API routes and schemas
│   │   │   ├── routes/
│   │   │   │   └── auth.py   # Authentication endpoints
│   │   │   ├── schemas.py    # Request/response models
│   │   │   └── middleware/   # API middleware
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   ├── verification_token.py
│   │   │   └── password_reset_token.py
│   │   ├── services/         # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── password_service.py
│   │   │   ├── token_service.py
│   │   │   ├── email_service.py
│   │   │   └── jwt_service.py
│   │   ├── lib/              # Utilities
│   │   │   ├── database.py
│   │   │   ├── security_logger.py
│   │   │   └── validators.py
│   │   ├── config.py         # Configuration
│   │   └── main.py           # App entry point
│   ├── tests/
│   │   ├── integration/      # Integration tests
│   │   └── unit/            # Unit tests
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── requirements-dev.txt
├── specs/                   # Feature specifications
├── config/                  # Configuration files
└── CLAUDE.md               # Development guidelines
```

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (or SQLite for development)
- SMTP server (or use local mailcatcher for development)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd doit
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. **Configure environment**
```bash
cp config/.env.example config/.env
# Edit config/.env with your settings
```

5. **Run database migrations**
```bash
cd src
alembic upgrade head
```

6. **Start the development server**
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## Configuration

Create a `config/.env` file with the following settings:

```env
# Application
APP_NAME=DoIt
ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///./auth.db
DATABASE_URL_TEST=sqlite:///./test.db

# SMTP Email
SMTP_HOST=localhost
SMTP_PORT=1025
FROM_EMAIL=noreply@yourdomain.com

# Security
ARGON2_TIME_COST=2
ARGON2_MEMORY_COST=65536
ARGON2_PARALLELISM=1

# Session & Tokens
SESSION_EXPIRY_HOURS=24
VERIFICATION_TOKEN_EXPIRY_HOURS=24
RESET_TOKEN_EXPIRY_HOURS=1

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
```

## API Endpoints

Base URL: `http://localhost:8000/v1/auth`

### Registration & Verification

**POST** `/register`
- Register a new user account
- Request body: `{ "email": "user@example.com", "password": "SecurePass123!" }`
- Response: `201 Created` with user details

**GET** `/verify-email?token=<verification_token>`
- Verify email address
- Query param: `token` (from verification email)
- Response: `200 OK` on success

**POST** `/resend-verification`
- Resend verification email
- Request body: `{ "email": "user@example.com" }`
- Response: `200 OK`

### Authentication

**POST** `/login`
- Authenticate user and create session
- Request body: `{ "email": "user@example.com", "password": "SecurePass123!" }`
- Response: `200 OK` with session token

**POST** `/logout`
- Terminate active session
- Headers: `Authorization: Bearer <session_token>`
- Response: `200 OK`

### Password Reset

**POST** `/password/reset-request`
- Request password reset email
- Request body: `{ "email": "user@example.com" }`
- Response: `200 OK` (generic response for security)

**POST** `/password/reset`
- Reset password using token
- Request body: `{ "token": "reset_token", "new_password": "NewSecurePass123!" }`
- Response: `200 OK`

### Health & Info

**GET** `/`
- API information
- Response: API name and version

**GET** `/health`
- Health check endpoint
- Response: `200 OK` with status

## Development

### Running Tests

```bash
cd backend/src
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=src          # With coverage report
pytest tests/unit         # Run only unit tests
pytest tests/integration  # Run only integration tests
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy src/

# Code formatting
black src/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Security Features

### Password Security
- **Argon2 hashing** - Industry-standard password hashing algorithm
- **Strength validation** - Minimum 8 characters, uppercase, lowercase, digit, and special character required
- **Never stored in plain text** - Only hashed passwords are stored

### Account Protection
- **Account lockout** - Automatic lockout after 5 failed login attempts within 15 minutes
- **Auto-unlock** - Accounts automatically unlock after 30 minutes
- **Failed attempt tracking** - All failed login attempts are logged and tracked

### Token Security
- **Single-use tokens** - Verification and reset tokens can only be used once
- **Time-limited expiry** - Verification tokens expire after 24 hours, reset tokens after 1 hour
- **JWT sessions** - Secure session tokens with 24-hour expiry

### Email Security
- **Verification required** - Users must verify email before login
- **Generic responses** - Password reset doesn't reveal account existence
- **Email normalization** - All emails stored in lowercase

### Audit & Compliance
- **Security logging** - All authentication events are logged with timestamps and IP addresses
- **Privacy-focused** - Generic responses prevent user enumeration
- **CORS configured** - Ready for production deployment with proper CORS settings

## Testing Coverage

The project includes comprehensive test suites:

### Unit Tests
- Authentication service logic
- Password hashing and validation
- JWT token generation and validation
- Input validators
- Security logger functionality

### Integration Tests
- Complete registration flow
- Email verification process
- Login with session creation
- Password reset workflow
- Account lockout mechanism

## Database Schema

### User
- `id` - Primary key
- `email` - Unique, normalized email address
- `password_hash` - Argon2 hashed password
- `email_verified` - Verification status
- `is_locked` - Account lockout status
- `failed_login_attempts` - Failed attempt counter
- `lockout_until` - Lockout expiry timestamp
- `created_at`, `updated_at`, `last_login_at` - Timestamps

### Session
- `id` - Primary key
- `user_id` - Foreign key to User
- `session_token` - JWT token
- `expires_at` - Session expiry
- `is_active` - Session status
- `created_at` - Creation timestamp

### VerificationToken
- `id` - Primary key
- `user_id` - Foreign key to User
- `token` - Verification token
- `expires_at` - Token expiry
- `is_used` - Usage status
- `created_at` - Creation timestamp

### PasswordResetToken
- `id` - Primary key
- `user_id` - Foreign key to User
- `token` - Reset token
- `expires_at` - Token expiry
- `is_used` - Usage status
- `created_at` - Creation timestamp

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the code style defined in `CLAUDE.md`
- Write tests for all new features
- Ensure all tests pass before submitting PR
- Update documentation as needed
- Use type hints throughout
- Add comprehensive docstrings

## License

[Add your license here]

## Support

For issues and questions, please open an issue in the GitHub repository.

## Roadmap

- [ ] Multi-factor authentication (MFA)
- [ ] OAuth2/Social login integration
- [ ] Rate limiting middleware
- [ ] API key management
- [ ] User profile management
- [ ] Role-based access control (RBAC)

---

**Status**: Feature 001-user-auth ✓ Complete

Built with FastAPI and security best practices for modern web applications.
