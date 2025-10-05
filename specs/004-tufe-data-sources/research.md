# Research: Secure TÜFE Data Sources

**Feature**: Research and Implement Secure TÜFE Data Sources  
**Date**: 2025-10-05  
**Branch**: 004-tufe-data-sources

## Research Findings

### Primary Data Source: TCMB EVDS API

**Decision**: Use TCMB (Turkish Central Bank) Electronic Data Distribution System (EVDS) API as the primary source for TÜFE data.

**Rationale**: 
- Official, secure API provided by the Turkish Central Bank
- No web scraping required - uses proper HTTPS API endpoints
- Provides structured JSON/XML data responses
- Includes proper authentication and rate limiting
- Compliant with official data usage policies

**API Details**:
- **Base URL**: `https://evds2.tcmb.gov.tr/service/evds/`
- **Authentication**: API key required (free registration)
- **Data Format**: JSON or XML
- **TÜFE Series Code**: `TP.FE.OKTG01`
- **Rate Limiting**: Built into the API
- **Documentation**: Available at TCMB EVDS portal

**Registration Process**:
1. Visit: https://evds2.tcmb.gov.tr/index.php?/evds/login
2. Click "KAYIT OL" (Register) to create account
3. Generate API key from profile page
4. Use API key in requests

**API Request Format**:
```
https://evds2.tcmb.gov.tr/service/evds/series=TP.FE.OKTG01&startDate=01-01-2024&endDate=31-12-2024&type=json&key=YOUR_API_KEY&aggregationTypes=avg&frequency=1
```

### Alternative Data Source: TÜİK Open Data Portal

**Decision**: TÜİK (Turkish Statistical Institute) as secondary source for validation.

**Rationale**:
- Official government statistical office
- Provides open data portal at data.tuik.gov.tr
- Can be used to validate TCMB data
- May have different update frequencies

**Implementation Notes**:
- TÜİK may not have direct API access
- Would require investigation of their data portal structure
- Could be used for data validation rather than primary fetching

### Security Considerations

**HTTPS Only**: All API calls must use HTTPS endpoints
**API Key Management**: Store API keys securely, not in code
**Rate Limiting**: Respect TCMB's rate limits
**Error Handling**: Graceful handling of API failures
**Data Validation**: Validate all fetched data before storage

### Implementation Strategy

**Phase 1**: Implement TCMB EVDS API integration
**Phase 2**: Add data validation and caching
**Phase 3**: Implement fallback mechanisms
**Phase 4**: Add TÜİK validation (if needed)

## Dependencies

### Required Libraries
- `requests` - Already in requirements.txt
- `json` - Built-in Python library
- `datetime` - Built-in Python library
- `decimal` - Built-in Python library

### API Requirements
- TCMB EVDS API key (free registration required)
- HTTPS connectivity
- JSON parsing capability

## Risk Assessment

### Low Risk
- Using official TCMB API (secure and reliable)
- Standard HTTP requests with proper error handling
- Data validation before storage

### Medium Risk
- API key management and security
- Rate limiting compliance
- API endpoint changes (rare but possible)

### Mitigation Strategies
- Store API keys in environment variables
- Implement proper rate limiting in code
- Add comprehensive error handling
- Cache data locally to reduce API calls

## Technical Implementation

### API Integration Pattern
```python
def fetch_tufe_from_tcmb_api(year: int, api_key: str) -> Optional[Decimal]:
    """
    Fetch TÜFE data from TCMB EVDS API.
    
    Args:
        year: Year to fetch data for
        api_key: TCMB EVDS API key
        
    Returns:
        TÜFE rate as Decimal or None if not available
    """
    # Implementation details in service layer
```

### Data Validation
- Validate year range (2000-2100)
- Validate percentage values (0-1000% reasonable range)
- Validate data format and structure
- Check for missing or null values

### Caching Strategy
- Cache TÜFE data for 24 hours
- Store in local SQLite database
- Include source attribution and fetch timestamp
- Allow manual refresh if needed

## Alternatives Considered

### Web Scraping (Rejected)
- **Why rejected**: Security risks, unreliable, violates terms of service
- **User feedback**: Explicitly requested against web scraping

### Manual Entry Only (Rejected)
- **Why rejected**: Poor user experience, no automation
- **User feedback**: Wants automated data fetching

### Third-party APIs (Not Researched)
- **Status**: Could be investigated if TCMB API proves insufficient
- **Priority**: Low - official sources preferred

## Next Steps

1. **Implement TCMB EVDS API integration**
2. **Add API key configuration to app settings**
3. **Implement data validation and caching**
4. **Add user interface for API key management**
5. **Test with real TCMB API endpoints**
6. **Add comprehensive error handling**

## References

- [TCMB EVDS Registration Guide](https://karakavuz.com/t-c-merkez-bankasi-evds-kayit-olma-ve-api-kullanma/)
- [TCMB EVDS API Documentation](https://evds2.tcmb.gov.tr/index.php?/evds/documentation/)
- [Python TCMB Integration Example](https://medium.com/datarunner/python-i%CC%87le-merkez-bankas%C4%B1-tcmb-verilerine-eri%C5%9Fim-3bf2baf3cce3)
