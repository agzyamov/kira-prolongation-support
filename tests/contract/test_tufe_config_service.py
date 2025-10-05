"""
Contract tests for TufeConfigService.
Tests the configuration service interface before implementation.
"""

import pytest
import os
from src.services.tufe_config_service import TufeConfigService


class TestTufeConfigService:
    """Contract tests for TufeConfigService."""

    def setup_method(self):
        """Set up test service for each test."""
        self.service = TufeConfigService()

    def test_get_tcmb_api_key_returns_string_or_none(self):
        """Test that get_tcmb_api_key returns string or None."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            api_key = self.service.get_tcmb_api_key()
            assert api_key is None or isinstance(api_key, str)

    def test_set_tcmb_api_key_returns_none(self):
        """Test that set_tcmb_api_key returns None."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            result = self.service.set_tcmb_api_key("test_key_123")
            assert result is None

    def test_get_cache_duration_hours_returns_int(self):
        """Test that get_cache_duration_hours returns integer."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            duration = self.service.get_cache_duration_hours()
            assert isinstance(duration, int)
            assert duration > 0

    def test_get_rate_limit_delay_returns_float(self):
        """Test that get_rate_limit_delay returns float."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            delay = self.service.get_rate_limit_delay()
            assert isinstance(delay, float)
            assert delay >= 0

    def test_is_debug_mode_returns_boolean(self):
        """Test that is_debug_mode returns boolean."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            debug_mode = self.service.is_debug_mode()
            assert isinstance(debug_mode, bool)

    def test_get_log_level_returns_string(self):
        """Test that get_log_level returns string."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            log_level = self.service.get_log_level()
            assert isinstance(log_level, str)
            assert log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_api_key_persistence(self):
        """Test that API key is persisted across service instances."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            # Set API key
            self.service.set_tcmb_api_key("test_key_123")
            
            # Create new service instance
            new_service = TufeConfigService()
            
            # Check if API key is persisted
            api_key = new_service.get_tcmb_api_key()
            assert api_key == "test_key_123"

    def test_environment_variable_handling(self):
        """Test that environment variables are handled properly."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            # Set environment variable
            os.environ['TCMB_API_KEY'] = 'env_test_key'
            
            # Create new service instance
            service = TufeConfigService()
            
            # Check if environment variable is read
            api_key = service.get_tcmb_api_key()
            assert api_key == 'env_test_key'
            
            # Clean up
            del os.environ['TCMB_API_KEY']

    def test_default_configuration_values(self):
        """Test that default configuration values are correct."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            # Test default cache duration
            duration = self.service.get_cache_duration_hours()
            assert duration == 24  # Default should be 24 hours
            
            # Test default rate limit delay
            delay = self.service.get_rate_limit_delay()
            assert delay == 1.0  # Default should be 1.0 seconds
            
            # Test default debug mode
            debug_mode = self.service.is_debug_mode()
            assert debug_mode is False  # Default should be False
            
            # Test default log level
            log_level = self.service.get_log_level()
            assert log_level == "INFO"  # Default should be INFO

    def test_configuration_validation(self):
        """Test that configuration values are validated."""
        # This will fail initially as the method doesn't exist
        with pytest.raises(AttributeError):
            # Test invalid API key
            with pytest.raises(ValueError):
                self.service.set_tcmb_api_key("")  # Empty key should raise error
            
            with pytest.raises(ValueError):
                self.service.set_tcmb_api_key(None)  # None key should raise error
