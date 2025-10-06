"""
OECD API Configuration for TÜFE Data Fetching

This module contains configuration constants for OECD API integration,
including rate limiting, retry logic, and data validation parameters.
"""

# OECD API Configuration
OECD_BASE_URL = "https://stats.oecd.org/restsdmx/sdmx.ashx"
OECD_DATASET = "PRICES_CPI"
OECD_SERIES_KEY = "A.TUR.CPALTT01.M"  # Annual, Turkey, All-items CPI, Monthly
OECD_FULL_ENDPOINT = f"{OECD_BASE_URL}/GetData/{OECD_DATASET}/{OECD_SERIES_KEY}/all"

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    "max_requests_per_hour": 100,
    "max_requests_per_day": 1000,
    "base_delay_seconds": 1.0,
    "max_delay_seconds": 60.0,
    "backoff_factor": 2.0,
    "jitter_range": 0.25,  # ±25% randomization
    "max_retries": 3,
    "timeout_seconds": 30
}

# Data Validation Configuration
VALIDATION_CONFIG = {
    "min_tufe_rate": 0.0,      # Minimum valid TÜFE rate (percentage)
    "max_tufe_rate": 200.0,    # Maximum valid TÜFE rate (percentage)
    "min_year": 2000,          # Minimum valid year
    "max_year_offset": 1,      # Maximum years in the future (current_year + offset)
    "valid_months": list(range(1, 13)),  # Valid months (1-12)
    "required_source": "OECD SDMX API"
}

# Caching Configuration
CACHE_CONFIG = {
    "recent_data_ttl_hours": 168,    # 7 days for recent data
    "historical_data_ttl_hours": 720, # 30 days for historical data
    "failed_request_ttl_hours": 1,   # 1 hour for failed requests
    "cleanup_interval_hours": 24     # Cleanup expired entries daily
}

# Error Handling Configuration
ERROR_CONFIG = {
    "retryable_status_codes": [429, 500, 502, 503, 504],  # HTTP status codes to retry
    "non_retryable_status_codes": [400, 401, 403, 404],   # HTTP status codes not to retry
    "connection_error_retry": True,                        # Retry on connection errors
    "timeout_error_retry": True,                          # Retry on timeout errors
    "max_consecutive_failures": 5                         # Max failures before marking source as failed
}

# SDMX XML Parsing Configuration
SDMX_CONFIG = {
    "namespaces": {
        'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
        'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
        'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common',
        'compact': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/compact'
    },
    "target_country": "TUR",           # Turkey country code
    "target_measure": "CPI",           # Consumer Price Index
    "target_frequency": "M",           # Monthly frequency
    "target_unit": "PA"                # Percentage Annual
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "target_response_time_seconds": 2.0,    # Target API response time
    "target_cache_response_time_ms": 500,   # Target cache response time
    "max_concurrent_requests": 1,           # Max concurrent API requests
    "request_batch_size": 5,                # Max years to fetch in single request
    "memory_usage_limit_mb": 100            # Max memory usage for data processing
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_api_requests": True,               # Log all API requests
    "log_response_times": True,             # Log response times
    "log_rate_limit_info": True,            # Log rate limit information
    "log_cache_hits": True,                 # Log cache hit/miss statistics
    "log_validation_errors": True,          # Log data validation errors
    "log_level": "INFO"                     # Logging level
}

# User Interface Configuration
UI_CONFIG = {
    "show_progress_bar": True,              # Show progress during data fetching
    "show_cache_status": True,              # Show cache hit/miss status
    "show_rate_limit_status": True,         # Show rate limit information
    "show_data_source_attribution": True,   # Show data source in results
    "enable_manual_entry_fallback": True,   # Allow manual data entry as fallback
    "auto_refresh_interval_seconds": 300    # Auto-refresh data every 5 minutes
}

# Development/Testing Configuration
DEV_CONFIG = {
    "mock_api_responses": False,            # Use mock responses for testing
    "mock_response_delay_ms": 100,          # Simulated response delay
    "mock_error_rate": 0.0,                 # Simulated error rate (0.0-1.0)
    "enable_debug_logging": False,          # Enable detailed debug logging
    "test_mode": False                      # Enable test mode features
}

def get_current_year():
    """Get the current year for validation purposes."""
    from datetime import datetime
    return datetime.now().year

def get_max_valid_year():
    """Get the maximum valid year for TÜFE data."""
    return get_current_year() + VALIDATION_CONFIG["max_year_offset"]

def get_cache_ttl_hours(year):
    """Get cache TTL in hours based on data age."""
    current_year = get_current_year()
    if year >= current_year:
        return CACHE_CONFIG["recent_data_ttl_hours"]
    else:
        return CACHE_CONFIG["historical_data_ttl_hours"]

def is_retryable_error(status_code, error_type=None):
    """Check if an error should be retried."""
    if status_code in ERROR_CONFIG["retryable_status_codes"]:
        return True
    if status_code in ERROR_CONFIG["non_retryable_status_codes"]:
        return False
    if error_type == "connection" and ERROR_CONFIG["connection_error_retry"]:
        return True
    if error_type == "timeout" and ERROR_CONFIG["timeout_error_retry"]:
        return True
    return False

def get_retry_delay(attempt):
    """Calculate delay for retry attempt with exponential backoff."""
    delay = RATE_LIMIT_CONFIG["base_delay_seconds"] * (RATE_LIMIT_CONFIG["backoff_factor"] ** attempt)
    return min(delay, RATE_LIMIT_CONFIG["max_delay_seconds"])

def add_jitter(delay):
    """Add jitter to delay to avoid thundering herd."""
    import random
    jitter_range = RATE_LIMIT_CONFIG["jitter_range"]
    jitter = random.uniform(-jitter_range, jitter_range)
    return delay * (1 + jitter)
