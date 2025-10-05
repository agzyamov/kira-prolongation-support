"""
Configuration management for TÜFE data sources.
"""
import os
from typing import Optional

class TufeConfig:
    """Configuration class for TÜFE data source settings."""
    
    # Static configuration
    TCMB_BASE_URL: str = "https://evds2.tcmb.gov.tr/service/evds/"
    TCMB_SERIES_CODE: str = "TP.FE.OKTG01"
    TCMB_DATA_FORMAT: str = "json"
    
    # API Limits
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 10
    
    @classmethod
    def get_tcmb_api_key(cls) -> Optional[str]:
        """Get TCMB API key from environment or return None."""
        return os.getenv('TCMB_API_KEY')
    
    @classmethod
    def set_tcmb_api_key(cls, api_key: str) -> None:
        """Set TCMB API key in environment."""
        os.environ['TCMB_API_KEY'] = api_key
    
    @classmethod
    def is_api_key_configured(cls) -> bool:
        """Check if TCMB API key is configured."""
        api_key = cls.get_tcmb_api_key()
        return api_key is not None and api_key.strip() != ""
    
    @classmethod
    def get_cache_duration_hours(cls) -> int:
        """Get cache duration in hours."""
        return int(os.getenv('TUFU_CACHE_DURATION_HOURS', '24'))
    
    @classmethod
    def get_rate_limit_delay(cls) -> float:
        """Get delay between API calls in seconds."""
        return float(os.getenv('TUFU_RATE_LIMIT_DELAY_SECONDS', '1.0'))
    
    @classmethod
    def is_debug_mode(cls) -> bool:
        """Check if debug mode is enabled."""
        return os.getenv('TUFU_DEBUG_MODE', 'false').lower() == 'true'
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get logging level for TÜFE operations."""
        return os.getenv('TUFU_LOG_LEVEL', 'INFO')
