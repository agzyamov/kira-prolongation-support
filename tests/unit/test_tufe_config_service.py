"""
Unit tests for TufeConfigService.
"""

import pytest
import os
from src.services.tufe_config_service import TufeConfigService


class TestTufeConfigService:
    """Unit tests for TufeConfigService."""

    def setup_method(self):
        """Set up test service for each test."""
        # Clean up environment variables before each test
        for key in ['TCMB_API_KEY', 'TUFU_CACHE_DURATION_HOURS', 'TUFU_RATE_LIMIT_DELAY_SECONDS', 
                   'TUFU_DEBUG_MODE', 'TUFU_LOG_LEVEL']:
            if key in os.environ:
                del os.environ[key]
        
        self.service = TufeConfigService()

    def test_get_tcmb_api_key_none(self):
        """Test getting TCMB API key when none is set."""
        api_key = self.service.get_tcmb_api_key()
        assert api_key is None

    def test_set_tcmb_api_key_success(self):
        """Test setting TCMB API key successfully."""
        self.service.set_tcmb_api_key("test_api_key_123")
        
        api_key = self.service.get_tcmb_api_key()
        assert api_key == "test_api_key_123"

    def test_set_tcmb_api_key_empty_raises_error(self):
        """Test setting empty TCMB API key raises error."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            self.service.set_tcmb_api_key("")

    def test_set_tcmb_api_key_none_raises_error(self):
        """Test setting None TCMB API key raises error."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            self.service.set_tcmb_api_key(None)

    def test_get_cache_duration_hours(self):
        """Test getting cache duration in hours."""
        duration = self.service.get_cache_duration_hours()
        assert isinstance(duration, int)
        assert duration > 0

    def test_get_rate_limit_delay(self):
        """Test getting rate limit delay in seconds."""
        delay = self.service.get_rate_limit_delay()
        assert isinstance(delay, float)
        assert delay >= 0

    def test_is_debug_mode(self):
        """Test checking if debug mode is enabled."""
        debug_mode = self.service.is_debug_mode()
        assert isinstance(debug_mode, bool)

    def test_get_log_level(self):
        """Test getting logging level."""
        log_level = self.service.get_log_level()
        assert isinstance(log_level, str)
        assert log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_is_api_key_configured_false(self):
        """Test checking if API key is configured when none is set."""
        is_configured = self.service.is_api_key_configured()
        assert is_configured is False

    def test_is_api_key_configured_true(self):
        """Test checking if API key is configured when one is set."""
        self.service.set_tcmb_api_key("test_key")
        
        is_configured = self.service.is_api_key_configured()
        assert is_configured is True

    def test_validate_api_key_no_key(self):
        """Test validating API key when none is configured."""
        is_valid = self.service.validate_api_key()
        assert is_valid is False

    def test_validate_api_key_invalid_key(self):
        """Test validating invalid API key."""
        self.service.set_tcmb_api_key("invalid_key")
        
        is_valid = self.service.validate_api_key()
        assert is_valid is False

    def test_get_configuration_summary(self):
        """Test getting configuration summary."""
        summary = self.service.get_configuration_summary()
        
        assert isinstance(summary, dict)
        assert "api_key_configured" in summary
        assert "api_key_valid" in summary
        assert "cache_duration_hours" in summary
        assert "rate_limit_delay_seconds" in summary
        assert "debug_mode" in summary
        assert "log_level" in summary

    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        # Set some configuration
        self.service.set_tcmb_api_key("test_key")
        
        # Reset to defaults
        self.service.reset_to_defaults()
        
        # Verify reset
        api_key = self.service.get_tcmb_api_key()
        assert api_key is None

    def test_update_cache_duration(self):
        """Test updating cache duration."""
        self.service.update_cache_duration(48)
        
        duration = self.service.get_cache_duration_hours()
        assert duration == 48

    def test_update_cache_duration_invalid(self):
        """Test updating cache duration with invalid value."""
        with pytest.raises(ValueError, match="Cache duration must be positive"):
            self.service.update_cache_duration(0)

    def test_update_rate_limit_delay(self):
        """Test updating rate limit delay."""
        self.service.update_rate_limit_delay(2.5)
        
        delay = self.service.get_rate_limit_delay()
        assert delay == 2.5

    def test_update_rate_limit_delay_invalid(self):
        """Test updating rate limit delay with invalid value."""
        with pytest.raises(ValueError, match="Rate limit delay must be non-negative"):
            self.service.update_rate_limit_delay(-1.0)

    def test_enable_disable_debug_mode(self):
        """Test enabling and disabling debug mode."""
        # Enable debug mode
        self.service.enable_debug_mode()
        assert self.service.is_debug_mode() is True
        
        # Disable debug mode
        self.service.disable_debug_mode()
        assert self.service.is_debug_mode() is False

    def test_set_log_level(self):
        """Test setting log level."""
        self.service.set_log_level("DEBUG")
        assert self.service.get_log_level() == "DEBUG"
        
        self.service.set_log_level("ERROR")
        assert self.service.get_log_level() == "ERROR"

    def test_set_log_level_invalid(self):
        """Test setting invalid log level."""
        with pytest.raises(ValueError, match="Log level must be one of"):
            self.service.set_log_level("INVALID")

    def test_get_environment_variables(self):
        """Test getting TÜFE-related environment variables."""
        # Set some environment variables
        os.environ['TCMB_API_KEY'] = 'test_key'
        os.environ['TUFU_DEBUG_MODE'] = 'true'
        
        env_vars = self.service.get_environment_variables()
        
        assert isinstance(env_vars, dict)
        assert 'TCMB_API_KEY' in env_vars
        assert 'TUFU_DEBUG_MODE' in env_vars
        
        # Clean up
        del os.environ['TCMB_API_KEY']
        del os.environ['TUFU_DEBUG_MODE']

    def test_validate_configuration_valid(self):
        """Test validating valid configuration."""
        # Set valid configuration
        self.service.set_tcmb_api_key("test_key")
        
        validation = self.service.validate_configuration()
        
        assert isinstance(validation, dict)
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert isinstance(validation["valid"], bool)
        assert isinstance(validation["errors"], list)
        assert isinstance(validation["warnings"], list)

    def test_validate_configuration_no_api_key(self):
        """Test validating configuration without API key."""
        validation = self.service.validate_configuration()
        
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
        assert "TCMB API key is not configured" in validation["errors"]

    def test_validate_configuration_invalid_cache_duration(self):
        """Test validating configuration with invalid cache duration."""
        # Try to set invalid cache duration - should raise exception
        with pytest.raises(ValueError, match="Cache duration must be positive"):
            self.service.update_cache_duration(-1)

    def test_validate_configuration_invalid_rate_delay(self):
        """Test validating configuration with invalid rate delay."""
        # Try to set invalid rate delay - should raise exception
        with pytest.raises(ValueError, match="Rate limit delay must be non-negative"):
            self.service.update_rate_limit_delay(-1.0)

    def test_validate_configuration_invalid_log_level(self):
        """Test validating configuration with invalid log level."""
        # Try to set invalid log level - should raise exception
        with pytest.raises(ValueError, match="Log level must be one of"):
            self.service.set_log_level("INVALID")

    def test_validate_configuration_warnings(self):
        """Test validating configuration with warnings."""
        # Set configuration that generates warnings
        self.service.update_cache_duration(200)  # Very long cache duration
        self.service.update_rate_limit_delay(15.0)  # Very long delay
        
        validation = self.service.validate_configuration()
        
        assert len(validation["warnings"]) > 0
        assert any("Cache duration is very long" in warning for warning in validation["warnings"])
        assert any("Rate limit delay is very long" in warning for warning in validation["warnings"])
