"""
database/config.py

Standalone database configuration — reads DATABASE_URL from environment variables.
The database module has ZERO dependency on the backend's app.core.config.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(__file__), "..", "backend", ".env"),
            os.path.join(os.path.dirname(__file__), "..", ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


db_settings = DatabaseSettings()
