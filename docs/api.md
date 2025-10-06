# API Documentation: OECD TÜFE Integration

**Version**: 1.0.0  
**Date**: 2025-01-27  
**Feature**: 005-omg-can-i

## Overview

This document provides API documentation for the OECD TÜFE data integration services. These services enable easy fetching of Turkish inflation data from the OECD SDMX API with automatic caching and rate limiting.

## Services

### OECDApiClient

**Purpose**: Dedicated client for OECD SDMX API integration

**Location**: `src/services/oecd_api_client.py`

#### Methods

##### `fetch_tufe_data(start_year: int, end_year: int) -> Dict[str, Any]`

Fetches TÜFE data from OECD API for specified year range.

**Parameters**:
- `start_year` (int): Starting year (2000-2025)
- `end_year` (int): Ending year (2000-2025)

**Returns**:
- `Dict[str, Any]`: Dictionary containing fetched data with 'items' key

**Raises**:
- `OECDApiError`: If API request fails
- `OECDDataParseError`: If XML response cannot be parsed

**Example**:
```python
from src.services.oecd_api_client import OECDApiClient

client = OECDApiClient()
data = client.fetch_tufe_data(2023, 2024)
print(f"Fetched {len(data['items'])} data points")
```

##### `is_healthy() -> bool`

Checks the health of the OECD API.

**Returns**:
- `bool`: True if API is reachable, False otherwise

**Example**:
```python
if client.is_healthy():
    print("OECD API is accessible")
else:
    print("OECD API is not reachable")
```

##### `get_api_info() -> Dict[str, Any]`

Provides basic information about the OECD API client.

**Returns**:
- `Dict[str, Any]`: API client details

**Example**:
```python
info = client.get_api_info()
print(f"API: {info['name']}")
print(f"Endpoint: {info['base_url']}")
```

### RateLimitHandler

**Purpose**: Manages API rate limiting and implements exponential backoff

**Location**: `src/services/rate_limit_handler.py`

#### Methods

##### `check_request_allowed(source_id: int) -> bool`

Checks if a request is allowed for a given source.

**Parameters**:
- `source_id` (int): The ID of the data source

**Returns**:
- `bool`: True if request is allowed, False otherwise

**Example**:
```python
from src.services.rate_limit_handler import RateLimitHandler

handler = RateLimitHandler()
if handler.check_request_allowed(source_id=1):
    # Make API request
    pass
else:
    print("Rate limit exceeded, please wait")
```

##### `record_request(source_id: int, is_success: bool, response_time: float = 0.0, status_code: Optional[int] = None, error_message: Optional[str] = None)`

Records an API request for tracking and rate limiting.

**Parameters**:
- `source_id` (int): The ID of the data source
- `is_success` (bool): True if request was successful
- `response_time` (float): Request duration in seconds
- `status_code` (Optional[int]): HTTP status code
- `error_message` (Optional[str]): Error message if request failed

**Example**:
```python
handler.record_request(
    source_id=1,
    is_success=True,
    response_time=1.5,
    status_code=200
)
```

##### `apply_backoff(attempt: int, max_retries: int, base_delay: float = 1.0)`

Applies exponential backoff delay with jitter.

**Parameters**:
- `attempt` (int): Current retry attempt (0-indexed)
- `max_retries` (int): Maximum number of retries
- `base_delay` (float): Base delay in seconds

**Raises**:
- `RateLimitExceededError`: If max retries exceeded

**Example**:
```python
for attempt in range(max_retries):
    try:
        # Make API request
        break
    except Exception:
        handler.apply_backoff(attempt, max_retries)
```

##### `get_rate_limit_status(source_id: int) -> Dict[str, Any]`

Gets current rate limit status for a source.

**Parameters**:
- `source_id` (int): The ID of the data source

**Returns**:
- `Dict[str, Any]`: Rate limit status information

**Example**:
```python
status = handler.get_rate_limit_status(source_id=1)
print(f"Can make request: {status['can_make_request']}")
print(f"Remaining: {status['remaining_hour']} per hour")
```

### DataValidator

**Purpose**: Validates fetched TÜFE data

**Location**: `src/services/data_validator.py`

#### Methods

##### `validate_tufe_rate(tufe_rate: float, min_rate: float = 0.0, max_rate: float = 200.0)`

Validates a TÜFE rate value.

**Parameters**:
- `tufe_rate` (float): The TÜFE rate to validate
- `min_rate` (float): Minimum acceptable rate (default: 0.0)
- `max_rate` (float): Maximum acceptable rate (default: 200.0)

**Raises**:
- `TufeValidationError`: If rate is outside valid range

**Example**:
```python
from src.services.data_validator import DataValidator

validator = DataValidator()
try:
    validator.validate_tufe_rate(10.5)
    print("Rate is valid")
except TufeValidationError as e:
    print(f"Invalid rate: {e}")
```

##### `validate_year_month(year: int, month: int)`

Validates year and month combination.

**Parameters**:
- `year` (int): Year to validate
- `month` (int): Month to validate

**Raises**:
- `TufeValidationError`: If year or month is invalid

