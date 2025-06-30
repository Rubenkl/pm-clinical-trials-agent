"""Tests for configuration system."""

import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError

from app.core.config import Settings, get_settings


class TestSettings:
    """Test cases for Settings configuration."""

    def test_settings_with_defaults(self):
        """Test that settings can be created with default values."""
        # Clear any environment variables that might interfere
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.app_name == "Clinical Trials Agent"
            assert settings.version == "0.1.0"
            assert settings.debug is True  # Changed default to True for testing
            assert settings.api_v1_str == "/api/v1"
            assert settings.openai_api_key == ""
            assert settings.database_url == ""
            assert settings.redis_url == "redis://localhost:6379"

    def test_settings_from_environment(self):
        """Test that settings are loaded from environment variables."""
        with patch.dict(os.environ, {
            "APP_NAME": "Test App",
            "DEBUG": "true",
            "OPENAI_API_KEY": "test-key-123",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "REDIS_URL": "redis://test:6379/1"
        }):
            settings = Settings()
            
            assert settings.app_name == "Test App"
            assert settings.debug is True
            assert settings.openai_api_key == "test-key-123"
            assert settings.database_url == "postgresql://test:test@localhost/test"
            assert settings.redis_url == "redis://test:6379/1"

    def test_settings_validation_error_for_invalid_url(self):
        """Test that invalid URLs raise validation errors."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "invalid-url"
        }):
            with pytest.raises(ValidationError):
                Settings()

    def test_openai_api_key_empty_allowed_in_debug(self):
        """Test that empty OpenAI API key is allowed in debug mode."""
        with patch.dict(os.environ, {
            "DEBUG": "true",
            "OPENAI_API_KEY": ""
        }):
            settings = Settings()
            assert settings.openai_api_key == ""
            assert settings.debug is True

    def test_log_level_validation(self):
        """Test that log level is validated correctly."""
        with patch.dict(os.environ, {
            "LOG_LEVEL": "INVALID"
        }):
            with pytest.raises(ValidationError):
                Settings()

    def test_database_config_properties(self):
        """Test database configuration properties."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/dbname"
        }):
            settings = Settings()
            
            assert settings.database_url == "postgresql://user:pass@localhost:5432/dbname"
            assert "postgresql://" in settings.database_url

    def test_cors_origins_parsing(self):
        """Test CORS origins are parsed correctly."""
        with patch.dict(os.environ, {
            "CORS_ORIGINS": "http://localhost:3000,https://example.com,https://app.example.com"
        }):
            settings = Settings()
            
            origins_list = settings.get_cors_origins_list()
            assert len(origins_list) == 3
            assert "http://localhost:3000" in origins_list
            assert "https://example.com" in origins_list
            assert "https://app.example.com" in origins_list


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2

    def test_get_settings_caching(self):
        """Test that settings are cached properly."""
        # Clear cache first
        get_settings.cache_clear()
        
        # First call should create instance
        settings1 = get_settings()
        
        # Second call should return cached instance  
        settings2 = get_settings()
        
        # Should be the same instance
        assert settings1 is settings2

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_get_settings_with_environment(self):
        """Test get_settings with environment variables."""
        # Clear cache first
        get_settings.cache_clear()
        
        settings = get_settings()
        assert settings.openai_api_key == "test-key"


@pytest.fixture
def mock_env_vars():
    """Fixture to provide mock environment variables."""
    return {
        "APP_NAME": "Test Clinical Trials Agent",
        "DEBUG": "true",
        "OPENAI_API_KEY": "test-openai-key-123",
        "DATABASE_URL": "postgresql://test:test@localhost/test_db",
        "REDIS_URL": "redis://localhost:6379/1",
        "LOG_LEVEL": "DEBUG",
        "CORS_ORIGINS": "http://localhost:3000,https://test.com"
    }


class TestSettingsIntegration:
    """Integration tests for settings configuration."""

    def test_full_configuration_load(self, mock_env_vars):
        """Test loading full configuration from environment."""
        with patch.dict(os.environ, mock_env_vars):
            settings = Settings()
            
            assert settings.app_name == "Test Clinical Trials Agent"
            assert settings.debug is True
            assert settings.openai_api_key == "test-openai-key-123"
            assert settings.database_url == "postgresql://test:test@localhost/test_db"
            assert settings.redis_url == "redis://localhost:6379/1"
            assert settings.log_level == "DEBUG"
            assert len(settings.get_cors_origins_list()) == 2

    def test_production_configuration(self):
        """Test production-ready configuration."""
        production_env = {
            "DEBUG": "false",
            "OPENAI_API_KEY": "prod-key-123",
            "DATABASE_URL": "postgresql://prod:prod@db.prod.com/clinical_trials",
            "REDIS_URL": "redis://cache.prod.com:6379",
            "LOG_LEVEL": "INFO",
            "CORS_ORIGINS": "https://app.clinicaltrials.com"
        }
        
        with patch.dict(os.environ, production_env):
            settings = Settings()
            
            assert settings.debug is False  # Environment variable "false" overrides default
            assert settings.log_level == "INFO"
            assert settings.openai_api_key == "prod-key-123"
            assert "prod.com" in settings.database_url