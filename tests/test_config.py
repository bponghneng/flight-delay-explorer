"""Tests for configuration management."""
import os
import pytest
from unittest.mock import patch

from flight_delay_explorer.config import Settings


class TestSettings:
    """Test Settings configuration class."""
    
    def test_settings_creation_with_defaults(self):
        """Test creating Settings with default values."""
        # Clear any existing environment variables first
        env_vars = [
            'FLIGHT_ACCESS_KEY', 'FLIGHT_BASE_URL', 
            'FLIGHT_MAX_RETRIES', 'FLIGHT_TIMEOUT_SECONDS'
        ]
        
        with patch.dict(os.environ, {}, clear=True):
            # Set required variables
            with patch.dict(os.environ, {'FLIGHT_ACCESS_KEY': 'test-key'}):
                settings = Settings()
                
                assert settings.access_key == "test-key"
                assert settings.base_url == "https://api.aviationstack.com/v1"
                assert settings.max_retries == 3
                assert settings.timeout_seconds == 30
    
    def test_settings_with_environment_variables(self):
        """Test that Settings loads values from environment variables."""
        env_vars = {
            'FLIGHT_ACCESS_KEY': 'custom-api-key',
            'FLIGHT_BASE_URL': 'https://custom.api.com/v2',
            'FLIGHT_MAX_RETRIES': '5',
            'FLIGHT_TIMEOUT_SECONDS': '60'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert settings.access_key == "custom-api-key"
            assert settings.base_url == "https://custom.api.com/v2"
            assert settings.max_retries == 5
            assert settings.timeout_seconds == 60
    
    def test_settings_type_validation(self):
        """Test that Settings validates field types correctly."""
        env_vars = {
            'FLIGHT_ACCESS_KEY': 'test-key',
            'FLIGHT_MAX_RETRIES': 'not-a-number',
            'FLIGHT_TIMEOUT_SECONDS': '30'
        }
        
        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError):
                Settings()
    
    def test_settings_required_fields(self):
        """Test that Settings requires access_key field."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                Settings()
    
    def test_settings_partial_override(self):
        """Test overriding only some environment variables."""
        env_vars = {
            'FLIGHT_ACCESS_KEY': 'test-key',
            'FLIGHT_MAX_RETRIES': '10'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert settings.access_key == "test-key"
            assert settings.max_retries == 10
            # Should use defaults for unspecified values
            assert settings.base_url == "https://api.aviationstack.com/v1"
            assert settings.timeout_seconds == 30
    
    def test_settings_field_types(self):
        """Test that Settings fields have correct types."""
        env_vars = {
            'FLIGHT_ACCESS_KEY': 'test-key',
            'FLIGHT_BASE_URL': 'https://api.example.com',
            'FLIGHT_MAX_RETRIES': '5',
            'FLIGHT_TIMEOUT_SECONDS': '45'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert isinstance(settings.access_key, str)
            assert isinstance(settings.base_url, str)
            assert isinstance(settings.max_retries, int)
            assert isinstance(settings.timeout_seconds, int)
    
    def test_settings_environment_prefix(self):
        """Test that Settings uses FLIGHT_ prefix for environment variables."""
        # Test that non-prefixed variables are ignored
        env_vars = {
            'FLIGHT_ACCESS_KEY': 'test-key',
            'ACCESS_KEY': 'should-be-ignored',
            'BASE_URL': 'should-be-ignored'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert settings.access_key == "test-key"
            assert settings.base_url == "https://api.aviationstack.com/v1"  # default