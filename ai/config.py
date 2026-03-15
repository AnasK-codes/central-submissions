"""
ai/config.py

Standalone AI configuration — reads API keys from environment variables.
The AI module has ZERO dependency on the backend's app.core.config.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class AISettings(BaseSettings):
    GROQ_API_KEY: str = ""
    PINECONE_API_KEY: str = ""

    model_config = SettingsConfigDict(
        # Look for .env in the backend folder (where the app is launched from)
        # as well as the project root
        env_file=(
            os.path.join(os.path.dirname(__file__), "..", "backend", ".env"),
            os.path.join(os.path.dirname(__file__), "..", ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


ai_settings = AISettings()
