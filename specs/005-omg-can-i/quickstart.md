# Quickstart: Easy TÜFE Data Fetching

**Feature**: 005-omg-can-i  
**Date**: 2025-01-27  
**Status**: Complete

## Overview

This quickstart guide demonstrates how to use the easy TÜFE data fetching feature. The system provides one-click access to Turkish inflation data from the OECD API with automatic caching and rate limit respect.

## Prerequisites

- Python 3.13+
- Streamlit 1.50.0+
- Requests 2.32.3+
- SQLite database with TÜFE tables

## Quick Start

### 1. Launch the Application

```bash
cd /Users/rustemagziamov/kira-prolongation-support
streamlit run app.py
```

### 2. Navigate to TÜFE Data Page

1. Open the application in your browser
2. Click on "Inflation Data" in the sidebar
3. You'll see the TÜFE data management interface

### 3. Fetch TÜFE Data from OECD API

1. **Select Year**: Choose the year for which you want TÜFE data
2. **Select Month** (optional): Choose specific month or leave blank for yearly data
3. **Click "Fetch TÜFE Data from OECD API"**: The system will automatically:
   - Connect to OECD API
   - Parse the SDMX XML response
   - Validate the data
   - Cache the results
   - Display the data

### 4. View Results

The system will display:
- **Success message**: "Successfully fetched TÜFE data for [year]"
- **Data table**: Showing year, month, TÜFE rate, and source
- **Cache status**: Whether data was fetched or retrieved from cache

## Test Scenarios

### Scenario 1: Successful Data Fetch

**Given**: User wants TÜFE data for 2024  
**When**: User clicks "Fetch TÜFE Data from OECD API"  
**Then**: System should:
- Show loading spinner
- Fetch data from OECD API
- Display success message
- Show TÜFE data in table
- Cache the data for future use

**Expected Result**: TÜFE data for 2024 displayed with source "OECD SDMX API"

### Scenario 2: Rate Limiting Handling

**Given**: User has made multiple API requests  
**When**: OECD API returns 429 (Too Many Requests)  
**Then**: System should:
- Show warning message: "Rate limited. Please try again in a few minutes."
- Suggest manual data entry
- Not crash or show technical errors

**Expected Result**: User-friendly error message with fallback option

### Scenario 3: Network Error Handling

**Given**: User's internet connection is unstable  
**When**: API request times out  
**Then**: System should:
- Show error message: "Request timed out. Please try again or enter data manually."
- Provide manual entry option
- Not lose user's work

**Expected Result**: Graceful error handling with recovery options

### Scenario 4: Cached Data Retrieval

**Given**: User previously fetched TÜFE data for 2023  
**When**: User requests the same data again  
**Then**: System should:
- Retrieve data from cache (if not expired)
- Show faster response
- Display cache status
- Not make unnecessary API calls

**Expected Result**: Fast data retrieval from cache

### Scenario 5: Data Validation

**Given**: OECD API returns invalid data  
**When**: System processes the response  
**Then**: System should:
- Validate data ranges (0-200% for TÜFE rates)
- Reject invalid data
- Show validation error message
- Suggest manual entry

**Expected Result**: Invalid data is rejected with clear feedback

### Scenario 6: Manual Data Entry Fallback

**Given**: All automatic data sources fail  
**When**: User needs TÜFE data  
**Then**: System should:
- Provide manual entry form
- Validate user input
- Save data to database
- Show success confirmation

**Expected Result**: User can manually enter TÜFE data

### Scenario 7: Cache Management

**Given**: User wants to manage cached data  
**When**: User accesses cache management  
**Then**: System should:
- Show cache statistics
- Allow cache cleanup
- Display expiration times
- Provide refresh options

**Expected Result**: User can manage cached data effectively

### Scenario 8: Multiple Year Fetch

**Given**: User needs TÜFE data for multiple years  
**When**: User selects year range and clicks fetch  
**Then**: System should:
- Fetch data for all years in range
- Show progress for each year
- Handle partial failures gracefully
- Cache all successful results

**Expected Result**: Bulk data fetch with progress indication

## Error Handling

### Common Error Messages

1. **"Rate limited. Please try again in a few minutes."**
   - **Cause**: Too many API requests
   - **Solution**: Wait and retry, or use manual entry

2. **"Request timed out. Please try again or enter data manually."**
   - **Cause**: Network connectivity issues
   - **Solution**: Check internet connection, retry, or manual entry

3. **"API error: 500"**
   - **Cause**: OECD API server error
   - **Solution**: Try again later, or use manual entry

4. **"No data found for the specified period"**
   - **Cause**: Data not available for requested period
   - **Solution**: Try different year range, or manual entry

5. **"Invalid TÜFE rate: must be between 0% and 200%"**
   - **Cause**: Data validation failure
   - **Solution**: Check data source, or manual entry

### Recovery Options

- **Retry**: Click the fetch button again
- **Manual Entry**: Use the manual data entry form
- **Cache Check**: Verify if data is already cached
- **Different Period**: Try a different year or month

## Performance Expectations

### Response Times
- **Cached data**: < 500ms
- **API fetch**: < 2 seconds
- **Bulk fetch**: < 5 seconds per year

### Rate Limits
- **OECD API**: Respects rate limits automatically
- **Retry logic**: Exponential backoff with jitter
- **Maximum retries**: 3 attempts

### Cache Behavior
- **Recent data**: 7 days TTL
- **Historical data**: 30 days TTL
- **Failed requests**: 1 hour TTL

## Troubleshooting

### Issue: "Connection error" message
**Solution**: Check internet connection, verify OECD API is accessible

### Issue: Data not displaying
**Solution**: Check browser console for errors, refresh page

### Issue: Slow response times
**Solution**: Check cache status, verify network connectivity

### Issue: Invalid data in results
**Solution**: Report issue, use manual entry as fallback

## Advanced Usage

### Batch Data Fetching
```python
# Fetch multiple years at once
years = [2020, 2021, 2022, 2023, 2024]
for year in years:
    data = services['inflation_service'].fetch_tufe_from_oecd_api(year, year)
    if data:
        print(f"Fetched {len(data)} records for {year}")
```

### Cache Management
```python
# Get cache statistics
stats = services['tufe_cache_service'].get_cache_statistics()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")

# Cleanup expired entries
removed = services['tufe_cache_service'].cleanup_expired_cache()
print(f"Removed {removed} expired entries")
```

### Error Monitoring
```python
# Monitor API errors
try:
    data = services['inflation_service'].fetch_tufe_from_oecd_api(2024, 2024)
except TufeApiError as e:
    print(f"API Error: {e.message}")
    print(f"Error Code: {e.code}")
    print(f"Retry After: {e.details.get('retry_after', 'N/A')} seconds")
```

## Support

For issues or questions:
1. Check the error messages and recovery options above
2. Verify your internet connection
3. Try manual data entry as fallback
4. Check the application logs for technical details

The system is designed to be robust and user-friendly, with multiple fallback options to ensure you can always access TÜFE data for your rental negotiations.