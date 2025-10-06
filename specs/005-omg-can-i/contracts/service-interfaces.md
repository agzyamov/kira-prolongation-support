# Service Interfaces: Easy TÜFE Data Fetching

**Feature**: 005-omg-can-i  
**Date**: 2025-01-27  
**Status**: Complete

## Overview

This document defines the service interfaces for easy TÜFE data fetching using OECD API. The interfaces extend existing services while adding new components for rate limiting and enhanced caching.

## Existing Services (Extended)

### InflationService
**Purpose**: Extended to support OECD API integration

**New Methods**:
```python
def fetch_tufe_from_oecd_api(self, start_year: int, end_year: int) -> List[InflationData]:
    """
    Fetch TÜFE data from OECD API for specified year range.
    
    Args:
        start_year: Starting year (2000-2025)
        end_year: Ending year (2000-2025)
    
    Returns:
        List of InflationData objects with TÜFE rates
    
    Raises:
        TufeApiError: If API request fails
        TufeValidationError: If data validation fails
    """

def get_oecd_tufe_data(self, year: int, month: int = None) -> Optional[InflationData]:
    """
    Get TÜFE data from OECD API for specific year/month.
    
    Args:
        year: Year (2000-2025)
        month: Month (1-12), optional for yearly data
    
    Returns:
        InflationData object or None if not found
    
    Raises:
        TufeApiError: If API request fails
    """

def is_oecd_data_available(self, year: int, month: int = None) -> bool:
    """
    Check if OECD TÜFE data is available for specified period.
    
    Args:
        year: Year (2000-2025)
        month: Month (1-12), optional
    
    Returns:
        True if data is available, False otherwise
    """
```

### TufeCacheService
**Purpose**: Enhanced caching with TTL support

**New Methods**:
```python
def cache_oecd_data(self, data: List[InflationData], ttl_hours: int = 168) -> None:
    """
    Cache OECD TÜFE data with specified TTL.
    
    Args:
        data: List of InflationData objects to cache
        ttl_hours: Time to live in hours (default: 168 = 7 days)
    
    Raises:
        TufeCacheError: If caching fails
    """

def get_cached_oecd_data(self, year: int, month: int = None) -> Optional[InflationData]:
    """
    Get cached OECD TÜFE data for specified period.
    
    Args:
        year: Year (2000-2025)
        month: Month (1-12), optional
    
    Returns:
        Cached InflationData or None if not found/expired
    """

def cleanup_expired_cache(self) -> int:
    """
    Remove expired cache entries.
    
    Returns:
        Number of entries removed
    """

def get_cache_statistics(self) -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache stats (total entries, expired, hit rate, etc.)
    """
```

## New Services

### OECDApiClient
**Purpose**: Dedicated client for OECD SDMX API

**Interface**:
```python
class OECDApiClient:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize OECD API client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
    
    def fetch_tufe_data(self, start_year: int, end_year: int) -> Dict[str, Any]:
        """
        Fetch TÜFE data from OECD API.
        
        Args:
            start_year: Starting year (2000-2025)
            end_year: Ending year (2000-2025)
        
        Returns:
            Dictionary with raw API response data
        
        Raises:
            TufeApiError: If API request fails
            TufeValidationError: If response validation fails
        """
    
    def parse_sdmx_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Parse SDMX XML response into structured data.
        
        Args:
            xml_content: Raw XML response from OECD API
        
        Returns:
            List of dictionaries with parsed TÜFE data
        
        Raises:
            TufeValidationError: If XML parsing fails
        """
    
    def validate_response(self, response: requests.Response) -> None:
        """
        Validate API response.
        
        Args:
            response: HTTP response object
        
        Raises:
            TufeApiError: If response is invalid
        """
    
    def get_rate_limit_info(self, response: requests.Response) -> Dict[str, Any]:
        """
        Extract rate limit information from response headers.
        
        Args:
            response: HTTP response object
        
        Returns:
            Dictionary with rate limit information
        """
```

### RateLimitHandler
**Purpose**: Manages API rate limiting and backoff

**Interface**:
```python
class RateLimitHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize rate limit handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
        """
    
    def should_retry(self, attempt: int, response: requests.Response) -> bool:
        """
        Determine if request should be retried.
        
        Args:
            attempt: Current attempt number (0-based)
            response: HTTP response object
        
        Returns:
            True if request should be retried, False otherwise
        """
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt.
        
        Args:
            attempt: Current attempt number (0-based)
        
        Returns:
            Delay in seconds
        """
    
    def add_jitter(self, delay: float) -> float:
        """
        Add randomization to delay to avoid thundering herd.
        
        Args:
            delay: Base delay in seconds
        
        Returns:
            Jittered delay in seconds
        """
    
    def is_rate_limited(self, response: requests.Response) -> bool:
        """
        Check if response indicates rate limiting.
        
        Args:
            response: HTTP response object
        
        Returns:
            True if rate limited, False otherwise
        """
```

