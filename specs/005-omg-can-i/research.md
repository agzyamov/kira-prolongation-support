# Research: Easy TÜFE Data Fetching

**Feature**: 005-omg-can-i  
**Date**: 2025-01-27  
**Status**: Complete

## Research Objectives

Based on the Technical Context, the following areas required research:

1. **OECD API Rate Limiting**: Understanding rate limits and best practices
2. **OECD SDMX API Integration**: Technical implementation details
3. **Caching Strategy**: Optimal caching approach for TÜFE data
4. **Error Handling**: Robust error handling for API failures
5. **Data Validation**: Ensuring data quality from OECD API

## Research Findings

### 1. OECD API Rate Limiting

**Decision**: Implement exponential backoff with jitter and respect 429 status codes

**Rationale**: 
- OECD API has undocumented but observed rate limits
- Users have experienced 429 (Too Many Requests) responses
- Need to implement respectful API usage patterns

**Implementation**:
- Exponential backoff: 1s, 2s, 4s, 8s, 16s delays
- Jitter: ±25% randomization to avoid thundering herd
- Maximum retry attempts: 3
- Respect Retry-After header if present

**Alternatives Considered**:
- Fixed delays: Too rigid, doesn't adapt to server load
- No retry logic: Poor user experience on temporary failures
- Aggressive retry: Risk of permanent IP blocking

### 2. OECD SDMX API Integration

**Decision**: Use OECD SDMX API with XML parsing for TÜFE data

**Rationale**:
- OECD provides official, reliable TÜFE data for Turkey
- SDMX format is standardized and well-documented
- XML parsing is straightforward with Python's built-in libraries
- No API key required (public endpoint)

**Technical Details**:
- Endpoint: `https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all`
- Format: SDMX XML
- Series: A.TUR.CPALTT01.M (Annual, Turkey, All-items CPI, Monthly)
- Data range: 2000-2025 (configurable)

**Implementation**:
```python
import requests
import xml.etree.ElementTree as ET

def fetch_tufe_data(start_year, end_year):
    url = f"https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime={start_year}-01&endTime={end_year}-12"
    response = requests.get(url, timeout=30)
    # Parse XML and extract TÜFE values
```

**Alternatives Considered**:
- TCMB EVDS API: Requires API key, user reported 403 errors
- Web scraping: Fragile, violates terms of service
- Manual data entry: Not scalable, error-prone

### 3. Caching Strategy

**Decision**: SQLite-based caching with TTL and automatic cleanup

**Rationale**:
- TÜFE data is relatively static (monthly updates)
- Reduces API calls and respects rate limits
- Provides offline capability
- Simple implementation with existing infrastructure

**Implementation**:
- Cache TTL: 7 days for recent data, 30 days for historical data
- Automatic cleanup of expired entries
- Cache key: year-month combination
- Fallback to manual entry when cache miss and API unavailable

**Cache Structure**:
```sql
CREATE TABLE tufe_data_cache (
    id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    tufe_rate REAL NOT NULL,
    source TEXT DEFAULT 'OECD SDMX API',
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    UNIQUE(year, month)
);
```

**Alternatives Considered**:
- In-memory caching: Lost on restart, not persistent
- File-based caching: More complex, no query capabilities
- No caching: Poor performance, rate limit issues

### 4. Error Handling

**Decision**: Graceful degradation with user-friendly error messages

**Rationale**:
- API failures should not break the application
- Users need clear feedback on what went wrong
- Fallback options should be available

**Error Scenarios**:
1. **Network timeout**: Retry with backoff, then show manual entry option
2. **Rate limiting (429)**: Show "try again later" message with estimated wait time
3. **Invalid response**: Log error, show manual entry option
4. **No data found**: Show manual entry option with helpful guidance

**Implementation**:
```python
try:
    data = fetch_tufe_data(year)
except requests.exceptions.Timeout:
    st.error("Request timed out. Please try again or enter data manually.")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        st.warning("Rate limited. Please try again in a few minutes.")
    else:
        st.error(f"API error: {e.response.status_code}")
except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
    st.info("You can enter TÜFE data manually below.")
```

**Alternatives Considered**:
- Fail silently: Poor user experience
- Retry indefinitely: Risk of permanent blocking
- Complex error recovery: Over-engineering for simple use case

### 5. Data Validation

**Decision**: Basic range validation and format checking

**Rationale**:
- TÜFE rates should be reasonable (0-200% range)
- Data format should be consistent
- Invalid data should be rejected with clear feedback

**Validation Rules**:
- TÜFE rate: 0.0 <= rate <= 200.0 (percentage)
- Year: 2000 <= year <= current_year + 1
- Month: 1 <= month <= 12
- Data source: Must be specified and non-empty

**Implementation**:
```python
def validate_tufe_data(year, month, rate, source):
    errors = []
    if not (0.0 <= rate <= 200.0):
        errors.append("TÜFE rate must be between 0% and 200%")
    if not (2000 <= year <= datetime.now().year + 1):
        errors.append("Year must be between 2000 and next year")
    if not (1 <= month <= 12):
        errors.append("Month must be between 1 and 12")
    if not source or not source.strip():
        errors.append("Data source must be specified")
    return errors
```

**Alternatives Considered**:
- No validation: Risk of invalid data in system
- Complex validation: Over-engineering for simple numeric data
- External validation service: Unnecessary complexity

## Integration Points

### Existing Infrastructure
- **DataStore**: Extends existing TÜFE tables
- **InflationService**: Adds OECD API integration
- **Streamlit UI**: Adds one-click fetch button
- **Caching**: Uses existing TÜFE cache infrastructure

### New Components
- **OECDApiClient**: Dedicated client for OECD API
- **RateLimitHandler**: Manages API rate limiting
- **DataValidator**: Validates fetched TÜFE data

## Risk Assessment

### High Risk
- **OECD API changes**: Endpoint or format changes could break integration
- **Rate limiting**: Aggressive usage could result in IP blocking

### Medium Risk
- **Network issues**: Poor connectivity could affect user experience
- **Data quality**: OECD data could have inconsistencies

### Low Risk
- **Caching issues**: Cache corruption is easily recoverable
- **Validation errors**: User can always enter data manually

## Mitigation Strategies

1. **API Monitoring**: Log all API calls and responses for debugging
2. **Graceful Degradation**: Always provide manual entry fallback
3. **User Education**: Clear error messages and guidance
4. **Regular Testing**: Automated tests for API integration
5. **Data Backup**: Export functionality for user data

## Conclusion

The research confirms that OECD API integration is the optimal approach for easy TÜFE data fetching. The implementation will be straightforward, leveraging existing infrastructure while adding robust error handling and caching. The solution respects API rate limits and provides excellent user experience through graceful degradation.