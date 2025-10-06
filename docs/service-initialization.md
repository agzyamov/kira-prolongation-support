# Service Initialization Guide

**Version**: 1.0.0  
**Date**: 2025-01-27  
**Feature**: 005-omg-can-i

## Overview

This guide explains how to properly initialize the OECD TÜFE integration services in the application.

## Service Initialization Order

Services must be initialized in the correct order due to dependencies:

1. **DataStore** (foundation)
2. **OECD API Services** (OECDApiClient, RateLimitHandler, DataValidator)
3. **Cache Services** (TufeCacheService)
4. **Business Services** (InflationService)

## Initialization Code

### In app.py

```python
def init_services():
    """Initialize all services with proper dependency order"""
    
    # 1. Initialize DataStore (foundation)
    data_store = DataStore()
    
    # 2. Initialize OECD API services
    oecd_client = OECDApiClient(timeout=30, max_retries=3)
    rate_limit_handler = RateLimitHandler(data_store=data_store)
    data_validator = DataValidator()
    
    # 3. Initialize cache service
    tufe_cache_service = TufeCacheService(data_store)
    
    # 4. Initialize business services
    inflation_service = InflationService(
        data_store=data_store,
        oecd_client=oecd_client,
        rate_limit_handler=rate_limit_handler,
        data_validator=data_validator
    )
    
    # Return services dictionary
    return {
        'data_store': data_store,
        'oecd_client': oecd_client,
        'rate_limit_handler': rate_limit_handler,
        'data_validator': data_validator,
        'tufe_cache_service': tufe_cache_service,
        'inflation_service': inflation_service
    }
```

### Standalone Initialization

```python
from src.storage.data_store import DataStore
from src.services.oecd_api_client import OECDApiClient
from src.services.rate_limit_handler import RateLimitHandler
from src.services.data_validator import DataValidator
from src.services.tufe_cache_service import TufeCacheService
from src.services.inflation_service import InflationService

# Initialize services
services = init_services()

# Use services
data = services['inflation_service'].fetch_tufe_from_oecd_api(2024, 2024)
```

## Configuration

### Environment Variables

```bash
# Optional: Override default timeouts
OECD_API_TIMEOUT=30
OECD_MAX_RETRIES=3
OECD_BACKOFF_FACTOR=2.0

# Optional: Override cache TTL
CACHE_TTL_HOURS=24
```

### Service Configuration

```python
# Custom configuration
oecd_client = OECDApiClient(
    timeout=60,  # Longer timeout for slow connections
    max_retries=5  # More retries for unreliable networks
)

rate_limit_handler = RateLimitHandler(
    max_retries=5,
    base_delay=2.0,  # Longer base delay
    backoff_factor=3.0  # More aggressive backoff
)

data_validator = DataValidator(
    min_rate=0.0,
    max_rate=300.0  # Higher max rate for extreme inflation
)
```

## Error Handling

### Service Initialization Errors

```python
try:
    services = init_services()
except Exception as e:
    print(f"Service initialization failed: {e}")
    # Handle initialization failure
```

### Individual Service Errors

```python
try:
    oecd_client = OECDApiClient()
except ImportError as e:
    print(f"Missing dependencies: {e}")
    # Handle missing dependencies
```

## Testing Initialization

### Unit Test Setup

```python
import pytest
from src.storage.data_store import DataStore

@pytest.fixture
def test_services():
    """Initialize services for testing"""
    data_store = DataStore(db_path=":memory:")
    return init_services(data_store=data_store)
```

### Integration Test Setup

```python
def test_service_integration():
    """Test service integration"""
    services = init_services()
    
    # Test service availability
    assert 'inflation_service' in services
    assert services['inflation_service'] is not None
    
    # Test service functionality
    data = services['inflation_service'].fetch_tufe_from_oecd_api(2024, 2024)
    assert isinstance(data, list)
```

## Best Practices

1. **Initialize DataStore first** - All other services depend on it
2. **Use dependency injection** - Pass dependencies explicitly
3. **Handle initialization errors** - Services may fail to initialize
4. **Test initialization** - Ensure services work together
5. **Use configuration** - Make timeouts and limits configurable
6. **Monitor service health** - Check service status regularly

## Troubleshooting

### Common Issues

1. **ImportError**: Missing dependencies
   - Solution: Install required packages

2. **DatabaseError**: Database not accessible
   - Solution: Check database path and permissions

3. **NetworkError**: API not reachable
   - Solution: Check internet connection and API status

4. **ConfigurationError**: Invalid configuration
   - Solution: Verify configuration values

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize with debug info
services = init_services()
print("Services initialized successfully")
```
