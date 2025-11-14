from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Config
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    DATABASE_URL: str = "sqlite:///./pfmo_data.db"

    # For production, DATABASE_URL will be set via environment variable
    # Format: postgresql://user:password@host:port/database

    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    # First Admin User (for initial setup)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"  # Change this!
    ADMIN_EMAIL: str = "admin@pfmo.org"
    ADMIN_FULL_NAME: str = "System Administrator"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
