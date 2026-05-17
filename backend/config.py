import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import logging

class Settings(BaseSettings):
    """
    Type-safe configuration using Pydantic BaseSettings.
    Loads from .env file automatically.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys & URLs
    GOOGLE_API_KEY: str

    # Directory Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "temp_uploads"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "chroma_data"

    # RAG Settings
    COLLECTION_NAME: str = "syllabus"
    LLM_MODEL: str = "gemini-3-flash-preview"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768
    TOP_K_RESULTS: int = 5
    MAX_CHUNK_SIZE: int = 500
    MIN_CHUNK_SIZE: int = 50
    CHUNK_OVERLAP: int = 50
    
    # Validation Settings
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]

    # App Metadata
    APP_TITLE: str = "AI Course Tutor API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "RAG-based AI tutor using course materials"

    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def validate_google_key(cls, v: str) -> str:
        if not v or v == "your_google_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY not found in .env file\n"
                "Get your key at: https://aistudio.google.com"
            )
        return v

    def create_directories(self):
        """Ensures all required directories exist."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# Initialize settings
try:
    settings = Settings()
    settings.create_directories()
    
    # Startup Confirmation (Plain text for Windows terminal compatibility)
    print("==============================")
    print("Config loaded successfully")
    print(f"Upload dir: {settings.UPLOAD_DIR}")
    print(f"ChromaDB dir: {settings.CHROMA_PERSIST_DIR}")
    print(f"LLM: Gemini Flash 3 ({settings.LLM_MODEL})")
    print(f"Embeddings: Gemini API ({settings.EMBEDDING_MODEL})")
    print("==============================")
except Exception as e:
    print(f"Configuration Error: {e}")
    raise
