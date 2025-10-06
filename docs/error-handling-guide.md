# Error Handling Guide: OECD TÜFE Integration

**Version**: 1.0.0  
**Date**: 2025-01-27  
**Feature**: 005-omg-can-i

## Overview

This guide provides comprehensive error handling examples and recovery procedures for the OECD TÜFE integration. It covers common error scenarios, recovery strategies, and best practices for robust error handling.

## Error Types and Handling

### 1. API Connection Errors

#### Scenario: Network Timeout

**Error**: `requests.exceptions.Timeout`

**Example**:
```python
from src.services.exceptions import TufeApiError
from src.services.inflation_service import InflationService

try:
    service = InflationService(data_store)
    data = service.fetch_tufe_from_oecd_api(2024, 2024)
except requests.exceptions.Timeout as e:
    print("Network timeout occurred")
    # Recovery: Retry with longer timeout
    service.oecd_client.timeout = 60
    data = service.fetch_tufe_from_oecd_api(2024, 2024)
except TufeApiError as e:
    print(f"API Error: {e}")
    # Recovery: Fallback to manual entry
    data = get_manual_tufe_data(2024, 2024)
```

**Recovery Procedures**:
1. **Retry with longer timeout**
2. **Check network connectivity**
3. **Fallback to cached data**
4. **Manual data entry**

#### Scenario: Connection Refused

**Error**: `requests.exceptions.ConnectionError`

**Example**:
```python
try:
    data = service.fetch_tufe_from_oecd_api(2024, 2024)
except requests.exceptions.ConnectionError as e:
    print("Connection refused - OECD API may be down")
    # Recovery: Check API health and use cache
    if service.is_oecd_api_healthy():
        data = service.fetch_tufe_from_oecd_api(2024, 2024)
    else:
        cached_data = service.get_cached_oecd_tufe_data(2024, 1)
        if cached_data:
            data = [cached_data]
        else:
            data = get_manual_tufe_data(2024, 2024)
```

**Recovery Procedures**:
1. **Check API health status**
2. **Use cached data if available**
3. **Wait and retry**
4. **Manual data entry**

### 2. Rate Limiting Errors

#### Scenario: Too Many Requests

**Error**: HTTP 429 (Too Many Requests)

**Example**:
```python
from src.services.exceptions import RateLimitExceededError

try:
    data = service.fetch_tufe_from_oecd_api(2024, 2024)
except RateLimitExceededError as e:
    print("Rate limit exceeded")
    # Recovery: Check rate limit status and wait
    status = service.get_rate_limit_status()
    if status['can_make_request']:
        data = service.fetch_tufe_from_oecd_api(2024, 2024)
    else:
        print(f"Wait {status['retry_after']} seconds")
        time.sleep(status['retry_after'])
        data = service.fetch_tufe_from_oecd_api(2024, 2024)
```

**Recovery Procedures**:
1. **Check rate limit status**
2. **Wait for reset time**
3. **Use exponential backoff**
4. **Fallback to cached data**

#### Scenario: Rate Limit Handler Failure

**Error**: `RateLimitExceededError`

**Example**:
```python
try:
    handler = RateLimitHandler()
    handler.apply_backoff(attempt=3, max_retries=3)
except RateLimitExceededError as e:
    print("Maximum retries exceeded")
    # Recovery: Reset rate limit and try again
    handler.reset_rate_limit(source_id=1)
    data = service.fetch_tufe_from_oecd_api(2024, 2024)
```

**Recovery Procedures**:
1. **Reset rate limit counters**
2. **Increase retry limits**
3. **Use alternative data source**
4. **Manual data entry**

### 3. Data Validation Errors

#### Scenario: Invalid TÜFE Rate

**Error**: `TufeValidationError`

**Example**:
```python
from src.services.exceptions import TufeValidationError

try:
    validator = DataValidator()
    validator.validate_tufe_rate(rate=250.0)  # Invalid rate
except TufeValidationError as e:
    print(f"Invalid TÜFE rate: {e}")
    # Recovery: Use default rate or manual entry
    rate = get_default_tufe_rate(year=2024, month=1)
    if rate:
        validator.validate_tufe_rate(rate)
    else:
        rate = get_manual_tufe_rate(2024, 1)
```

**Recovery Procedures**:
1. **Use default/fallback values**
2. **Request manual input**
3. **Skip invalid data**
4. **Log validation errors**

#### Scenario: Invalid Year/Month

**Error**: `TufeValidationError`

**Example**:
```python
try:
    validator.validate_year_month(year=1999, month=13)
except TufeValidationError as e:
    print(f"Invalid date: {e}")
    # Recovery: Use current year/month
    from datetime import datetime
    current_year = datetime.now().year
    current_month = datetime.now().month
    validator.validate_year_month(current_year, current_month)
```

