"""
Integration tests for login functionality.
Tests complete login flow including account lockout.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.lib.database import Base, get_db
from src.models.user import User
from src.models.verification_token import VerificationToken
from src.services.password_service import PasswordService


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_login.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def create_verified_user(email: str, password: str):
    """Helper to create a verified user"""
    db = TestingSessionLocal()
    password_service = PasswordService()

    user = User(
        email=email,
        password_hash=password_service.hash_password(password),
        email_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_login_success():
    """Test successful login"""
    create_verified_user("test@example.com", "SecurePass123!")

    response = client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "session_token" in data
    assert "expires_at" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["email_verified"] is True


def test_login_invalid_email():
    """Test login with non-existent email"""
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!"
        }
    )

    assert response.status_code == 400
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_password():
    """Test login with wrong password"""
    create_verified_user("test@example.com", "SecurePass123!")

    response = client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword456!"
        }
    )

    assert response.status_code == 400
    assert "Invalid email or password" in response.json()["detail"]


def test_login_unverified_email():
    """Test login fails if email not verified"""
    # Create unverified user
    db = TestingSessionLocal()
    password_service = PasswordService()
    user = User(
        email="unverified@example.com",
        password_hash=password_service.hash_password("SecurePass123!"),
        email_verified=False
    )
    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/v1/auth/login",
        json={
            "email": "unverified@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 401
    assert "verify your email" in response.json()["detail"]


def test_login_account_lockout():
    """Test account gets locked after 5 failed attempts"""
    create_verified_user("test@example.com", "SecurePass123!")

    # Make 5 failed login attempts
    for i in range(5):
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword!"
            }
        )

        if i < 4:
            # First 4 attempts: invalid password
            assert response.status_code == 400
        else:
            # 5th attempt locks account and returns 403
            assert response.status_code == 403
            assert "locked" in response.json()["detail"]

    # Next attempt should show account is still locked
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"  # Even correct password
        }
    )

    assert response.status_code == 403
    assert "Account is locked" in response.json()["detail"]


def test_login_resets_failed_attempts():
    """Test successful login resets failed attempts counter"""
    create_verified_user("test@example.com", "SecurePass123!")

    # Make 2 failed attempts
    for _ in range(2):
        client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword!"
            }
        )

    # Successful login should reset counter
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200

    # Now can try 5 more times before lockout
    for i in range(5):
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword!"
            }
        )

        if i < 4:
            assert response.status_code == 400
            assert "Invalid" in response.json()["detail"]
        else:
            # 5th attempt locks account and returns 403
            assert response.status_code == 403
            assert "locked" in response.json()["detail"]


def test_login_creates_session():
    """Test login creates session in database"""
    create_verified_user("test@example.com", "SecurePass123!")

    response = client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200
    token = response.json()["session_token"]

    # Verify session exists in database
    from src.models.session import Session
    db = TestingSessionLocal()
    session = db.query(Session).filter(Session.token == token).first()
    assert session is not None
    assert session.is_active is True
    db.close()


def test_login_case_insensitive_email():
    """Test login is case-insensitive for email"""
    create_verified_user("test@example.com", "SecurePass123!")

    # Try login with uppercase email
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "TEST@EXAMPLE.COM",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "test@example.com"
