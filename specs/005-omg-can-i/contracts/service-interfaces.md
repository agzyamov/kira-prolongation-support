# Service Interfaces: Easy TÜFE Data Fetching

**Feature**: 005-omg-can-i  
**Date**: 2025-10-06  
**Status**: Complete

## Service Interface Overview

This document defines the service interfaces for the easy TÜFE data fetching feature, extending the existing TÜFE infrastructure with enhanced source management and automatic fallback capabilities.

## New Service Interfaces

### TufeFetchService
**Purpose**: Orchestrates TÜFE data fetching with automatic source selection and fallback

**Interface**:
```python
class TufeFetchService:
    def __init__(self, data_store: DataStore, source_manager: TufeSourceManager):
        pass
    
    def fetch_tufe_easy(self, year: int) -> TufeFetchResult:
        """
        One-click TÜFE data fetching with automatic source selection.
        
        Args:
            year: Year for which to fetch TÜFE data
            
        Returns:
            TufeFetchResult with data, source info, and status
            
        Raises:
            TufeFetchError: If all sources fail
            ValidationError: If year is invalid
        """
        pass
    
    def fetch_tufe_with_source(self, year: int, source_id: int) -> TufeFetchResult:
        """
        Fetch TÜFE data from a specific source.
        
        Args:
            year: Year for which to fetch TÜFE data
            source_id: ID of the source to use
            
        Returns:
            TufeFetchResult with data, source info, and status
            
        Raises:
            TufeFetchError: If source fails
            SourceNotFoundError: If source doesn't exist
        """
        pass
    
    def get_fetch_status(self, session_id: str) -> TufeFetchSession:
        """
        Get the status of a fetch operation.
        
        Args:
            session_id: Unique identifier for the fetch session
            
        Returns:
            TufeFetchSession with current status and details
            
        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        pass
    
    def cancel_fetch(self, session_id: str) -> bool:
        """
        Cancel an ongoing fetch operation.
        
        Args:
            session_id: Unique identifier for the fetch session
            
        Returns:
            True if cancelled successfully
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionNotCancellableError: If session cannot be cancelled
        """
        pass
```

### TufeSourceManager
**Purpose**: Manages source selection, health monitoring, and fallback logic

**Interface**:
```python
class TufeSourceManager:
    def __init__(self, data_store: DataStore):
        pass
    
    def get_best_source(self, year: int) -> Optional[TufeDataSource]:
        """
        Get the best available source for fetching TÜFE data.
        
        Args:
            year: Year for which to fetch data
            
        Returns:
            Best available source or None if no sources available
        """
        pass
    
    def get_source_priority_order(self) -> List[TufeDataSource]:
        """
        Get sources ordered by priority and reliability.
        
        Returns:
            List of sources ordered by priority (highest first)
        """
        pass
    
    def update_source_health(self, source_id: int, is_healthy: bool, response_time: float) -> None:
        """
        Update the health status of a source.
        
        Args:
            source_id: ID of the source to update
            is_healthy: Whether the source is currently healthy
            response_time: Response time in milliseconds
            
        Raises:
            SourceNotFoundError: If source doesn't exist
        """
        pass
    
    def mark_source_failed(self, source_id: int, error_message: str) -> None:
        """
        Mark a source as failed with error details.
        
        Args:
            source_id: ID of the source to mark as failed
            error_message: Error message describing the failure
            
        Raises:
            SourceNotFoundError: If source doesn't exist
        """
        pass
    
    def mark_source_success(self, source_id: int, response_time: float) -> None:
        """
        Mark a source as successful with performance metrics.
        
        Args:
            source_id: ID of the source to mark as successful
            response_time: Response time in milliseconds
            
        Raises:
            SourceNotFoundError: If source doesn't exist
        """
        pass
    
    def get_source_reliability_score(self, source_id: int) -> float:
        """
        Get the current reliability score of a source.
        
        Args:
            source_id: ID of the source
            
        Returns:
            Reliability score between 0.0 and 1.0
            
        Raises:
            SourceNotFoundError: If source doesn't exist
        """
        pass
    
    def run_health_checks(self) -> Dict[int, bool]:
        """
        Run health checks on all active sources.
        
        Returns:
            Dictionary mapping source IDs to health status
        """
        pass
```

### TufeAutoConfig
**Purpose**: Manages zero-configuration setup and automatic source discovery

**Interface**:
```python
class TufeAutoConfig:
    def __init__(self, data_store: DataStore):
        pass
    
    def setup_zero_config(self) -> TufeAutoConfig:
        """
        Set up zero-configuration TÜFE fetching.
        
        Returns:
            TufeAutoConfig with default settings
        """
        pass
    
    def discover_available_sources(self) -> List[TufeDataSource]:
        """
        Automatically discover available TÜFE data sources.
        
        Returns:
            List of discovered sources
        """
        pass
    
    def auto_configure_sources(self) -> List[TufeDataSource]:
        """
        Automatically configure discovered sources.
        
        Returns:
            List of configured sources
        """
        pass
    
    def get_default_priority_order(self) -> List[int]:
        """
        Get the default priority order for sources.
        
        Returns:
            List of source IDs in priority order
        """
        pass
    
    def is_auto_config_enabled(self) -> bool:
        """
        Check if auto-configuration is enabled.
        
        Returns:
            True if auto-configuration is enabled
        """
        pass
    
    def enable_auto_config(self) -> None:
        """
        Enable auto-configuration.
        """
        pass
    
    def disable_auto_config(self) -> None:
        """
        Disable auto-configuration.
        """
        pass
```

### TufeValidator (Enhanced)
**Purpose**: Validates TÜFE data with enhanced quality checks