**Recovery Procedures**:
1. **Use current date**
2. **Request valid input**
3. **Use default values**
4. **Skip invalid records**

### 4. Data Parsing Errors

#### Scenario: Invalid XML Response

**Error**: `OECDDataParseError`

**Example**:
```python
from src.services.exceptions import OECDDataParseError

try:
    client = OECDApiClient()
    data = client.fetch_tufe_data(2024, 2024)
except OECDDataParseError as e:
    print(f"XML parsing failed: {e}")
    # Recovery: Try alternative parsing or manual entry
    try:
        # Try with different XML parser
        data = client.parse_xml_response_alternative(xml_content)
    except Exception:
        # Fallback to manual entry
        data = get_manual_tufe_data(2024, 2024)
```

**Recovery Procedures**:
1. **Try alternative parsing methods**
2. **Validate XML structure**
3. **Use cached data**
4. **Manual data entry**

#### Scenario: Missing Data Fields

**Error**: `KeyError` or `AttributeError`

**Example**:
```python
try:
    parsed_data = client.parse_sdmx_response(xml_content)
    for item in parsed_data:
        rate = item['value']  # May not exist
except KeyError as e:
    print(f"Missing field: {e}")
    # Recovery: Use default values or skip
    for item in parsed_data:
        rate = item.get('value', get_default_tufe_rate())
        if rate:
            process_tufe_data(item)
```

**Recovery Procedures**:
1. **Use default values**
2. **Skip incomplete records**
3. **Request manual input**
4. **Log missing fields**

### 5. Cache Errors

#### Scenario: Cache Write Failure

**Error**: `TufeCacheError`

**Example**:
```python
from src.services.exceptions import TufeCacheError

try:
    cache_service = TufeCacheService(data_store)
    cache_service.cache_oecd_data(data, ttl_hours=24)
except TufeCacheError as e:
    print(f"Cache write failed: {e}")
    # Recovery: Continue without caching
    print("Continuing without caching...")
    # Data is still available, just not cached
```

**Recovery Procedures**:
1. **Continue without caching**
2. **Retry cache operation**
3. **Use alternative cache**
4. **Log cache errors**

#### Scenario: Cache Read Failure

**Error**: `TufeCacheError`

**Example**:
```python
try:
    cached_data = cache_service.get_cached_oecd_data(2024, 1)
except TufeCacheError as e:
    print(f"Cache read failed: {e}")
    # Recovery: Fetch from API
    data = service.fetch_tufe_from_oecd_api(2024, 2024)
    cached_data = data[0] if data else None
```

**Recovery Procedures**:
1. **Fetch from API**
2. **Use alternative cache**
3. **Manual data entry**
4. **Skip caching**

## Comprehensive Error Handling

### Service-Level Error Handling

```python
class RobustInflationService:
    """InflationService with comprehensive error handling"""
    
    def fetch_tufe_with_fallback(self, year: int, month: int = None):
        """Fetch TÜFE data with multiple fallback strategies"""
        
        # Strategy 1: Try API fetch
        try:
            data = self.fetch_tufe_from_oecd_api(year, year)
            if data:
                return data
        except TufeApiError as e:
            print(f"API fetch failed: {e}")
        
        # Strategy 2: Try cached data
        try:
            cached_data = self.get_cached_oecd_tufe_data(year, month)
            if cached_data:
                print("Using cached data")
                return [cached_data]
        except TufeCacheError as e:
            print(f"Cache read failed: {e}")
        
        # Strategy 3: Try manual entry
        try:
            manual_data = self.get_manual_tufe_data(year, month)
            if manual_data:
                print("Using manual data")
                return [manual_data]
        except Exception as e:
            print(f"Manual data failed: {e}")
        
        # Strategy 4: Use default values
        default_data = self.get_default_tufe_data(year, month)
        if default_data:
            print("Using default data")
            return [default_data]
        
        # Strategy 5: Return empty result
        print("No data available")
        return []
```

### Application-Level Error Handling

```python
def handle_tufe_fetch_error(error: Exception, year: int, month: int = None):
    """Handle TÜFE fetch errors at application level"""
    
    error_type = type(error).__name__
    
    if error_type == 'TufeApiError':
        return {
            'success': False,
            'error': 'API_ERROR',
            'message': 'Unable to fetch data from OECD API',
            'recovery': 'Try again later or enter data manually',
            'fallback': 'manual_entry'
        }
    
    elif error_type == 'RateLimitExceededError':
        return {
            'success': False,
            'error': 'RATE_LIMIT',
            'message': 'Rate limit exceeded. Please wait and try again.',
            'recovery': 'Wait a few minutes before retrying',
            'fallback': 'cached_data'
        }
    
    elif error_type == 'TufeValidationError':
        return {
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'Invalid data received from API',
            'recovery': 'Data will be validated and cleaned',
            'fallback': 'default_values'
        }
    
    elif error_type == 'TufeCacheError':
        return {
            'success': False,
            'error': 'CACHE_ERROR',
            'message': 'Cache operation failed',
            'recovery': 'Continuing without caching',
            'fallback': 'api_fetch'
        }
    
    else:
        return {
            'success': False,
            'error': 'UNKNOWN_ERROR',
            'message': f'Unexpected error: {str(error)}',
            'recovery': 'Please try again or contact support',
            'fallback': 'manual_entry'
        }
```

