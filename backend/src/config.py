"""
Configuration management for the application.
Loads settings from environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
env_path = Path(__file__).resolve().parent.parent.parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "MyApp")
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./auth.db")
    DATABASE_URL_TEST: str = os.getenv("DATABASE_URL_TEST", "sqlite:///./test.db")

    # SMTP Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@localhost")
    FROM_NAME: str = os.getenv("FROM_NAME", "MyApp")

    # Security
    ARGON2_TIME_COST: int = int(os.getenv("ARGON2_TIME_COST", "2"))
    ARGON2_MEMORY_COST: int = int(os.getenv("ARGON2_MEMORY_COST", "65536"))
    ARGON2_PARALLELISM: int = int(os.getenv("ARGON2_PARALLELISM", "1"))

    # Session
    SESSION_EXPIRY_HOURS: int = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))

    # Tokens
    VERIFICATION_TOKEN_EXPIRY_HOURS: int = int(os.getenv("VERIFICATION_TOKEN_EXPIRY_HOURS", "24"))
    RESET_TOKEN_EXPIRY_HOURS: int = int(os.getenv("RESET_TOKEN_EXPIRY_HOURS", "1"))

    # Rate Limiting
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES: int = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
    LOCKOUT_WINDOW_MINUTES: int = int(os.getenv("LOCKOUT_WINDOW_MINUTES", "15"))


# Global settings instance
settings = Settings()
