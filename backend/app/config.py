"""
Configuration module for Healthcare Pricing Backend.

Reads PostgreSQL credentials from .env file and constructs
the database connection URL.
"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Base directory is the backend/ folder (parent of app/)
BASE_DIR = Path(__file__).resolve().parent.parent


def ensure_env_file() -> None:
    """
    Automatically copy .env.example to .env if .env does not exist.
    """
    env_path = BASE_DIR / ".env"
    env_example_path = BASE_DIR / ".env.example"

    if not env_path.exists():
        if env_example_path.exists():
            shutil.copy(env_example_path, env_path)
            print("✔ Created .env from .env.example")
        else:
            raise FileNotFoundError(
                "Neither .env nor .env.example found in backend/. "
                "Please create a .env file with database credentials."
            )


@dataclass(frozen=True)
class Settings:
    """Immutable database configuration loaded from environment variables."""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def database_url(self) -> str:
        """SQLAlchemy connection URL for the target database."""
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


def load_settings() -> Settings:
    """
    Load database settings from the .env file.
    """
    ensure_env_file()
    load_dotenv(BASE_DIR / ".env", override=True)

    return Settings(
        DB_HOST=os.getenv("DB_HOST", "localhost"),
        DB_PORT=int(os.getenv("DB_PORT", "5432")),
        DB_NAME=os.getenv("DB_NAME", "healthcare_pricing"),
        DB_USER=os.getenv("DB_USER", "postgres"),
        DB_PASSWORD=os.getenv("DB_PASSWORD", "root"),
    )