### DataValidator
**Purpose**: Validates fetched TÜFE data

**Interface**:
```python
class DataValidator:
    def __init__(self, min_rate: float = 0.0, max_rate: float = 200.0):
        """
        Initialize data validator.
        
        Args:
            min_rate: Minimum valid TÜFE rate (percentage)
            max_rate: Maximum valid TÜFE rate (percentage)
        """
    
    def validate_tufe_rate(self, rate: float) -> None:
        """
        Validate TÜFE rate value.
        
        Args:
            rate: TÜFE rate to validate
        
        Raises:
            TufeValidationError: If rate is invalid
        """
    
    def validate_year(self, year: int) -> None:
        """
        Validate year value.
        
        Args:
            year: Year to validate
        
        Raises:
            TufeValidationError: If year is invalid
        """
    
    def validate_month(self, month: int) -> None:
        """
        Validate month value.
        
        Args:
            month: Month to validate
        
        Raises:
            TufeValidationError: If month is invalid
        """
    
    def validate_data_source(self, source: str) -> None:
        """
        Validate data source.
        
        Args:
            source: Data source to validate
        
        Raises:
            TufeValidationError: If source is invalid
        """
    
    def validate_complete_record(self, year: int, month: int, rate: float, source: str) -> None:
        """
        Validate complete TÜFE record.
        
        Args:
            year: Year
            month: Month
            rate: TÜFE rate
            source: Data source
        
        Raises:
            TufeValidationError: If any field is invalid
        """
```

## Error Handling

### Exception Hierarchy
```python
class TufeApiError(Exception):
    """Base exception for TÜFE API errors"""
    pass

class TufeValidationError(TufeApiError):
    """Exception for data validation errors"""
    pass

class TufeRateLimitError(TufeApiError):
    """Exception for rate limiting errors"""
    pass

class TufeNetworkError(TufeApiError):
    """Exception for network-related errors"""
    pass
```

### Error Response Format
```python
{
    "error": "TufeApiError",
    "message": "Human-readable error message",
    "code": "ERROR_CODE",
    "details": {
        "attempt": 1,
        "max_retries": 3,
        "retry_after": 60,
        "endpoint": "https://stats.oecd.org/...",
        "status_code": 429
    },
    "timestamp": "2025-01-27T10:30:00Z"
}
```

## Integration Points

### Streamlit UI Integration
```python
# In app.py
def render_tufe_fetch_ui():
    """Render TÜFE data fetching UI"""
    st.subheader("TÜFE Data Fetching")
    
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Year", range(2000, 2026), index=len(range(2000, 2026))-1)
    with col2:
        month = st.selectbox("Month", range(1, 13), index=0)
    
    if st.button("Fetch TÜFE Data from OECD API"):
        try:
            with st.spinner("Fetching TÜFE data..."):
                data = services['inflation_service'].fetch_tufe_from_oecd_api(year, year)
                if data:
                    st.success(f"Successfully fetched TÜFE data for {year}")
                    # Display data
                else:
                    st.warning("No data found for the specified period")
        except TufeApiError as e:
            st.error(f"API Error: {e.message}")
            st.info("You can enter TÜFE data manually below.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
```

### Service Initialization
```python
# In app.py init_services()
def init_services():
    """Initialize all services"""
    # ... existing services ...
    
    # New OECD API services
    services['oecd_api_client'] = OECDApiClient(timeout=30, max_retries=3)
    services['rate_limit_handler'] = RateLimitHandler(max_retries=3, base_delay=1.0)
    services['data_validator'] = DataValidator(min_rate=0.0, max_rate=200.0)
    
    # Enhanced existing services
    services['inflation_service'] = InflationService(
        data_store=services['data_store'],
        oecd_client=services['oecd_api_client'],
        rate_limit_handler=services['rate_limit_handler'],
        validator=services['data_validator']
    )
```

## Testing Contracts

### Unit Test Requirements
- **OECDApiClient**: Test API calls, response parsing, error handling
- **RateLimitHandler**: Test backoff logic, jitter, rate limit detection
- **DataValidator**: Test validation rules, error conditions
- **InflationService**: Test integration, caching, fallback behavior

### Integration Test Requirements
- **End-to-end**: Test complete fetch flow from UI to database
- **Error scenarios**: Test network failures, rate limiting, invalid data
- **Caching**: Test cache hit/miss, expiration, cleanup
- **Performance**: Test response times, memory usage

### Contract Test Requirements
- **Service interfaces**: Verify all methods exist and have correct signatures
- **Error handling**: Verify proper exception types and messages
- **Data validation**: Verify validation rules are enforced
- **Rate limiting**: Verify backoff behavior and retry logic