**Example**:
```python
validator.validate_year_month(2024, 1)  # Valid
validator.validate_year_month(2024, 13)  # Raises TufeValidationError
```

##### `validate_complete_record(year: int, month: int, tufe_rate: float, source: str)`

Validates a complete TÜFE data record.

**Parameters**:
- `year` (int): Year of the record
- `month` (int): Month of the record
- `tufe_rate` (float): TÜFE rate
- `source` (str): Data source

**Raises**:
- `TufeValidationError`: If any field is invalid

**Example**:
```python
validator.validate_complete_record(
    year=2024,
    month=1,
    tufe_rate=10.5,
    source="OECD SDMX API"
)
```

##### `validate_batch_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

Validates a batch of TÜFE data records.

**Parameters**:
- `data` (List[Dict[str, Any]]): List of data records to validate

**Returns**:
- `List[Dict[str, Any]]`: List of valid records only

**Example**:
```python
raw_data = [
    {"year": 2024, "month": 1, "value": 10.5, "source": "OECD SDMX API"},
    {"year": 2024, "month": 2, "value": 11.0, "source": "OECD SDMX API"}
]

valid_data = validator.validate_batch_data(raw_data)
print(f"Validated {len(valid_data)} records")
```

### Enhanced InflationService

**Purpose**: Extended to support OECD API integration

**Location**: `src/services/inflation_service.py`

#### New Methods

##### `fetch_tufe_from_oecd_api(start_year: int, end_year: int) -> List[InflationData]`

Fetches TÜFE data from OECD API for specified year range.

**Parameters**:
- `start_year` (int): Starting year (2000-2025)
- `end_year` (int): Ending year (2000-2025)

**Returns**:
- `List[InflationData]`: List of InflationData objects

**Raises**:
- `TufeApiError`: If API request fails
- `TufeValidationError`: If data validation fails

**Example**:
```python
from src.services.inflation_service import InflationService

service = InflationService(data_store)
data = service.fetch_tufe_from_oecd_api(2023, 2024)
for item in data:
    print(f"{item.year}-{item.month}: {item.tufe_rate}%")
```

##### `fetch_and_cache_oecd_tufe_data(start_year: int, end_year: int) -> List[InflationData]`

Fetches TÜFE data from OECD API and caches it.

**Parameters**:
- `start_year` (int): Starting year (2000-2025)
- `end_year` (int): Ending year (2000-2025)

**Returns**:
- `List[InflationData]`: List of InflationData objects

**Example**:
```python
data = service.fetch_and_cache_oecd_tufe_data(2023, 2024)
print(f"Cached {len(data)} records")
```

##### `get_cached_oecd_tufe_data(year: int, month: int = None) -> Optional[InflationData]`

Gets cached OECD TÜFE data.

**Parameters**:
- `year` (int): Year to retrieve
- `month` (int): Month to retrieve (optional)

**Returns**:
- `Optional[InflationData]`: Cached data or None if not found

**Example**:
```python
cached_data = service.get_cached_oecd_tufe_data(2024, 1)
if cached_data:
    print(f"Cached rate: {cached_data.tufe_rate}%")
else:
    print("No cached data found")
```

##### `is_oecd_api_healthy() -> bool`

Checks if OECD API is healthy.

**Returns**:
- `bool`: True if API is healthy, False otherwise

**Example**:
```python
if service.is_oecd_api_healthy():
    print("OECD API is accessible")
else:
    print("OECD API is not reachable")
```

##### `get_rate_limit_status() -> dict`

Gets rate limit status.

**Returns**:
- `dict`: Rate limit status information

**Example**:
```python
status = service.get_rate_limit_status()
print(f"Can make request: {status['can_make_request']}")
```

### Enhanced TufeCacheService

**Purpose**: Enhanced caching with TTL support

**Location**: `src/services/tufe_cache_service.py`

#### New Methods

##### `cache_oecd_data(inflation_data: List[InflationData], ttl_hours: int = None) -> int`

Caches OECD TÜFE data with TTL support.

**Parameters**:
- `inflation_data` (List[InflationData]): Data to cache
- `ttl_hours` (int): TTL in hours (default from config)

**Returns**:
- `int`: Number of items cached

**Raises**:
- `TufeCacheError`: If caching fails
- `TufeValidationError`: If data validation fails

**Example**:
```python
from src.services.tufe_cache_service import TufeCacheService

cache_service = TufeCacheService(data_store)
cached_count = cache_service.cache_oecd_data(data, ttl_hours=24)
print(f"Cached {cached_count} items")
```

##### `get_cached_oecd_data(year: int, month: int = None) -> Optional[InflationData]`

Gets cached OECD TÜFE data.

**Parameters**:
- `year` (int): Year to retrieve
- `month` (int): Month to retrieve (optional)

**Returns**:
- `Optional[InflationData]`: Cached data or None if not found

**Example**:
```python
cached_data = cache_service.get_cached_oecd_data(2024, 1)
if cached_data:
    print(f"Found cached data: {cached_data.tufe_rate}%")
```

##### `cleanup_expired_cache() -> int`

Removes expired cache entries.

**Returns**:
- `int`: Number of entries removed

