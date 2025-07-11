"""Application configuration settings."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="Clinical Trials Agent", env="APP_NAME")
    version: str = Field(default="0.1.0", env="VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    api_v1_str: str = Field(default="/api/v1", env="API_V1_STR")

    # OpenAI Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")

    # Database Configuration
    database_url: str = Field(default="", env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # CORS
    cors_origins: str = Field(default="", env="CORS_ORIGINS")

    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    # Test Data Configuration
    use_test_data: bool = Field(default=False, env="USE_TEST_DATA")
    test_data_preset: str = Field(default="cardiology_phase2", env="TEST_DATA_PRESET")
    test_data_path: str = Field(default="tests/test_data/", env="TEST_DATA_PATH")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if v and not v.startswith(
            (
                "postgresql://",
                "postgresql+asyncpg://",
                "sqlite://",
                "sqlite+aiosqlite://",
                "mysql://",
                "mysql+aiomysql://",
            )
        ):
            raise ValueError("Invalid database URL format")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        """Parse CORS origins from string."""
        return v or ""

    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if not self.cors_origins:
            return []
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @field_validator("openai_temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate OpenAI temperature is between 0 and 2."""
        if not 0 <= v <= 2:
            raise ValueError("OpenAI temperature must be between 0 and 2")
        return v

    @field_validator("test_data_preset")
    @classmethod
    def validate_test_data_preset(cls, v: str) -> str:
        """Validate test data preset name."""
        valid_presets = ["cardiology_phase2", "oncology_phase1"]
        if v not in valid_presets:
            raise ValueError(f"Test data preset must be one of {valid_presets}")
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience function to access settings
settings = get_settings()
