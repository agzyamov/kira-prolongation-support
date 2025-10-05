# Data Model: Secure TÜFE Data Sources

**Feature**: Research and Implement Secure TÜFE Data Sources  
**Date**: 2025-10-05  
**Branch**: 004-tufe-data-sources

## Entity Extensions

### InflationData (Extended)
**File**: `src/models/inflation_data.py`

**New Fields**:
- No new fields required - existing structure supports TÜFE data

**New Methods**:
- `is_from_tcmb_api() -> bool`: Returns True if data was fetched from TCMB API
- `get_source_attribution() -> str`: Returns formatted source attribution string

**Validation Rules**:
- Existing validation remains unchanged
- New methods must handle edge cases gracefully

## New Entities

### TufeDataSource
**File**: `src/models/tufe_data_source.py`

**Fields**:
- `source_name: str` - Official name of the data source (e.g., "TCMB EVDS API")
- `api_endpoint: str` - Base API endpoint URL
- `series_code: str` - TCMB series code for TÜFE data (e.g., "TP.FE.OKTG01")
- `data_format: str` - Expected response format ("json" or "xml")
- `requires_auth: bool` - Whether API key is required
- `rate_limit_per_hour: int` - API rate limit (requests per hour)
- `last_verified: datetime` - When the source was last verified as working
- `is_active: bool` - Whether this source is currently active

**Validation Rules**:
- `source_name` must be non-empty string
- `api_endpoint` must be valid HTTPS URL
- `series_code` must be non-empty string
- `data_format` must be one of ["json", "xml"]
- `rate_limit_per_hour` must be positive integer
- `last_verified` must be valid datetime
- `is_active` must be boolean

### TufeApiKey
**File**: `src/models/tufe_api_key.py`

**Fields**:
- `key_name: str` - Human-readable name for the API key
- `api_key: str` - The actual API key (encrypted in storage)
- `source_id: int` - Reference to TufeDataSource
- `created_at: datetime` - When the key was created
- `last_used: datetime` - When the key was last used
- `is_active: bool` - Whether the key is currently active

**Validation Rules**:
- `key_name` must be non-empty string
- `api_key` must be non-empty string (will be encrypted)
- `source_id` must be positive integer
- `created_at` and `last_used` must be valid datetime objects
- `is_active` must be boolean

### TufeDataCache
**File**: `src/models/tufe_data_cache.py`

**Fields**:
- `year: int` - Year of the TÜFE data
- `tufe_rate: Decimal` - TÜFE percentage value
- `source_name: str` - Source of the data (e.g., "TCMB EVDS API")
- `fetched_at: datetime` - When the data was fetched
- `expires_at: datetime` - When the cached data expires
- `api_response: str` - Raw API response (for debugging)
- `is_validated: bool` - Whether the data has been validated

**Validation Rules**:
- `year` must be between 2000-2100
- `tufe_rate` must be non-negative Decimal
- `source_name` must be non-empty string
- `fetched_at` and `expires_at` must be valid datetime objects
- `fetched_at` must be before `expires_at`
- `api_response` must be valid JSON string
- `is_validated` must be boolean

## Database Schema Changes

### New Tables

#### tufe_data_sources
```sql
CREATE TABLE tufe_data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    api_endpoint TEXT NOT NULL,
    series_code TEXT NOT NULL,
    data_format TEXT NOT NULL CHECK(data_format IN ('json', 'xml')),
    requires_auth BOOLEAN NOT NULL DEFAULT 1,
    rate_limit_per_hour INTEGER NOT NULL DEFAULT 100,
    last_verified TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### tufe_api_keys
```sql
CREATE TABLE tufe_api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL,
    api_key TEXT NOT NULL, -- Will be encrypted
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (source_id) REFERENCES tufe_data_sources(id)
);
```

#### tufe_data_cache
```sql
CREATE TABLE tufe_data_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL CHECK(year BETWEEN 2000 AND 2100),
    tufe_rate DECIMAL(6,2) NOT NULL,
    source_name TEXT NOT NULL,
    fetched_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    api_response TEXT, -- JSON string
    is_validated BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, source_name)
);
```

### Indexes
```sql
CREATE INDEX idx_tufe_cache_year ON tufe_data_cache(year);
CREATE INDEX idx_tufe_cache_expires ON tufe_data_cache(expires_at);
CREATE INDEX idx_tufe_api_keys_source ON tufe_api_keys(source_id);
CREATE INDEX idx_tufe_sources_active ON tufe_data_sources(is_active);
```

## Data Relationships

### TufeDataSource → TufeApiKey
- One-to-many relationship
- A data source can have multiple API keys
- API keys are tied to specific data sources

### TufeDataCache → TufeDataSource
- Many-to-one relationship (via source_name)
- Cache entries reference their data source
- Allows tracking of data provenance

### InflationData → TufeDataCache
- One-to-one relationship (via year)
- InflationData can reference cached TÜFE data
- Maintains data lineage and source attribution

## Data Validation Rules

### TÜFE Rate Validation
- Must be between 0% and 1000% (reasonable range for inflation)
- Must be a valid Decimal number
- Must have at most 2 decimal places

### API Key Validation
- Must be non-empty string
- Must be stored encrypted
- Must be associated with valid data source

### Cache Expiration
- Default cache duration: 24 hours
- Cache must expire before new data is fetched
- Expired cache entries should be cleaned up

## Security Considerations

### API Key Storage
- API keys must be encrypted at rest
- Use environment variables for production
- Never log API keys in plain text

### Data Validation
- Validate all API responses before storage
- Sanitize input data
- Check for malicious content in API responses

### Rate Limiting
- Respect TCMB API rate limits
- Implement exponential backoff for failures
- Track API usage to prevent abuse

## Migration Strategy

### Phase 1: Add New Tables
- Create new tables without affecting existing data
- Add indexes for performance
- Set up foreign key constraints

### Phase 2: Populate Default Data
- Insert TCMB EVDS as default data source
- Set up initial configuration
- Test API connectivity

### Phase 3: Update Existing Code
- Modify InflationService to use new data sources
- Update UI to show data source information
- Add API key management interface

### Phase 4: Data Migration
- Migrate existing TÜFE data to new cache structure
- Add source attribution to existing data
- Validate data integrity
