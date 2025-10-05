# Service Interfaces: Secure TÜFE Data Sources

**Feature**: Research and Implement Secure TÜFE Data Sources  
**Date**: 2025-10-05  
**Branch**: 004-tufe-data-sources

## Service Extensions

### InflationService (Extended)
**File**: `src/services/inflation_service.py`

**New Methods**:
```python
def fetch_tufe_from_tcmb_api(self, year: int, api_key: str) -> Optional[Decimal]:
    """
    Fetch TÜFE data from TCMB EVDS API.
    
    Args:
        year: Year to fetch TÜFE for
        api_key: TCMB EVDS API key
        
    Returns:
        TÜFE rate as Decimal or None if not available
        
    Raises:
        TufeApiError: If API call fails
        TufeValidationError: If data validation fails
    """

def get_tufe_data_sources(self) -> List[TufeDataSource]:
    """
    Get all available TÜFE data sources.
    
    Returns:
        List of TufeDataSource objects
    """

def get_active_tufe_source(self) -> Optional[TufeDataSource]:
    """
    Get the currently active TÜFE data source.
    
    Returns:
        Active TufeDataSource or None if none active
    """

def cache_tufe_data(self, year: int, rate: Decimal, source: str, api_response: str) -> int:
    """
    Cache TÜFE data with source attribution.
    
    Args:
        year: Year of the data
        rate: TÜFE rate
        source: Data source name
        api_response: Raw API response
        
    Returns:
        Cache entry ID
    """

def get_cached_tufe_data(self, year: int) -> Optional[TufeDataCache]:
    """
    Get cached TÜFE data for a year.
    
    Args:
        year: Year to get cached data for
        
    Returns:
        TufeDataCache object or None if not cached
    """

def is_tufe_cache_valid(self, year: int) -> bool:
    """
    Check if cached TÜFE data is still valid.
    
    Args:
        year: Year to check cache for
        
    Returns:
        True if cache is valid and not expired
    """

def validate_tufe_data(self, rate: Decimal, year: int) -> bool:
    """
    Validate TÜFE data before storage.
    
    Args:
        rate: TÜFE rate to validate
        year: Year for context
        
    Returns:
        True if data is valid
        
    Raises:
        TufeValidationError: If data is invalid
    """
```

## New Services

### TufeDataSourceService
**File**: `src/services/tufe_data_source_service.py`

**Methods**:
```python
def __init__(self, data_store: DataStore):
    """Initialize with DataStore."""

def get_all_sources(self) -> List[TufeDataSource]:
    """Get all TÜFE data sources."""

def get_active_source(self) -> Optional[TufeDataSource]:
    """Get the currently active data source."""

def add_source(self, source: TufeDataSource) -> int:
    """Add a new data source."""

def update_source(self, source_id: int, source: TufeDataSource) -> bool:
    """Update an existing data source."""

def deactivate_source(self, source_id: int) -> bool:
    """Deactivate a data source."""

def verify_source(self, source_id: int) -> bool:
    """Verify that a data source is working."""

def get_source_by_id(self, source_id: int) -> Optional[TufeDataSource]:
    """Get a data source by ID."""
```

### TufeApiKeyService
**File**: `src/services/tufe_api_key_service.py`

**Methods**:
```python
def __init__(self, data_store: DataStore):
    """Initialize with DataStore."""

def get_api_key(self, source_id: int) -> Optional[str]:
    """Get decrypted API key for a data source."""

def set_api_key(self, source_id: int, key_name: str, api_key: str) -> int:
    """Set encrypted API key for a data source."""

def update_api_key(self, key_id: int, api_key: str) -> bool:
    """Update an existing API key."""

def deactivate_api_key(self, key_id: int) -> bool:
    """Deactivate an API key."""

def get_keys_for_source(self, source_id: int) -> List[TufeApiKey]:
    """Get all API keys for a data source."""

def record_api_usage(self, key_id: int) -> None:
    """Record API key usage timestamp."""
```

### TufeCacheService
**File**: `src/services/tufe_cache_service.py`

