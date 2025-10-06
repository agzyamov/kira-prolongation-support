# Data Model: Easy TÜFE Data Fetching

**Feature**: 005-omg-can-i  
**Date**: 2025-01-27  
**Status**: Complete

## Overview

This feature extends the existing TÜFE data infrastructure to support easy fetching from OECD API. The data model builds upon existing entities while adding new components for rate limiting and enhanced caching.

## Existing Entities (Extended)

### TufeDataSource
**Purpose**: Represents OECD API as the primary TÜFE data source

**Fields**:
- `id`: Primary key
- `name`: "OECD SDMX API"
- `endpoint`: "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all"
- `api_type`: "SDMX"
- `requires_auth`: false
- `priority`: 1 (highest priority)
- `reliability_score`: 0.95
- `last_health_check`: timestamp
- `health_status`: "HEALTHY" | "DEGRADED" | "FAILED" | "UNKNOWN"
- `failure_count`: integer
- `success_count`: integer
- `avg_response_time`: float (milliseconds)
- `rate_limit_remaining`: integer
- `rate_limit_reset`: timestamp
- `created_at`: timestamp
- `updated_at`: timestamp

**Methods**:
- `update_health_status(status)`: Update health status
- `mark_success()`: Increment success count
- `mark_failure()`: Increment failure count
- `update_rate_limit(remaining, reset_time)`: Update rate limit info
- `is_healthy()`: Check if source is healthy
- `needs_health_check()`: Check if health check is needed

### TufeDataCache
**Purpose**: Enhanced caching for OECD API data with TTL

**Fields**:
- `id`: Primary key
- `year`: integer (2000-2025)
- `month`: integer (1-12)
- `tufe_rate`: float (percentage)
- `source`: "OECD SDMX API"
- `cached_at`: timestamp
- `expires_at`: timestamp (7 days for recent, 30 days for historical)
- `fetch_duration`: float (milliseconds)
- `retry_count`: integer
- `created_at`: timestamp
- `updated_at`: timestamp

**Methods**:
- `is_expired()`: Check if cache entry is expired
- `get_ttl_seconds()`: Get time to live in seconds
- `mark_fetch_success(duration)`: Update fetch statistics
- `increment_retry()`: Increment retry count

## New Entities

### OECDApiClient
**Purpose**: Dedicated client for OECD SDMX API integration

**Fields**:
- `base_url`: "https://stats.oecd.org/restsdmx/sdmx.ashx"
- `timeout`: 30 (seconds)
- `max_retries`: 3
- `backoff_factor`: 2.0
- `jitter_range`: 0.25

**Methods**:
- `fetch_tufe_data(start_year, end_year)`: Fetch TÜFE data for date range
- `parse_sdmx_xml(xml_content)`: Parse SDMX XML response
- `handle_rate_limit(response)`: Handle 429 responses
- `validate_response(response)`: Validate API response
- `get_rate_limit_info(response)`: Extract rate limit headers

### RateLimitHandler
**Purpose**: Manages API rate limiting and backoff

**Fields**:
- `max_retries`: 3
- `base_delay`: 1.0 (seconds)
- `max_delay`: 60.0 (seconds)
- `backoff_factor`: 2.0
- `jitter_range`: 0.25

**Methods**:
- `should_retry(attempt, response)`: Determine if retry is appropriate
- `get_delay(attempt)`: Calculate delay for next attempt
- `add_jitter(delay)`: Add randomization to delay
- `is_rate_limited(response)`: Check if response indicates rate limiting

### DataValidator
**Purpose**: Validates fetched TÜFE data

**Fields**:
- `min_rate`: 0.0 (percentage)
- `max_rate`: 200.0 (percentage)
- `min_year`: 2000
- `max_year`: current_year + 1

**Methods**:
- `validate_tufe_rate(rate)`: Validate TÜFE rate value
- `validate_year(year)`: Validate year value
- `validate_month(month)`: Validate month value
- `validate_data_source(source)`: Validate data source
- `validate_complete_record(year, month, rate, source)`: Validate complete record

## Data Relationships

```
TufeDataSource (1) ←→ (many) TufeDataCache
    ↓
OECDApiClient (uses)
    ↓
RateLimitHandler (uses)
    ↓
DataValidator (uses)
```

## Database Schema Updates

### Existing Tables (Enhanced)
```sql
-- Add rate limiting fields to tufe_data_sources
ALTER TABLE tufe_data_sources ADD COLUMN rate_limit_remaining INTEGER DEFAULT NULL;
ALTER TABLE tufe_data_sources ADD COLUMN rate_limit_reset TIMESTAMP DEFAULT NULL;

-- Add TTL fields to tufe_data_cache
ALTER TABLE tufe_data_cache ADD COLUMN expires_at TIMESTAMP NOT NULL DEFAULT (datetime('now', '+7 days'));
ALTER TABLE tufe_data_cache ADD COLUMN fetch_duration REAL DEFAULT NULL;
ALTER TABLE tufe_data_cache ADD COLUMN retry_count INTEGER DEFAULT 0;
```

### New Tables
```sql
-- Rate limiting configuration
CREATE TABLE rate_limit_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    max_requests_per_hour INTEGER DEFAULT 100,
    max_requests_per_day INTEGER DEFAULT 1000,
    backoff_factor REAL DEFAULT 2.0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES tufe_data_sources (id)
);

-- API request logs
CREATE TABLE api_request_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL,
    method TEXT DEFAULT 'GET',
    status_code INTEGER,
    response_time REAL,
    rate_limit_remaining INTEGER,
    rate_limit_reset TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES tufe_data_sources (id)
);
```

## Data Validation Rules

### TÜFE Rate Validation
- **Range**: 0.0% ≤ rate ≤ 200.0%
- **Format**: Float with 2 decimal places
- **Required**: Yes

### Year Validation
- **Range**: 2000 ≤ year ≤ current_year + 1
- **Format**: Integer
- **Required**: Yes

### Month Validation
- **Range**: 1 ≤ month ≤ 12
- **Format**: Integer
- **Required**: Yes

### Data Source Validation
- **Format**: Non-empty string
- **Required**: Yes
- **Allowed values**: "OECD SDMX API"

## Caching Strategy

### Cache TTL Rules
- **Recent data** (current year): 7 days
- **Historical data** (previous years): 30 days
- **Failed requests**: 1 hour (to avoid repeated failures)

### Cache Key Strategy
- **Primary key**: (year, month)
- **Secondary key**: source
- **Composite key**: (year, month, source)

### Cache Invalidation
- **Automatic**: Based on TTL expiration
- **Manual**: User-triggered refresh
- **Error-based**: Failed requests expire quickly

## Error Handling

### API Error Types
1. **Network errors**: Timeout, connection refused
2. **HTTP errors**: 429 (rate limited), 500 (server error)
3. **Data errors**: Invalid XML, missing data
4. **Validation errors**: Invalid TÜFE values

### Error Recovery
1. **Retry with backoff**: For transient errors
2. **Fallback to cache**: For rate limiting
3. **Manual entry**: For persistent failures
4. **User notification**: Clear error messages

## Performance Considerations

### API Call Optimization
- **Batch requests**: Fetch multiple years in single call
- **Incremental updates**: Only fetch new data
- **Smart caching**: Avoid redundant requests

### Database Optimization
- **Indexes**: On (year, month) and expires_at
- **Cleanup**: Regular removal of expired entries
- **Connection pooling**: Reuse database connections

### Memory Management
- **Streaming**: Parse large XML responses incrementally
- **Cleanup**: Clear temporary data after processing
- **Monitoring**: Track memory usage during operations