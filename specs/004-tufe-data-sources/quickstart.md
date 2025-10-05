# Quickstart: Secure TÜFE Data Sources

**Feature**: Research and Implement Secure TÜFE Data Sources  
**Date**: 2025-10-05  
**Branch**: 004-tufe-data-sources

## Test Scenarios

### Scenario 1: TCMB API Key Configuration
**Given**: A user wants to configure TÜFE data fetching  
**When**: I set up the TCMB API key in the application  
**Then**: The system should store the API key securely and validate it works

**Test Steps**:
1. Navigate to "📊 Inflation Data" page
2. Click "⚙️ Configure TÜFE Data Sources"
3. Enter TCMB API key in the configuration form
4. Click "🔑 Validate API Key"
5. Verify success message: "✅ API key validated successfully"
6. Check that the key is stored securely (not visible in UI)

### Scenario 2: TÜFE Data Fetching from TCMB API
**Given**: A valid TCMB API key is configured  
**When**: I request TÜFE data for the current year  
**Then**: The system should fetch data from TCMB EVDS API and cache it

**Test Steps**:
1. Ensure TCMB API key is configured (from Scenario 1)
2. Navigate to "📊 Inflation Data" page
3. Click "🔄 Fetch from TCMB API"
4. Wait for spinner to complete
5. Verify success message: "✅ TÜFE data fetched from TCMB: X.XX%"
6. Check that data appears in the "Saved Inflation Data" section
7. Verify data source shows "TCMB EVDS API"

### Scenario 3: Data Source Attribution
**Given**: TÜFE data has been fetched from TCMB API  
**When**: I view the negotiation summary or export data  
**Then**: The data source attribution should be clearly displayed

**Test Steps**:
1. Fetch TÜFE data (from Scenario 2)
2. Navigate to "🤝 Negotiation Summary" page
3. Check that "Data source: TCMB (exchange rates), TÜFE (inflation)" is displayed
4. Click "📄 Export Summary as PDF"
5. Open the exported PDF
6. Verify data source attribution is included in the document

### Scenario 4: Cache Management
**Given**: TÜFE data has been cached  
**When**: I request the same data again  
**Then**: The system should use cached data if still valid

**Test Steps**:
1. Fetch TÜFE data for current year (from Scenario 2)
2. Note the fetch timestamp
3. Click "🔄 Fetch from TCMB API" again
4. Verify message: "ℹ️ Using cached TÜFE data (fetched at [timestamp])"
5. Check that no new API call was made
6. Wait 24+ hours and try again
7. Verify new API call is made and cache is refreshed

### Scenario 5: API Error Handling
**Given**: An invalid API key is configured  
**When**: I attempt to fetch TÜFE data  
**Then**: The system should handle the error gracefully

**Test Steps**:
1. Configure an invalid TCMB API key
2. Click "🔄 Fetch from TCMB API"
3. Verify error message: "❌ API Error: Invalid API key"
4. Check that manual entry option is still available
5. Verify system falls back to manual entry gracefully

### Scenario 6: Rate Limiting Handling
**Given**: Multiple rapid API requests are made  
**When**: The rate limit is exceeded  
**Then**: The system should handle rate limiting gracefully

**Test Steps**:
1. Configure valid TCMB API key
2. Make multiple rapid API requests (if possible)
3. Verify rate limit error handling
4. Check that system implements exponential backoff
5. Verify manual entry fallback is available

### Scenario 7: Data Validation
**Given**: TÜFE data is fetched from API  
**When**: The data is processed  
**Then**: The system should validate the data before storing

**Test Steps**:
1. Fetch TÜFE data from TCMB API
2. Check that data is within reasonable range (0-1000%)
3. Verify data is stored as Decimal with proper precision
4. Check that invalid data would be rejected
5. Verify data source attribution is preserved

### Scenario 8: Manual Override
**Given**: TÜFE data has been fetched from API  
**When**: I want to override the data manually  
**Then**: The system should allow manual entry and update the cache

**Test Steps**:
1. Fetch TÜFE data from TCMB API
2. Click "📝 Enter TÜFE Manually"
3. Enter a different TÜFE rate
4. Click "💾 Save TÜFE"
5. Verify success message: "✅ TÜFE data updated manually"
6. Check that manual entry overrides API data
7. Verify data source shows "Manual Entry"

### Scenario 9: Multiple Data Sources
**Given**: Multiple TÜFE data sources are configured  
**When**: I want to switch between sources  
**Then**: The system should allow source selection

**Test Steps**:
1. Configure TCMB API as primary source
2. Add TÜİK as secondary source (if available)
3. Navigate to data source selection
4. Switch between available sources
5. Verify data fetching uses selected source
6. Check that source attribution updates correctly

### Scenario 10: Cache Cleanup
**Given**: Expired cache entries exist  
**When**: The system runs cleanup  
**Then**: Expired entries should be removed

**Test Steps**:
1. Create test cache entries with past expiration dates
2. Run cache cleanup process
3. Verify expired entries are removed
4. Check that valid entries remain
5. Verify cleanup statistics are displayed

## Performance Benchmarks

### API Response Time
- TCMB API calls should complete within 5 seconds
- Cache lookups should complete within 100ms
- Data validation should complete within 50ms

### Cache Performance
- Cache hit rate should be >90% for repeated requests
- Cache storage should use <1MB for 10 years of data
- Cache cleanup should complete within 1 second

### Error Recovery
- API failures should be handled within 2 seconds
- Fallback to manual entry should be available immediately
- Error messages should be user-friendly and actionable

## Security Validation

### API Key Security
- API keys should never be logged in plain text
- API keys should be encrypted at rest
- API keys should be masked in UI displays

### Data Integrity
- All API responses should be validated before storage
- Data should be stored with proper source attribution
- Cache should include integrity checks

### Network Security
- All API calls should use HTTPS
- API endpoints should be validated
- Rate limiting should be respected

## Integration Testing

### End-to-End Flow
1. Configure API key → Fetch data → Cache data → Use in calculations → Export with attribution
2. Test complete flow with real TCMB API (if available)
3. Verify all components work together correctly
4. Test error scenarios and recovery

### UI Integration
1. Test all UI components for TÜFE data management
2. Verify error messages are user-friendly
3. Check that loading states work correctly
4. Test responsive design on different screen sizes

### Data Flow Integration
1. Verify TÜFE data flows correctly to calculation service
2. Check that legal rule calculations use correct TÜFE data
3. Test that export service includes proper attribution
4. Verify chart generation uses cached data efficiently