**Methods**:
```python
def __init__(self, data_store: DataStore):
    """Initialize with DataStore."""

def get_cached_data(self, year: int) -> Optional[TufeDataCache]:
    """Get cached TÜFE data for a year."""

def cache_data(self, year: int, rate: Decimal, source: str, api_response: str) -> int:
    """Cache TÜFE data with expiration."""

def is_cache_valid(self, year: int) -> bool:
    """Check if cached data is still valid."""

def invalidate_cache(self, year: int) -> bool:
    """Invalidate cached data for a year."""

def cleanup_expired_cache(self) -> int:
    """Remove expired cache entries."""

def get_cache_stats(self) -> Dict[str, int]:
    """Get cache statistics."""

def get_data_lineage(self, year: int) -> Optional[str]:
    """Get data source lineage for a year."""
```

## New Exception Classes

### TufeApiError
**File**: `src/services/exceptions.py`

```python
class TufeApiError(ServiceError):
    """Raised when TÜFE API calls fail"""
    pass
```

### TufeValidationError
**File**: `src/services/exceptions.py`

```python
class TufeValidationError(ServiceError):
    """Raised when TÜFE data validation fails"""
    pass
```

### TufeCacheError
**File**: `src/services/exceptions.py`

```python
class TufeCacheError(ServiceError):
    """Raised when TÜFE cache operations fail"""
    pass
```

## API Integration Patterns

### TCMB EVDS API Client
**File**: `src/services/tcmb_api_client.py`

**Methods**:
```python
def __init__(self, api_key: str):
    """Initialize with TCMB API key."""

def fetch_tufe_data(self, year: int) -> Dict[str, Any]:
    """
    Fetch TÜFE data from TCMB EVDS API.
    
    Args:
        year: Year to fetch data for
        
    Returns:
        API response as dictionary
        
    Raises:
        TufeApiError: If API call fails
    """

def validate_api_key(self) -> bool:
    """Validate that the API key is working."""

def get_rate_limit_status(self) -> Dict[str, Any]:
    """Get current rate limit status."""

def build_api_url(self, year: int) -> str:
    """Build TCMB API URL for given year."""
```

## Configuration Management

### TufeConfigService
**File**: `src/services/tufe_config_service.py`

**Methods**:
```python
def __init__(self):
    """Initialize configuration service."""

def get_tcmb_api_key(self) -> Optional[str]:
    """Get TCMB API key from environment or config."""

def set_tcmb_api_key(self, api_key: str) -> None:
    """Set TCMB API key in configuration."""

def get_cache_duration_hours(self) -> int:
    """Get cache duration in hours."""

def get_rate_limit_delay(self) -> float:
    """Get delay between API calls in seconds."""

def is_debug_mode(self) -> bool:
    """Check if debug mode is enabled."""

def get_log_level(self) -> str:
    """Get logging level for TÜFE operations."""
```

## Error Handling Patterns

### API Error Handling
```python
def handle_api_error(self, error: Exception) -> None:
    """
    Handle API errors with appropriate logging and user feedback.
    
    Args:
        error: The exception that occurred
    """
    if isinstance(error, requests.Timeout):
        raise TufeApiError("API request timed out")
    elif isinstance(error, requests.ConnectionError):
        raise TufeApiError("Unable to connect to TCMB API")
    elif isinstance(error, requests.HTTPError):
        if error.response.status_code == 401:
            raise TufeApiError("Invalid API key")
        elif error.response.status_code == 429:
            raise TufeApiError("Rate limit exceeded")
        else:
            raise TufeApiError(f"API error: {error.response.status_code}")
    else:
        raise TufeApiError(f"Unexpected error: {str(error)}")
```

### Data Validation Patterns
```python
def validate_tufe_response(self, response: Dict[str, Any]) -> Decimal:
    """
    Validate TÜFE API response data.
    
    Args:
        response: API response dictionary
        
    Returns:
        Validated TÜFE rate as Decimal
        
    Raises:
        TufeValidationError: If data is invalid
    """
    # Implementation details for validation
```

## Integration Points

### Streamlit UI Integration
- API key configuration in settings
- Data source selection dropdown
- Cache status display
- Manual refresh button
- Error message display

### Export Service Integration
- Include data source attribution in exports
- Show cache status in summaries
- Display API fetch timestamps

### Chart Generator Integration
- Show data source in chart annotations
- Display cache validity in tooltips
- Include source attribution in chart titles
