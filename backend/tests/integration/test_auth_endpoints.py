"""
Integration tests for authentication endpoints.
Tests the full API flow including database integration.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.lib.database import Base, get_db
from src.models.user import User
from src.models.verification_token import VerificationToken
from src.models.session import Session


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
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


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_register_success():
    """Test successful user registration"""
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "user_id" in data
    assert "Please check your email" in data["message"]


def test_register_duplicate_email():
    """Test registration with duplicate email fails"""
    # First registration
    client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    # Second registration with same email
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "AnotherPass456!"
        }
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_weak_password():
    """Test registration with weak password fails"""
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "weak"
        }
    )

    # Pydantic validation (min_length) returns 422, business logic returns 400
    assert response.status_code in [400, 422]
    assert "security requirements" in str(response.json()) or "min_length" in str(response.json())


def test_register_invalid_email():
    """Test registration with invalid email fails"""
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 422  # Pydantic validation error


def test_verify_email_success():
    """Test successful email verification"""
    # Register user
    register_response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    user_id = register_response.json()["user_id"]

    # Get verification token from database
    db = TestingSessionLocal()
    token = db.query(VerificationToken).filter(
        VerificationToken.user_id == user_id
    ).first()

    # Verify email
    response = client.get(f"/v1/auth/verify-email?token={token.token}")
    assert response.status_code == 200
    data = response.json()
    assert "verified successfully" in data["message"]

    # Check user is now verified
    user = db.query(User).filter(User.id == user_id).first()
    assert user.email_verified is True
    db.close()


def test_verify_email_invalid_token():
    """Test email verification with invalid token fails"""
    response = client.get("/v1/auth/verify-email?token=invalid-token-123")
    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


def test_verify_email_already_used():
    """Test email verification with already used token fails"""
    # Register user
    register_response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    user_id = register_response.json()["user_id"]

    # Get verification token
    db = TestingSessionLocal()
    token = db.query(VerificationToken).filter(
        VerificationToken.user_id == user_id
    ).first()
    token_value = token.token
    db.close()

    # Verify email first time
    response1 = client.get(f"/v1/auth/verify-email?token={token_value}")
    assert response1.status_code == 200

    # Try to verify again
    response2 = client.get(f"/v1/auth/verify-email?token={token_value}")
    assert response2.status_code == 400
    assert "already used" in response2.json()["detail"]


def test_resend_verification():
    """Test resending verification email"""
    # Register user
    client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    # Resend verification
    response = client.post(
        "/v1/auth/resend-verification",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 200
    assert "message" in response.json()


def test_resend_verification_nonexistent_email():
    """Test resending verification for nonexistent email returns generic message"""
    response = client.post(
        "/v1/auth/resend-verification",
        json={"email": "nonexistent@example.com"}
    )

    # Should return success even for nonexistent email (security)
    assert response.status_code == 200
    assert "message" in response.json()
