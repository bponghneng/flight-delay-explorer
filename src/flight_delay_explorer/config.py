"""Configuration management for Flight Delay Explorer."""

import os
from typing import Any
from unittest.mock import patch

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @classmethod
    def for_testing(
        cls,
        use_env_vars: bool = True,
        **overrides: Any,
    ) -> "Settings":
        """Create Settings instance for testing with .env file disabled.

        Args:
            use_env_vars: Whether to use environment variables (default: True)
            **overrides: Override specific settings values
        """

        # Always disable .env file loading in test mode
        # This ensures we don't pick up values from the .env file
        kwargs = {"_env_file": None}

        # Create the instance with or without environment variables
        if use_env_vars:
            # Use current environment variables but no .env file
            instance = cls(**kwargs)  # type: ignore
        else:
            # Create with a clean environment (no env vars, no .env file)
            # This ensures we get the default values defined in the class
            with patch.dict(os.environ, {}, clear=True):
                instance = cls(**kwargs)  # type: ignore

        # Apply any overrides directly to the instance attributes
        for key, value in overrides.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        return instance

    access_key: str = Field(
        default="test-key-e2e",
        alias="AVIATIONSTACK_ACCESS_KEY",
        description="AviationStack API access key",
    )
    base_url: str = Field(
        default="https://api.aviationstack.com/v1",
        alias="BASE_URL",
        description="API base URL",
    )
    max_retries: int = Field(
        default=3, alias="MAX_RETRIES", description="Maximum retry attempts"
    )
    timeout_seconds: int = Field(
        default=30, alias="TIMEOUT_SECONDS", description="Request timeout in seconds"
    )
