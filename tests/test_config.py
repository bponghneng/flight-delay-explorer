"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from flight_delay_explorer.config import Settings


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_creation_with_defaults(self):
        """Test creating Settings with default values."""
        # Test with environment isolation - no .env file loading and no env vars
        settings = Settings.for_testing(use_env_vars=False)

        assert settings.access_key == "test-key-e2e"
        assert settings.base_url == "https://api.aviationstack.com/v1"
        assert settings.max_retries == 3
        assert settings.timeout_seconds == 30

    def test_settings_with_environment_variables(self):
        """Test that Settings loads values from environment variables."""
        env_vars = {
            "AVIATIONSTACK_ACCESS_KEY": "custom-api-key",
            "BASE_URL": "https://custom.api.com/v2",
            "MAX_RETRIES": "5",
            "TIMEOUT_SECONDS": "60",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings.for_testing()

            assert settings.access_key == "custom-api-key"
            assert settings.base_url == "https://custom.api.com/v2"
            assert settings.max_retries == 5
            assert settings.timeout_seconds == 60

    def test_settings_type_validation(self):
        """Test that Settings validates field types correctly."""
        env_vars = {
            "AVIATIONSTACK_ACCESS_KEY": "test-key",
            "MAX_RETRIES": "not-a-number",
            "TIMEOUT_SECONDS": "30",
        }

        with patch.dict(os.environ, env_vars, clear=True), pytest.raises(ValueError):
            Settings.for_testing()

    def test_settings_required_fields(self):
        """Test that Settings has a default access_key value."""
        settings = Settings.for_testing(use_env_vars=False)
        assert settings.access_key == "test-key-e2e"

    def test_settings_partial_override(self):
        """Test overriding only some environment variables."""
        env_vars = {"AVIATIONSTACK_ACCESS_KEY": "test-key", "MAX_RETRIES": "10"}

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings.for_testing()

            assert settings.access_key == "test-key"
            assert settings.max_retries == 10
            # Should use defaults for unspecified values
            assert settings.base_url == "https://api.aviationstack.com/v1"
            assert settings.timeout_seconds == 30

    def test_settings_field_types(self):
        """Test that Settings fields have correct types."""
        env_vars = {
            "AVIATIONSTACK_ACCESS_KEY": "test-key",
            "BASE_URL": "https://api.example.com",
            "MAX_RETRIES": "5",
            "TIMEOUT_SECONDS": "45",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings.for_testing()

            assert isinstance(settings.access_key, str)
            assert isinstance(settings.base_url, str)
            assert isinstance(settings.max_retries, int)
            assert isinstance(settings.timeout_seconds, int)

    def test_settings_environment_prefix(self):
        """Test that Settings uses correct environment variable names."""
        # Test that proper aliases are used
        env_vars = {
            "AVIATIONSTACK_ACCESS_KEY": "test-key",
            "ACCESS_KEY": "should-be-ignored",
            "WRONG_BASE_URL": "should-be-ignored",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings.for_testing()

            assert settings.access_key == "test-key"
            assert settings.base_url == "https://api.aviationstack.com/v1"  # default
