"""
TufeConfigService for managing TÜFE configuration.

This service provides secure configuration management for TÜFE (Turkish CPI) data sources,
including TCMB API key management, cache settings, and rate limiting configuration.

Features:
- Secure TCMB API key storage and validation
- Configurable cache duration (default: 24 hours)
- Rate limiting configuration for API calls
- Debug mode and logging level management
- Environment variable integration
- Configuration validation and error handling

Security:
- API keys are stored in environment variables
- No plain text storage of sensitive data
- Configuration validation prevents invalid settings
"""

import os
from typing import Optional
from src.config.tufe_config import TufeConfig


class TufeConfigService:
    """Service for managing TÜFE configuration."""
    
    def __init__(self):
        """Initialize the configuration service."""
        self.config = TufeConfig()
    
    def get_tcmb_api_key(self) -> Optional[str]:
        """Get the TCMB API key."""
        return self.config.get_tcmb_api_key()
    
    def set_tcmb_api_key(self, api_key: str) -> None:
        """Set the TCMB API key."""
        if not api_key or not api_key.strip():
            raise ValueError("API key must be a non-empty string")
        
        self.config.set_tcmb_api_key(api_key)
    
    def get_cache_duration_hours(self) -> int:
        """Get cache duration in hours."""
        return self.config.get_cache_duration_hours()
    
    def get_rate_limit_delay(self) -> float:
        """Get rate limit delay in seconds."""
        return self.config.get_rate_limit_delay()
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.is_debug_mode()
    
    def get_log_level(self) -> str:
        """Get logging level."""
        return self.config.get_log_level()
    
    def is_api_key_configured(self) -> bool:
        """Check if API key is configured."""
        return self.config.is_api_key_configured()
    
    def validate_api_key(self) -> bool:
        """Validate the configured API key."""
        try:
            if not self.is_api_key_configured():
                return False
            
            # Import here to avoid circular imports
            from src.services.tcmb_api_client import TCMBApiClient
            
            api_key = self.get_tcmb_api_key()
            if not api_key:
                return False
            
            client = TCMBApiClient(api_key)
            return client.validate_api_key()
            
        except Exception:
            return False
    
    def get_configuration_summary(self) -> dict:
        """Get a summary of the current configuration."""
        return {
            "api_key_configured": self.is_api_key_configured(),
            "api_key_valid": self.validate_api_key() if self.is_api_key_configured() else False,
            "cache_duration_hours": self.get_cache_duration_hours(),
            "rate_limit_delay_seconds": self.get_rate_limit_delay(),
            "debug_mode": self.is_debug_mode(),
            "log_level": self.get_log_level()
        }
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        # Reset API key
        if 'TCMB_API_KEY' in os.environ:
            del os.environ['TCMB_API_KEY']
        
        # Reset other environment variables
        for key in ['TUFU_CACHE_DURATION_HOURS', 'TUFU_RATE_LIMIT_DELAY_SECONDS', 
                   'TUFU_DEBUG_MODE', 'TUFU_LOG_LEVEL']:
            if key in os.environ:
                del os.environ[key]
        
        # Reinitialize config
        self.config = TufeConfig()
    
    def update_cache_duration(self, hours: int) -> None:
        """Update cache duration."""
        if hours <= 0:
            raise ValueError("Cache duration must be positive")
        
        os.environ['TUFU_CACHE_DURATION_HOURS'] = str(hours)
    
    def update_rate_limit_delay(self, seconds: float) -> None:
        """Update rate limit delay."""
        if seconds < 0:
            raise ValueError("Rate limit delay must be non-negative")
        
        os.environ['TUFU_RATE_LIMIT_DELAY_SECONDS'] = str(seconds)
    
    def enable_debug_mode(self) -> None:
        """Enable debug mode."""
        os.environ['TUFU_DEBUG_MODE'] = 'true'
    
    def disable_debug_mode(self) -> None:
        """Disable debug mode."""
        os.environ['TUFU_DEBUG_MODE'] = 'false'
    
    def set_log_level(self, level: str) -> None:
        """Set logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        
        os.environ['TUFU_LOG_LEVEL'] = level.upper()
    
    def get_environment_variables(self) -> dict:
        """Get all TÜFE-related environment variables."""
        tufe_vars = {}
        for key, value in os.environ.items():
            if key.startswith('TCMB_') or key.startswith('TUFU_'):
                tufe_vars[key] = value
        return tufe_vars
    
    def validate_configuration(self) -> dict:
        """Validate the current configuration."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check API key
        if not self.is_api_key_configured():
            validation_results["errors"].append("TCMB API key is not configured")
            validation_results["valid"] = False
        elif not self.validate_api_key():
            validation_results["warnings"].append("TCMB API key is configured but not valid")
        
        # Check cache duration
        cache_duration = self.get_cache_duration_hours()
        if cache_duration <= 0:
            validation_results["errors"].append("Cache duration must be positive")
            validation_results["valid"] = False
        elif cache_duration > 168:  # More than a week
            validation_results["warnings"].append("Cache duration is very long (>1 week)")
        
        # Check rate limit delay
        rate_delay = self.get_rate_limit_delay()
        if rate_delay < 0:
            validation_results["errors"].append("Rate limit delay must be non-negative")
            validation_results["valid"] = False
        elif rate_delay > 10:
            validation_results["warnings"].append("Rate limit delay is very long (>10 seconds)")
        
        # Check log level
        log_level = self.get_log_level()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_levels:
            validation_results["errors"].append(f"Invalid log level: {log_level}")
            validation_results["valid"] = False
        
        return validation_results