**Example**:
```python
removed_count = cache_service.cleanup_expired_cache()
print(f"Removed {removed_count} expired entries")
```

##### `get_cache_statistics() -> dict`

Gets detailed cache statistics.

**Returns**:
- `dict`: Cache statistics

**Example**:
```python
stats = cache_service.get_cache_statistics()
print(f"Total entries: {stats['total_entries']}")
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

## Exception Classes

### OECDApiError

**Purpose**: Base exception for OECD API errors

**Location**: `src/services/exceptions.py`

**Example**:
```python
from src.services.exceptions import OECDApiError

try:
    data = client.fetch_tufe_data(2024, 2024)
except OECDApiError as e:
    print(f"API Error: {e}")
```

### OECDDataParseError

**Purpose**: Exception for OECD data parsing errors

**Location**: `src/services/exceptions.py`

**Example**:
```python
from src.services.exceptions import OECDDataParseError

try:
    parsed_data = client.parse_xml_response(xml_content)
except OECDDataParseError as e:
    print(f"Parse Error: {e}")
```

### RateLimitExceededError

**Purpose**: Exception for rate limit exceeded

**Location**: `src/services/exceptions.py`

**Example**:
```python
from src.services.exceptions import RateLimitExceededError

try:
    handler.apply_backoff(attempt, max_retries)
except RateLimitExceededError as e:
    print(f"Rate limit exceeded: {e}")
```

### TufeValidationError

**Purpose**: Exception for TÜFE data validation errors

**Location**: `src/services/exceptions.py`

**Example**:
```python
from src.services.exceptions import TufeValidationError

try:
    validator.validate_tufe_rate(rate)
except TufeValidationError as e:
    print(f"Validation Error: {e}")
```

## Configuration

### OECD API Configuration

**Location**: `src/config/oecd_config.py`

**Constants**:
- `OECD_API_ENDPOINT`: OECD API endpoint URL
- `OECD_SERIES_CODE`: Series code for Turkish CPI data
- `OECD_DATA_FORMAT`: Data format (xml)
- `DEFAULT_MAX_REQUESTS_PER_HOUR`: Default rate limit (100)
- `DEFAULT_MAX_REQUESTS_PER_DAY`: Default daily limit (1000)
- `DEFAULT_BACKOFF_FACTOR`: Exponential backoff factor (2.0)
- `DEFAULT_MAX_RETRIES`: Maximum retry attempts (3)

**Example**:
```python
from src.config.oecd_config import OECD_API_ENDPOINT, DEFAULT_MAX_REQUESTS_PER_HOUR

print(f"API Endpoint: {OECD_API_ENDPOINT}")
print(f"Rate Limit: {DEFAULT_MAX_REQUESTS_PER_HOUR} requests/hour")
```

## Usage Examples

### Basic Data Fetching

```python
from src.services.inflation_service import InflationService
from src.storage.data_store import DataStore

# Initialize services
data_store = DataStore()
inflation_service = InflationService(data_store)

# Fetch TÜFE data
data = inflation_service.fetch_tufe_from_oecd_api(2023, 2024)
print(f"Fetched {len(data)} records")

# Display data
for item in data:
    print(f"{item.year}-{item.month:02d}: {item.tufe_rate}%")
```

### Caching and Retrieval

```python
# Fetch and cache data
data = inflation_service.fetch_and_cache_oecd_tufe_data(2023, 2024)

# Retrieve from cache
cached_data = inflation_service.get_cached_oecd_tufe_data(2023, 1)
if cached_data:
    print(f"Cached rate: {cached_data.tufe_rate}%")
```

### Error Handling

```python
from src.services.exceptions import TufeApiError, TufeValidationError

try:
    data = inflation_service.fetch_tufe_from_oecd_api(2023, 2024)
except TufeApiError as e:
    print(f"API Error: {e}")
    # Handle API error
except TufeValidationError as e:
    print(f"Validation Error: {e}")
    # Handle validation error
```

### Rate Limit Monitoring

```python
# Check rate limit status
status = inflation_service.get_rate_limit_status()
if status['can_make_request']:
    print("✅ Requests allowed")
    print(f"Remaining: {status['remaining_hour']} per hour")
else:
    print("⚠️ Rate limited")
    print(f"Message: {status['message']}")
```

## Performance Considerations

### Response Times
- **API fetch**: < 2 seconds
- **Cached data**: < 500ms
- **Bulk fetch**: < 5 seconds per year

### Rate Limits
- **OECD API**: 100 requests/hour (estimated)
- **Retry logic**: Exponential backoff with jitter
- **Maximum retries**: 3 attempts

### Caching
- **Recent data**: 7 days TTL
- **Historical data**: 30 days TTL
- **Failed requests**: 1 hour TTL

## Best Practices

1. **Always check cache first** before making API requests
2. **Handle rate limiting gracefully** with user-friendly messages
3. **Validate data** before processing or storing
4. **Use appropriate TTL** for different data types
5. **Monitor API health** before making requests
6. **Implement proper error handling** with fallback options
7. **Respect rate limits** to maintain API access
8. **Clean up expired cache** regularly to manage storage