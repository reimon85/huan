"""Application configuration using Pydantic settings."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
    )

    # Application
    app_name: str = Field(default="Trading Companion", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Wiki Configuration
    wiki_content_path: Path = Field(
        default=Path("./trading_companion/wiki/content"),
        description="Path to wiki content files",
    )
    wiki_db_path: Path = Field(
        default=Path("./data/wiki.db"),
        description="Path to SQLite database for search index",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload on code changes")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Comma-separated CORS origins",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100, description="Maximum requests per window"
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format (json/text)")

    # Paths
    @property
    def data_dir(self) -> Path:
        """Ensure data directory exists and return path."""
        self.wiki_db_path.parent.mkdir(parents=True, exist_ok=True)
        return self.wiki_db_path.parent


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