## Recovery Strategies

### 1. Automatic Recovery

```python
def auto_recovery_fetch(year: int, month: int = None):
    """Automatic recovery with multiple strategies"""
    
    strategies = [
        ('api_fetch', fetch_from_api),
        ('cached_data', fetch_from_cache),
        ('manual_entry', fetch_manual_data),
        ('default_values', fetch_default_data)
    ]
    
    for strategy_name, strategy_func in strategies:
        try:
            data = strategy_func(year, month)
            if data:
                print(f"Recovery successful using {strategy_name}")
                return data
        except Exception as e:
            print(f"Strategy {strategy_name} failed: {e}")
            continue
    
    print("All recovery strategies failed")
    return None
```

### 2. User-Initiated Recovery

```python
def user_recovery_options(error: Exception):
    """Provide user with recovery options"""
    
    options = []
    
    if isinstance(error, TufeApiError):
        options.extend([
            {'action': 'retry', 'label': 'Try Again', 'description': 'Retry the API request'},
            {'action': 'manual', 'label': 'Enter Manually', 'description': 'Enter data manually'},
            {'action': 'cache', 'label': 'Use Cache', 'description': 'Use cached data if available'}
        ])
    
    elif isinstance(error, RateLimitExceededError):
        options.extend([
            {'action': 'wait', 'label': 'Wait and Retry', 'description': 'Wait for rate limit reset'},
            {'action': 'manual', 'label': 'Enter Manually', 'description': 'Enter data manually'}
        ])
    
    return options
```

### 3. Graceful Degradation

```python
def graceful_degradation(year: int, month: int = None):
    """Implement graceful degradation"""
    
    # Try to get any available data
    data_sources = [
        ('api', fetch_from_api),
        ('cache', fetch_from_cache),
        ('manual', fetch_manual_data),
        ('default', fetch_default_data)
    ]
    
    for source_name, fetch_func in data_sources:
        try:
            data = fetch_func(year, month)
            if data:
                return {
                    'data': data,
                    'source': source_name,
                    'quality': get_data_quality(source_name),
                    'warning': get_quality_warning(source_name)
                }
        except Exception:
            continue
    
    return {
        'data': [],
        'source': 'none',
        'quality': 'none',
        'warning': 'No data available from any source'
    }
```

## Best Practices

### 1. Error Logging

```python
import logging

logger = logging.getLogger(__name__)

def log_error_with_context(error: Exception, context: dict):
    """Log error with full context"""
    logger.error(
        f"TÜFE fetch error: {error}",
        extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
    )
```

### 2. Error Monitoring

```python
def monitor_error_rates():
    """Monitor error rates and patterns"""
    error_counts = {
        'api_errors': 0,
        'rate_limit_errors': 0,
        'validation_errors': 0,
        'cache_errors': 0
    }
    
    # Track error rates
    if error_counts['api_errors'] > 10:
        logger.warning("High API error rate detected")
    
    if error_counts['rate_limit_errors'] > 5:
        logger.warning("Frequent rate limiting detected")
```

### 3. Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Circuit breaker for API calls"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
```

## Testing Error Handling

### Unit Tests

```python
def test_error_handling():
    """Test error handling scenarios"""
    
    # Test API error handling
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        with pytest.raises(TufeApiError):
            service.fetch_tufe_from_oecd_api(2024, 2024)
    
    # Test rate limit handling
    with patch('requests.get', return_value=Mock(status_code=429)):
        with pytest.raises(RateLimitExceededError):
            service.fetch_tufe_from_oecd_api(2024, 2024)
    
    # Test validation error handling
    with pytest.raises(TufeValidationError):
        validator.validate_tufe_rate(250.0)
```

### Integration Tests

```python
def test_error_recovery():
    """Test error recovery strategies"""
    
    # Test automatic recovery
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        data = auto_recovery_fetch(2024, 1)
        assert data is not None
        assert data[0]['source'] == 'cache'  # Should fallback to cache
    
    # Test graceful degradation
    with patch('requests.get', side_effect=Exception):
        result = graceful_degradation(2024, 1)
        assert result['data'] is not None
        assert result['source'] in ['cache', 'manual', 'default']
```

This comprehensive error handling guide ensures robust operation of the OECD TÜFE integration with multiple recovery strategies and graceful degradation.
