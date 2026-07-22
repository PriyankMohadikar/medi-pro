"""
Configuration module for Healthcare Pricing Data Layer.

Handles environment variable loading, .env file management,
and database URL construction.
"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Base directory is the backend/ folder
BASE_DIR = Path(__file__).resolve().parent


def ensure_env_file() -> None:
    """
    Automatically copy .env.example to .env if .env does not exist.
    This allows first-run setup without manual file creation.
    """
    env_path = BASE_DIR / ".env"
    env_example_path = BASE_DIR / ".env.example"

    if not env_path.exists():
        if env_example_path.exists():
            shutil.copy(env_example_path, env_path)
            print(f"✔ Created .env from .env.example")
        else:
            raise FileNotFoundError(
                "Neither .env nor .env.example found in backend/. "
                "Please create a .env file with database credentials."
            )


@dataclass(frozen=True)
class Settings:
    """Immutable database and LLM configuration loaded from environment variables."""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DATABASE_URL: str = ""
    
    # AI Provider configuration
    AI_PROVIDER: str = "ollama"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openrouter/free"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"

    # Ollama settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    TEMPERATURE: float = 0.2
    TOP_P: float = 0.9
    NUM_PREDICT: int = 512

    # CORS & Deployment
    ALLOWED_ORIGINS: str = ""

    @property
    def database_url(self) -> str:
        """SQLAlchemy connection URL for the target database (supports Supabase/Cloud PostgreSQL)."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip().strip("'").strip('"')
            # Normalize postgres:// to postgresql+psycopg2:// if needed
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg2://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def default_database_url(self) -> str:
        """
        SQLAlchemy connection URL for the default 'postgres' database.
        Used to check/create the target database.
        """
        if self.DATABASE_URL:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/postgres"
        )


def mask_database_url(url: str) -> str:
    """Mask the password in a database connection URL for safe logging."""
    if not url:
        return "<empty>"
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.password:
            masked_netloc = parsed.netloc.replace(f":{parsed.password}@", ":****@")
            return parsed._replace(netloc=masked_netloc).geturl()
        return url
    except Exception:
        return "<invalid_url_format>"


def load_settings() -> Settings:
    """
    Load database settings from environment variables and .env file.
    System environment variables (e.g., Render/Cloud) take precedence over .env file defaults.
    """
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)
    else:
        env_example_path = BASE_DIR / ".env.example"
        if env_example_path.exists():
            load_dotenv(env_example_path, override=False)

    raw_db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL") or ""
    if raw_db_url:
        raw_db_url = raw_db_url.strip().strip("'").strip('"')

    return Settings(
        DB_HOST=os.getenv("DB_HOST", "localhost"),
        DB_PORT=int(os.getenv("DB_PORT", "5432")),
        DB_NAME=os.getenv("DB_NAME", "healthcare_pricing"),
        DB_USER=os.getenv("DB_USER", "postgres"),
        DB_PASSWORD=os.getenv("DB_PASSWORD", "root"),

        DATABASE_URL=raw_db_url,
        
        OLLAMA_HOST=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        TEMPERATURE=float(os.getenv("TEMPERATURE", "0.2")),
        TOP_P=float(os.getenv("TOP_P", "0.9")),
        NUM_PREDICT=int(os.getenv("NUM_PREDICT", "512")),
        
        AI_PROVIDER=os.getenv("AI_PROVIDER", "ollama"),
        GROQ_API_KEY=os.getenv("GROQ_API_KEY", ""),
        GROQ_MODEL=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY", ""),
        OPENROUTER_MODEL=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", ""),
        GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS", ""),
    )


