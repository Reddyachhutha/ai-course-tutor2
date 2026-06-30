#!/usr/bin/env python3
"""
Production-grade configuration for AI Tutor Platform
Supports multiple environments: development, staging, production
"""

import os
import logging
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Type-safe configuration using Pydantic BaseSettings.
    Loads from .env file and environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ==================== ENVIRONMENT ====================
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ==================== API KEYS & SECRETS ====================
    GOOGLE_API_KEY: str
    SECRET_KEY: str = "change-me-in-production"

    # ==================== PATHS ====================
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "temp_uploads"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "chroma_data"

    # ==================== SERVER ====================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    APP_TITLE: str = "AI Course Tutor API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "RAG-based AI tutor using course materials"

    # ==================== CORS & SECURITY ====================
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    ENFORCE_HTTPS: bool = False
    ALLOWED_HOSTS: List[str] = ["*"]

    # ==================== RAG SETTINGS ====================
    COLLECTION_NAME: str = "syllabus"
    LLM_MODEL: str = "gemini-3-flash-preview"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768
    TOP_K_RESULTS: int = 5
    MAX_CHUNK_SIZE: int = 500
    MIN_CHUNK_SIZE: int = 50
    CHUNK_OVERLAP: int = 50

    # ==================== FILE UPLOAD ====================
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]

    # ==================== FRONTEND ====================
    FRONTEND_PORT: int = 8501
    BACKEND_URL: str = "http://localhost:8000"

    # ==================== DATABASE ====================
    DATABASE_URL: str = "sqlite:///./test.db"  # Optional: for future SQL DB

    # ==================== MONITORING & LOGGING ====================
    SENTRY_DSN: str = ""  # Optional: for error tracking
    ENABLE_METRICS: bool = False

    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def validate_google_key(cls, v: str) -> str:
        if not v or v == "your_google_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY not found or invalid in .env file\n"
                "Get your key at: https://aistudio.google.com/app/apikey"
            )
        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        if v not in ["development", "staging", "production"]:
            raise ValueError(
                f"ENVIRONMENT must be one of: development, staging, production. Got: {v}"
            )
        if v == "production":
            if os.getenv("SECRET_KEY", "").startswith("change-me"):
                raise ValueError("SECRET_KEY must be changed in production!")
        return v

    @field_validator("DEBUG")
    @classmethod
    def validate_debug(cls, v: bool, info) -> bool:
        # Never allow debug=True in production
        if info.data.get("ENVIRONMENT") == "production" and v:
            raise ValueError("DEBUG cannot be True in production environment")
        return v

    def create_directories(self) -> None:
        """Ensures all required directories exist."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Upload directory: {self.UPLOAD_DIR}")
        logger.info(f"✓ ChromaDB directory: {self.CHROMA_PERSIST_DIR}")

    def setup_logging(self) -> None:
        """Configure logging based on environment."""
        log_level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        logger.info(
            f"🚀 Starting AI Tutor Platform ({self.ENVIRONMENT} mode)"
        )
        logger.info(f"📚 Version: {self.APP_VERSION}")
        logger.info(f"🤖 LLM Model: {self.LLM_MODEL}")
        logger.info(f"📊 Embeddings: {self.EMBEDDING_MODEL}")


# Initialize settings with error handling
try:
    settings = Settings()
    settings.create_directories()
    settings.setup_logging()

except Exception as e:
    print(f"❌ Configuration Error: {e}")
    raise
