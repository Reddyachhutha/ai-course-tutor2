import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, SecretStr
import logging

class Settings(BaseSettings):
    """
    Type-safe configuration using Pydantic BaseSettings.
    Loads from .env file automatically.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys & URLs
    GOOGLE_API_KEY: str
    OPENROUTER_API_KEY: str = "optional"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Directory Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "temp_uploads"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "chroma_data"

    # RAG Settings
    COLLECTION_NAME: str = "syllabus"
    MAX_CHUNK_SIZE: int = 500
    MIN_CHUNK_SIZE: int = 50
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5
    
    # Validation Settings
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]

    # App Metadata
    APP_TITLE: str = "🎓 AI Course Tutor API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "RAG-based AI tutor using course materials"

    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def validate_google_key(cls, v: str) -> str:
        if not v or v == "your_google_api_key_here":
            raise ValueError(
                "❌ GOOGLE_API_KEY not found in .env file\n"
                "Get your key at: https://makersuite.google.com"
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
    
    # Startup Confirmation
    print("="*30)
    print("Config loaded successfully")
    print(f"Upload dir: {settings.UPLOAD_DIR}")
    print(f"ChromaDB dir: {settings.CHROMA_PERSIST_DIR}")
    print("LLM: Gemini Flash 3")
    print("Embeddings: all-MiniLM-L6-v2 (local)")
    print("="*30)
except Exception as e:
    print(f"Configuration Error: {e}")
    raise
