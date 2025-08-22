# app/config.py
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anon key")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(
        None, description="Service role key (server only)"
    )

    # App
    SECRET_KEY: str = Field("change-me", description="Cookie signing key")
    COOKIE_NAME: str = "pikszis_session"
    COOKIE_SAMESITE: str = "lax"
    COOKIE_SECURE: bool = False
    SESSION_MAX_AGE: int = 60 * 60 * 24 * 30  # 30 days

    # WordPress embed / CORS
    EMBED_ALLOWED_ORIGINS: Optional[str] = None  # comma-separated origins, e.g. "https://example.com,https://foo.bar"

    # Recommended questionnaires to pin first
    CORE_QUESTIONNAIRE_IDS: List[str] = ["IDEA", "COMM", "Q1"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()
