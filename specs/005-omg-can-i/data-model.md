# Data Model: Easy TÜFE Data Fetching

**Feature**: 005-omg-can-i  
**Date**: 2025-10-06  
**Status**: Complete

## Entity Overview

This feature extends the existing TÜFE data infrastructure with enhanced source management, automatic fallback, and zero-configuration capabilities.

## Enhanced Entities

### TufeDataSource (Enhanced)
**Purpose**: Represents different sources of Turkish inflation data with reliability tracking

**Fields**:
- `id`: Primary key (existing)
- `name`: Source name (e.g., "TCMB EVDS", "TÜİK API") (existing)
- `api_endpoint`: Base URL for API calls (existing)
- `is_active`: Whether source is currently available (existing)
- `created_at`: Timestamp of creation (existing)
- `updated_at`: Timestamp of last update (existing)
- **NEW**: `priority`: Integer (1-10, lower = higher priority)
- **NEW**: `reliability_score`: Float (0.0-1.0, based on success rate)
- **NEW**: `last_health_check`: Timestamp of last health check
- **NEW**: `health_status`: Enum (healthy, degraded, failed, unknown)
- **NEW**: `failure_count`: Integer (consecutive failures)
- **NEW**: `success_count`: Integer (consecutive successes)
- **NEW**: `avg_response_time`: Float (milliseconds)
- **NEW**: `rate_limit_remaining`: Integer (API rate limit remaining)
- **NEW**: `rate_limit_reset`: Timestamp (when rate limit resets)

**Validation Rules**:
- Priority must be between 1 and 10
- Reliability score must be between 0.0 and 1.0
- Health status must be one of: healthy, degraded, failed, unknown
- Failure count and success count must be non-negative integers

**State Transitions**:
- `unknown` → `healthy`: First successful health check
- `healthy` → `degraded`: Response time > threshold or rate limit issues
- `degraded` → `healthy`: Performance improves
- `degraded` → `failed`: Consecutive failures exceed threshold
- `failed` → `healthy`: Successful health check after failure period

### TufeFetchSession (New)
**Purpose**: Tracks the status of TÜFE data fetching operations

**Fields**:
- `id`: Primary key
- `session_id`: Unique identifier for the fetch session
- `requested_year`: Year for which TÜFE data was requested
- `status`: Enum (pending, in_progress, success, failed, cancelled)
- `started_at`: Timestamp when fetch started
- `completed_at`: Timestamp when fetch completed
- `source_attempts`: JSON array of source attempts with timestamps
- `final_source`: Source that provided the data (if successful)
- `error_message`: Error message if fetch failed
- `retry_count`: Number of retry attempts
- `user_id`: Optional user identifier for tracking

**Validation Rules**:
- Requested year must be between 2000 and current year + 1
- Status must be one of: pending, in_progress, success, failed, cancelled
- Source attempts must be valid JSON array
- Retry count must be non-negative integer

**State Transitions**:
- `pending` → `in_progress`: Fetch operation starts
- `in_progress` → `success`: Data successfully fetched
- `in_progress` → `failed`: All sources failed
- `in_progress` → `cancelled`: User cancels operation
- `failed` → `in_progress`: Retry attempt

### TufeSourceManager (New)
**Purpose**: Manages source selection, health monitoring, and fallback logic

**Fields**:
- `id`: Primary key
- `name`: Manager instance name
- `active_sources`: JSON array of active source IDs
- `health_check_interval`: Integer (seconds between health checks)
- `failure_threshold`: Integer (failures before marking source as failed)
- `success_threshold`: Integer (successes before marking source as healthy)
- `max_retry_attempts`: Integer (maximum retry attempts per source)
- `retry_delay`: Integer (seconds between retry attempts)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

**Validation Rules**:
- Health check interval must be between 60 and 3600 seconds
- Failure threshold must be between 1 and 10
- Success threshold must be between 1 and 10
- Max retry attempts must be between 1 and 5
- Retry delay must be between 1 and 60 seconds

### TufeAutoConfig (New)
**Purpose**: Manages zero-configuration setup and automatic source discovery

**Fields**:
- `id`: Primary key
- `config_name`: Configuration name
- `auto_discovery_enabled`: Boolean (enable automatic source discovery)
- `default_priority_order`: JSON array of source priorities
- `fallback_to_manual`: Boolean (allow fallback to manual entry)
- `cache_duration_hours`: Integer (cache duration in hours)
- `validation_enabled`: Boolean (enable data validation)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

**Validation Rules**:
- Cache duration must be between 1 and 168 hours (1 week)
- Default priority order must be valid JSON array
- All boolean fields must be valid boolean values

## Enhanced Existing Entities

### TufeApiKey (Enhanced)
**Purpose**: Manages API keys for different TÜFE data sources

**New Fields**:
- `source_priority`: Integer (priority for this source)
- `auto_configured`: Boolean (whether key was auto-discovered)
- `last_used`: Timestamp (when key was last used)
- `usage_count`: Integer (number of times key was used)
- `is_valid`: Boolean (whether key is currently valid)

### TufeDataCache (Enhanced)
**Purpose**: Caches TÜFE data with enhanced source tracking

**New Fields**:
- `source_attempts`: JSON array (sources attempted before cache hit)
- `fetch_duration`: Float (time taken to fetch data)
- `validation_status`: Enum (valid, invalid, warning)
- `data_quality_score`: Float (0.0-1.0, based on validation)

## Relationships

### TufeDataSource ↔ TufeFetchSession
- One-to-many: A source can be used in multiple fetch sessions
- A fetch session can attempt multiple sources

### TufeSourceManager ↔ TufeDataSource
- One-to-many: A manager can manage multiple sources
- A source can be managed by one manager

### TufeAutoConfig ↔ TufeDataSource
- One-to-many: A config can specify multiple sources
- A source can be configured by multiple configs

### TufeApiKey ↔ TufeDataSource
- One-to-one: Each API key belongs to one source
- Each source can have one API key

## Data Validation Rules

### TÜFE Rate Validation
- Must be between 0.0 and 100.0 percent
- Must be reasonable compared to historical data
- Must be from official sources only

### Source Reliability Validation
- Reliability score must be updated after each fetch attempt
- Health status must be updated based on recent performance
- Priority must be maintained based on reliability

### Session Validation
- Fetch sessions must have valid status transitions
- Source attempts must be recorded with timestamps
- Error messages must be descriptive and actionable

## Performance Considerations

### Indexing Strategy
- Index on `TufeDataSource.priority` for fast source selection
- Index on `TufeDataSource.health_status` for health filtering
- Index on `TufeFetchSession.status` for session monitoring
- Index on `TufeDataCache.year` for cache lookups

### Caching Strategy
- Cache source health status for 5 minutes
- Cache successful fetch results for 24 hours
- Cache failed fetch attempts for 1 hour
- Cache source reliability scores for 1 hour

### Data Retention
- Keep fetch sessions for 30 days
- Keep source health history for 7 days
- Keep API key usage logs for 90 days
- Keep cache entries until expiration

## Security Considerations

### API Key Management
- API keys are encrypted at rest
- API keys are masked in logs and UI
- API keys are validated before use
- API keys are rotated based on usage patterns

### Data Validation
- All fetched data is validated before storage
- Source attribution is maintained for audit trails
- Error messages don't expose sensitive information
- Rate limiting prevents abuse

### Access Control
- Source management requires appropriate permissions
- Fetch sessions are isolated by user context
- Configuration changes are logged and audited
- Health check results are monitored for anomalies