**Interface**:
```python
class TufeValidator:
    def __init__(self):
        pass
    
    def validate_tufe_data(self, data: TufeData, source: TufeDataSource) -> ValidationResult:
        """
        Validate TÜFE data with comprehensive checks.
        
        Args:
            data: TÜFE data to validate
            source: Source that provided the data
            
        Returns:
            ValidationResult with validation status and details
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    def validate_source_attribution(self, data: TufeData, source: TufeDataSource) -> bool:
        """
        Validate that data attribution matches the source.
        
        Args:
            data: TÜFE data to validate
            source: Source that provided the data
            
        Returns:
            True if attribution is valid
        """
        pass
    
    def validate_data_freshness(self, data: TufeData) -> bool:
        """
        Validate that data is fresh and not stale.
        
        Args:
            data: TÜFE data to validate
            
        Returns:
            True if data is fresh
        """
        pass
    
    def validate_rate_reasonableness(self, rate: float, year: int) -> bool:
        """
        Validate that TÜFE rate is reasonable for the given year.
        
        Args:
            rate: TÜFE rate to validate
            year: Year for which the rate applies
            
        Returns:
            True if rate is reasonable
        """
        pass
    
    def get_data_quality_score(self, data: TufeData) -> float:
        """
        Calculate a data quality score for the given data.
        
        Args:
            data: TÜFE data to score
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        pass
```

## Enhanced Existing Service Interfaces

### TufeDataSourceService (Enhanced)
**Purpose**: Manages TÜFE data sources with enhanced reliability tracking

**New Methods**:
```python
def update_source_reliability(self, source_id: int, reliability_score: float) -> None:
    """Update the reliability score of a source."""

def get_sources_by_priority(self) -> List[TufeDataSource]:
    """Get sources ordered by priority and reliability."""

def get_healthy_sources(self) -> List[TufeDataSource]:
    """Get only healthy sources."""

def update_source_health(self, source_id: int, health_status: str) -> None:
    """Update the health status of a source."""

def get_source_performance_metrics(self, source_id: int) -> Dict[str, Any]:
    """Get performance metrics for a source."""
```

### TufeCacheService (Enhanced)
**Purpose**: Manages TÜFE data caching with enhanced source tracking

**New Methods**:
```python
def cache_with_source_info(self, data: TufeData, source: TufeDataSource, fetch_duration: float) -> int:
    """Cache data with source information and performance metrics."""

def get_cache_with_source_info(self, year: int) -> Optional[Tuple[TufeData, TufeDataSource, Dict[str, Any]]]:
    """Get cached data with source information."""

def update_cache_quality_score(self, cache_id: int, quality_score: float) -> None:
    """Update the quality score of cached data."""

def get_cache_performance_stats(self) -> Dict[str, Any]:
    """Get cache performance statistics."""
```

## Data Transfer Objects

### TufeFetchResult
**Purpose**: Result of a TÜFE data fetch operation

**Fields**:
- `success`: Boolean (whether fetch was successful)
- `data`: Optional[TufeData] (fetched data if successful)
- `source`: Optional[TufeDataSource] (source that provided data)
- `session_id`: str (unique session identifier)
- `fetch_duration`: float (time taken to fetch data)
- `attempts`: List[SourceAttempt] (sources attempted)
- `error_message`: Optional[str] (error message if failed)
- `cached`: bool (whether data came from cache)

### SourceAttempt
**Purpose**: Represents an attempt to fetch data from a source

**Fields**:
- `source_id`: int (ID of the source attempted)
- `source_name`: str (name of the source)
- `attempted_at`: datetime (when attempt was made)
- `success`: bool (whether attempt was successful)
- `response_time`: float (response time in milliseconds)
- `error_message`: Optional[str] (error message if failed)

### ValidationResult
**Purpose**: Result of data validation

**Fields**:
- `valid`: bool (whether data is valid)
- `quality_score`: float (quality score between 0.0 and 1.0)
- `warnings`: List[str] (validation warnings)
- `errors`: List[str] (validation errors)
- `validation_details`: Dict[str, Any] (detailed validation information)

## Error Handling

### Custom Exceptions
```python
class TufeFetchError(ServiceError):
    """Raised when TÜFE data fetching fails"""
    pass

class SourceNotFoundError(ServiceError):
    """Raised when a requested source doesn't exist"""
    pass

class SessionNotFoundError(ServiceError):
    """Raised when a fetch session doesn't exist"""
    pass

class SessionNotCancellableError(ServiceError):
    """Raised when a fetch session cannot be cancelled"""
    pass

class AutoConfigError(ServiceError):
    """Raised when auto-configuration fails"""
    pass

class ValidationError(ServiceError):
    """Raised when data validation fails"""
    pass
```

## Performance Requirements

### Response Times
- Easy fetch operation: < 2 seconds
- Source health check: < 500ms
- Cache lookup: < 100ms
- Source selection: < 50ms

### Reliability
- 99% success rate for easy fetch operations
- Automatic fallback within 5 seconds
- Health check accuracy: 95%

### Scalability
- Support for up to 10 concurrent fetch operations
- Handle up to 1000 fetch requests per hour
- Cache up to 1000 TÜFE data points

## Security Requirements

### API Key Management
- API keys are encrypted at rest
- API keys are masked in logs and UI
- API keys are validated before use
- Rate limiting prevents abuse

### Data Validation
- All fetched data is validated before storage
- Source attribution is maintained for audit trails
- Error messages don't expose sensitive information
- Input validation prevents injection attacks

### Access Control
- Source management requires appropriate permissions
- Fetch sessions are isolated by user context
- Configuration changes are logged and audited
- Health check results are monitored for anomalies
