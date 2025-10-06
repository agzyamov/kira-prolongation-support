# Troubleshooting Guide: OECD API Integration

**Version**: 1.0.0  
**Date**: 2025-01-27  
**Feature**: 005-omg-can-i

## Overview

This guide provides solutions for common issues encountered when using the OECD API integration for TÜFE data fetching. The system is designed to be robust with multiple fallback options, but understanding these troubleshooting steps will help you resolve issues quickly.

## Common Issues and Solutions

### 1. Connection Errors

#### Issue: "Connection error" or "Request timed out"

**Symptoms**:
- Error message: "Request timed out. Please try again or enter data manually."
- Loading spinner appears but never completes
- Network timeout errors in logs

**Causes**:
- Internet connectivity issues
- OECD API server problems
- Firewall or proxy restrictions
- DNS resolution issues

**Solutions**:

1. **Check Internet Connection**
   ```bash
   # Test basic connectivity
   ping google.com
   
   # Test OECD API connectivity
   curl -I https://stats.oecd.org/restsdmx/sdmx.ashx
   ```

2. **Verify OECD API Status**
   - Visit [OECD Statistics](https://stats.oecd.org/) to check if the service is operational
   - Check [OECD API Status](https://stats.oecd.org/restsdmx/sdmx.ashx) directly

3. **Check Firewall/Proxy Settings**
   - Ensure your firewall allows HTTPS connections to `stats.oecd.org`
   - If behind a corporate proxy, configure proxy settings
   - Test with a different network (mobile hotspot)

4. **DNS Resolution**
   ```bash
   # Test DNS resolution
   nslookup stats.oecd.org
   
   # Try different DNS servers
   # Google DNS: 8.8.8.8, 8.8.4.4
   # Cloudflare DNS: 1.1.1.1, 1.0.0.1
   ```

5. **Retry with Backoff**
   - The system automatically retries with exponential backoff
   - Wait 1-2 minutes between manual retries
   - Use cached data if available

### 2. Rate Limiting Issues

#### Issue: "Rate limited" or "Too Many Requests"

**Symptoms**:
- Error message: "Rate limited. Please try again in a few minutes."
- HTTP 429 status code
- Requests fail after multiple attempts

**Causes**:
- Too many API requests in a short time
- Shared IP address with high usage
- Aggressive retry attempts

**Solutions**:

1. **Wait for Rate Limit Reset**
   ```python
   # Check rate limit status
   status = inflation_service.get_rate_limit_status()
   print(f"Rate limit reset in: {status.get('reset_time', 'Unknown')}")
   ```

2. **Use Cached Data**
   - Check if data is already cached
   - Use manual data entry as fallback
   - Wait for cache to refresh

3. **Implement Proper Backoff**
   ```python
   # The system automatically handles this, but you can monitor
   import time
   
   for attempt in range(3):
       try:
           data = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
           break
       except TufeApiError as e:
           if "rate limit" in str(e).lower():
               wait_time = 2 ** attempt  # Exponential backoff
               print(f"Rate limited, waiting {wait_time} seconds...")
               time.sleep(wait_time)
           else:
               raise
   ```

4. **Monitor Rate Limit Status**
   ```python
   # Check before making requests
   status = inflation_service.get_rate_limit_status()
   if not status['can_make_request']:
       print(f"Rate limited: {status['message']}")
       print(f"Remaining requests: {status['remaining_hour']} per hour")
   ```

### 3. Data Validation Errors

#### Issue: "Invalid TÜFE rate" or "Data validation failed"

**Symptoms**:
- Error message: "Invalid TÜFE rate: must be between 0% and 200%"
- Data appears corrupted or unexpected
- Validation errors in logs

**Causes**:
- OECD API returned invalid data
- Data format changes
- Network corruption during transmission
- API response parsing issues

**Solutions**:

1. **Check Data Format**
   ```python
   # Validate data manually
   validator = DataValidator()
   
   try:
       validator.validate_tufe_rate(10.5)  # Should pass
       validator.validate_tufe_rate(201.0)  # Should fail
   except TufeValidationError as e:
       print(f"Validation error: {e}")
   ```

2. **Review API Response**
   ```python
   # Check raw API response
   client = OECDApiClient()
   try:
       raw_data = client.fetch_tufe_data(2020, 2020)
       print(f"Raw response: {raw_data}")
   except Exception as e:
       print(f"API error: {e}")
   ```

3. **Use Manual Data Entry**
   - Enter data manually as fallback
   - Verify data from official sources
   - Report data quality issues

4. **Check Data Ranges**
   ```python
   # Validate year and month ranges
   validator = DataValidator()
   
   # Valid ranges
   validator.validate_year(2020)  # 2000-2030
   validator.validate_month(6)    # 1-12
   
   # Invalid ranges
   try:
       validator.validate_year(1999)  # Too old
   except TufeValidationError as e:
       print(f"Year validation error: {e}")
   ```

### 4. Cache Issues

#### Issue: "Cache error" or "Data not found in cache"

**Symptoms**:
- Error message: "Failed to get cached OECD TÜFE data"
- Cache statistics show unexpected values
- Data not persisting between sessions

**Causes**:
- Database corruption
- Cache expiration
- Storage permissions
- Memory issues

**Solutions**:

1. **Check Cache Statistics**
   ```python
   # Get cache statistics
   stats = inflation_service.get_cache_statistics()
   print(f"Total entries: {stats['total_entries']}")
   print(f"Active entries: {stats['active_entries']}")
   print(f"Expired entries: {stats['expired_entries']}")
   print(f"Hit rate: {stats['hit_rate']:.2%}")
   ```

2. **Cleanup Expired Cache**
   ```python
   # Remove expired entries
   removed_count = inflation_service.cleanup_expired_cache()
   print(f"Removed {removed_count} expired entries")
   ```

3. **Check Database Integrity**
   ```python
   # Verify database connection
   data_store = DataStore()
   
   # Check if tables exist
   with data_store.get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
       tables = cursor.fetchall()
       print(f"Available tables: {tables}")
   ```

4. **Reset Cache**
   ```python
   # Clear all cache entries (use with caution)
   data_store = DataStore()
   with data_store.get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute("DELETE FROM tufe_data_cache")
       conn.commit()
   ```

### 5. Performance Issues

#### Issue: Slow response times or timeouts

**Symptoms**:
- Response times >2 seconds
- Application becomes unresponsive
- Memory usage increases

**Causes**:
- Large dataset requests
- Network latency
- System resource constraints
- Inefficient queries

**Solutions**:

1. **Optimize Request Size**
   ```python
   # Request smaller date ranges
   data = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)  # Single year
   # Instead of: inflation_service.fetch_tufe_from_oecd_api(2000, 2024)  # 25 years
   ```

2. **Use Cached Data**
   ```python
   # Check cache first
   cached_data = inflation_service.get_cached_oecd_tufe_data(2020, 6)
   if cached_data:
       print("Using cached data")
   else:
       print("Fetching from API")
       data = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
   ```

3. **Monitor Performance**
   ```python
   import time
   
   start_time = time.time()
   data = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
   end_time = time.time()
   
   print(f"Fetch time: {end_time - start_time:.2f} seconds")
   print(f"Data points: {len(data)}")
   ```

4. **Check System Resources**
   ```python
   import psutil
   
   # Check memory usage
   memory = psutil.virtual_memory()
   print(f"Memory usage: {memory.percent}%")
   
   # Check CPU usage
   cpu = psutil.cpu_percent()
   print(f"CPU usage: {cpu}%")
   ```

### 6. API Health Issues

#### Issue: "OECD API is not accessible" or health check failures

**Symptoms**:
- Health check returns False
- API info retrieval fails
- Consistent connection errors

**Causes**:
- OECD API server maintenance
- Regional service outages
- API endpoint changes
- Authentication issues

**Solutions**:

1. **Check API Health**
   ```python
   # Test API health
   if inflation_service.is_oecd_api_healthy():
       print("✅ OECD API is healthy")
   else:
       print("❌ OECD API is not accessible")
   ```

2. **Get API Information**
   ```python
   # Get API details
   try:
       info = inflation_service.get_oecd_api_info()
       print(f"API: {info['name']}")
       print(f"Base URL: {info['base_url']}")
       print(f"Series Code: {info['series_code']}")
   except Exception as e:
       print(f"API info error: {e}")
   ```

3. **Test Direct API Access**
   ```bash
   # Test API endpoint directly
   curl -v "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2020&endTime=2020"
   ```

4. **Check OECD Status**
   - Visit [OECD Statistics](https://stats.oecd.org/)
   - Check [OECD API Documentation](https://stats.oecd.org/restsdmx/sdmx.ashx)
   - Look for maintenance announcements

### 7. Data Quality Issues

#### Issue: Unexpected or incorrect TÜFE values

**Symptoms**:
- TÜFE rates seem unrealistic
- Data doesn't match official sources
- Inconsistent values

**Causes**:
- API data quality issues
- Parsing errors
- Data source changes
- Regional data differences

**Solutions**:

1. **Verify Data Source**
   ```python
   # Check data source attribution
   data = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
   for item in data:
       print(f"Source: {item.source}")
       print(f"Year: {item.year}, Month: {item.month}, Rate: {item.tufe_rate}%")
   ```

2. **Compare with Official Sources**
   - Check [TÜİK (Turkish Statistical Institute)](https://www.tuik.gov.tr/)
   - Verify with [OECD Statistics](https://stats.oecd.org/)
   - Cross-reference with [TCMB (Central Bank of Turkey)](https://www.tcmb.gov.tr/)

3. **Validate Data Ranges**
   ```python
   # Check for reasonable TÜFE rates
   data = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
   for item in data:
       if item.tufe_rate < 0 or item.tufe_rate > 200:
           print(f"Unusual TÜFE rate: {item.tufe_rate}% for {item.year}-{item.month}")
   ```

4. **Report Data Issues**
   - Document the issue with specific examples
   - Include timestamps and data values
   - Report to OECD if necessary

## Debug Mode

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Services will now log detailed information
```

### Debug Information Collection

```python
def collect_debug_info():
    """Collect debug information for troubleshooting"""
    debug_info = {
        'timestamp': datetime.now().isoformat(),
        'api_health': inflation_service.is_oecd_api_healthy(),
        'rate_limit_status': inflation_service.get_rate_limit_status(),
        'cache_stats': inflation_service.get_cache_statistics(),
        'api_info': inflation_service.get_oecd_api_info()
    }
    
    return debug_info

# Collect debug info
debug_info = collect_debug_info()
print(json.dumps(debug_info, indent=2))
```

## Emergency Procedures

### Complete System Reset

If all else fails, you can reset the system:

1. **Clear All Cache**
   ```python
   data_store = DataStore()
   with data_store.get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute("DELETE FROM tufe_data_cache")
       cursor.execute("DELETE FROM api_request_logs")
       conn.commit()
   ```

2. **Reset Rate Limit Tracking**
   ```python
   rate_limit_handler = RateLimitHandler()
   rate_limit_handler.reset_rate_limit_tracking()
   ```

3. **Reinitialize Services**
   ```python
   # Restart the application
   # This will reinitialize all services
   ```

### Manual Data Entry Fallback

When all automated methods fail:

1. **Use Manual Entry**
   - Navigate to the Inflation Data page
   - Use the manual data entry form
   - Enter TÜFE data from official sources

2. **Import CSV Data**
   - Prepare CSV file with TÜFE data
   - Use the CSV import feature
   - Verify data after import

3. **External Data Sources**
   - [TÜİK Official Statistics](https://www.tuik.gov.tr/)
   - [OECD Statistics](https://stats.oecd.org/)
   - [TCMB Economic Data](https://www.tcmb.gov.tr/)

## Prevention

### Best Practices

1. **Regular Monitoring**
   - Check API health regularly
   - Monitor rate limit status
   - Review cache statistics

2. **Proper Error Handling**
   - Always use try-catch blocks
   - Implement fallback mechanisms
   - Log errors for debugging

3. **Resource Management**
   - Clean up expired cache entries
   - Monitor memory usage
   - Optimize request sizes

4. **Data Validation**
   - Validate all incoming data
   - Check data ranges and formats
   - Verify data sources

### Monitoring Script

```python
def monitor_system_health():
    """Monitor system health and report issues"""
    issues = []
    
    # Check API health
    if not inflation_service.is_oecd_api_healthy():
        issues.append("OECD API is not healthy")
    
    # Check rate limit status
    rate_status = inflation_service.get_rate_limit_status()
    if not rate_status['can_make_request']:
        issues.append(f"Rate limited: {rate_status['message']}")
    
    # Check cache statistics
    cache_stats = inflation_service.get_cache_statistics()
    if cache_stats['hit_rate'] < 0.5:
        issues.append("Low cache hit rate")
    
    # Report issues
    if issues:
        print("⚠️ System Health Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ System is healthy")
    
    return issues

# Run monitoring
monitor_system_health()
```

## Support

### Getting Help

1. **Check Logs**
   - Review application logs for error details
   - Look for specific error messages
   - Check timestamps for correlation

2. **Collect Debug Information**
   - Use the debug info collection script
   - Include system information
   - Document steps to reproduce

3. **Report Issues**
   - Include error messages
   - Provide debug information
   - Describe expected vs actual behavior

4. **Use Fallback Options**
   - Manual data entry
   - CSV import
   - External data sources

### Contact Information

- **OECD API Issues**: [OECD Statistics Support](https://stats.oecd.org/)
- **Application Issues**: Check application logs and documentation
- **Data Quality Issues**: [TÜİK Support](https://www.tuik.gov.tr/)

Remember: The system is designed to be robust with multiple fallback options. Even if the OECD API is unavailable, you can always enter TÜFE data manually to continue with your rental negotiations.
