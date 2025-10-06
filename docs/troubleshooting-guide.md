# Troubleshooting Guide: OECD API Integration

**Version**: 1.0.0  
**Date**: 2025-01-27  
**Feature**: 005-omg-can-i

## Overview

This guide helps diagnose and resolve common issues with the OECD API integration for TÜFE data fetching. It covers error scenarios, debugging techniques, and step-by-step solutions.

## Quick Diagnostic Checklist

Before diving into specific issues, run through this checklist:

- [ ] **API Connectivity**: Can you reach `https://stats.oecd.org`?
- [ ] **Rate Limits**: Are you within the 100 requests/hour limit?
- [ ] **Data Format**: Is the response in expected XML format?
- [ ] **Cache Status**: Are you checking cache before making API calls?
- [ ] **Error Logs**: What specific error messages are you seeing?

## Common Issues and Solutions

### 1. Connection Errors

#### Issue: "Connection error" or "Failed to connect to OECD API"

**Symptoms:**
- Error message: "Connection error"
- 404 errors in browser
- Timeout errors

**Possible Causes:**
- Network connectivity issues
- Incorrect API endpoint
- Firewall blocking requests
- OECD API service down

**Solutions:**

1. **Check Network Connectivity**
   ```bash
   # Test basic connectivity
   ping stats.oecd.org
   
   # Test HTTPS connectivity
   curl -I https://stats.oecd.org
   
   # Test specific endpoint
   curl -I "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all"
   ```

2. **Verify API Endpoint**
   ```python
   # Test the exact endpoint used by the application
   import requests
   
   url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all"
   response = requests.get(url, timeout=30)
   print(f"Status: {response.status_code}")
   print(f"Headers: {response.headers}")
   ```

3. **Check Firewall/Proxy Settings**
   - Ensure outbound HTTPS (port 443) is allowed
   - Check if corporate firewall blocks OECD domains
   - Verify proxy settings if behind corporate network

4. **Test with Different User Agent**
   ```python
   headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
   }
   response = requests.get(url, headers=headers, timeout=30)
   ```

#### Issue: "404 Not Found" errors

**Symptoms:**
- HTTP 404 status code
- "Not Found" in response body
- API key in URL (incorrect usage)

**Solutions:**

1. **Remove API Key from URL**
   ```python
   # ❌ Wrong - OECD API doesn't use API keys in URL
   url = "http://localhost:8502?api_key=your_key"
   
   # ✅ Correct - OECD API is public, no authentication required
   url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all"
   ```

2. **Verify Endpoint Format**
   ```python
   # Correct endpoint format
   base_url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData"
   dataset = "PRICES_CPI"
   series = "A.TUR.CPALTT01.M"
   url = f"{base_url}/{dataset}/{series}/all"
   ```

### 2. Rate Limiting Issues

#### Issue: "Rate limit exceeded" or 429 errors

**Symptoms:**
- HTTP 429 status code
- "Too Many Requests" error
- Requests being blocked

**Solutions:**

1. **Implement Proper Backoff**
   ```python
   import time
   import random
   
   def make_request_with_backoff(url, max_retries=3):
       for attempt in range(max_retries):
           try:
               response = requests.get(url, timeout=30)
               
               if response.status_code == 429:
                   # Exponential backoff with jitter
                   delay = (2 ** attempt) + random.uniform(0, 1)
                   print(f"Rate limited, waiting {delay:.2f} seconds...")
                   time.sleep(delay)
                   continue
               
               return response
               
           except requests.exceptions.RequestException as e:
               if attempt == max_retries - 1:
                   raise
               delay = 2 ** attempt
               time.sleep(delay)
   ```

2. **Monitor Request Frequency**
   ```python
   # Track requests per hour
   from datetime import datetime, timedelta
   
   class RequestTracker:
       def __init__(self):
           self.requests = []
       
       def can_make_request(self, max_per_hour=100):
           now = datetime.now()
           hour_ago = now - timedelta(hours=1)
           
           # Remove old requests
           self.requests = [req for req in self.requests if req > hour_ago]
           
           return len(self.requests) < max_per_hour
       
       def record_request(self):
           self.requests.append(datetime.now())
   ```

3. **Use Caching to Reduce Requests**
   ```python
   # Check cache before making API request
   def get_tufe_data_with_cache(year, month):
       # Try cache first
       cached_data = get_cached_data(year, month)
       if cached_data and not cached_data.is_expired():
           return cached_data
       
       # Only make API request if not in cache
       return fetch_from_api(year, month)
   ```

### 3. Data Parsing Issues

#### Issue: "Failed to parse XML response" or "OECDDataParseError"

**Symptoms:**
- XML parsing errors
- Missing data in response
- Unexpected data format

**Solutions:**

1. **Validate XML Response**
   ```python
   import xml.etree.ElementTree as ET
   
   def validate_xml_response(xml_content):
       try:
           root = ET.fromstring(xml_content)
           print(f"Root tag: {root.tag}")
           print(f"Root attributes: {root.attrib}")
           
           # Check for expected namespaces
           namespaces = {
               'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
               'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'
           }
           
           # Look for Series elements
           series_elements = root.findall('.//generic:Series', namespaces)
           print(f"Found {len(series_elements)} series elements")
           
           return True
           
       except ET.ParseError as e:
           print(f"XML Parse Error: {e}")
           return False
   ```

2. **Handle Different Response Formats**
   ```python
   def parse_oecd_response(response_content):
       # Check if response is XML
       if response_content.startswith(b'<?xml'):
           return parse_xml_response(response_content)
       
       # Check if response is JSON
       try:
           import json
           return json.loads(response_content)
       except json.JSONDecodeError:
           pass
       
       # Check if response is HTML (error page)
       if b'<html>' in response_content.lower():
           raise Exception("Received HTML response instead of data")
       
       raise Exception("Unknown response format")
   ```

3. **Debug Data Structure**
   ```python
   def debug_oecd_data_structure(xml_content):
       root = ET.fromstring(xml_content)
       
       # Print all namespaces
       print("Namespaces found:")
       for prefix, uri in root.attrib.items():
           if prefix.startswith('{'):
               print(f"  {prefix}: {uri}")
       
       # Print all elements
       print("\nAll elements:")
       for elem in root.iter():
           print(f"  {elem.tag}: {elem.attrib}")
           if elem.text and elem.text.strip():
               print(f"    Text: {elem.text.strip()}")
   ```

### 4. Cache Issues

#### Issue: "Cache not working" or "Data not being cached"

**Symptoms:**
- Same API requests being made repeatedly
- Cache entries not being created
- Expired cache not being cleaned up

**Solutions:**

1. **Verify Cache Configuration**
   ```python
   # Check cache settings
   def verify_cache_config():
       config = {
           'cache_enabled': True,
           'default_ttl_hours': 24,
           'max_cache_size': 1000
       }
       
       print("Cache configuration:")
       for key, value in config.items():
           print(f"  {key}: {value}")
   ```

2. **Test Cache Operations**
   ```python
   def test_cache_operations():
       # Test cache write
       test_data = {'year': 2024, 'month': 1, 'tufe_rate': 50.0}
       cache_key = f"tufe_2024_1"
       
       # Write to cache
       cache_service.set(cache_key, test_data, ttl_hours=1)
       print("✅ Cache write successful")
       
       # Test cache read
       cached_data = cache_service.get(cache_key)
       if cached_data:
           print("✅ Cache read successful")
           print(f"  Data: {cached_data}")
       else:
           print("❌ Cache read failed")
       
       # Test cache expiration
       time.sleep(2)  # Wait for expiration
       expired_data = cache_service.get(cache_key)
       if expired_data is None:
           print("✅ Cache expiration working")
       else:
           print("❌ Cache expiration not working")
   ```

3. **Monitor Cache Performance**
   ```python
   def monitor_cache_performance():
       stats = cache_service.get_cache_statistics()
       
       print("Cache Performance:")
       print(f"  Total entries: {stats['total_entries']}")
       print(f"  Hit rate: {stats['hit_rate']:.2%}")
       print(f"  Expired entries: {stats['expired_entries']}")
       print(f"  Average age: {stats['avg_age_hours']:.1f} hours")
   ```

### 5. Data Validation Issues

#### Issue: "Invalid TÜFE data" or "TufeValidationError"

**Symptoms:**
- Data validation errors
- Unexpected data values
- Missing required fields

**Solutions:**

1. **Validate Data Before Processing**
   ```python
   def validate_tufe_data(data):
       errors = []
       
       # Check required fields
       required_fields = ['year', 'month', 'value']
       for field in required_fields:
           if field not in data:
               errors.append(f"Missing required field: {field}")
       
       # Validate year
       if 'year' in data:
           year = data['year']
           if not isinstance(year, int) or not (2000 <= year <= 2100):
               errors.append(f"Invalid year: {year}")
       
       # Validate month
       if 'month' in data:
           month = data['month']
           if not isinstance(month, int) or not (1 <= month <= 12):
               errors.append(f"Invalid month: {month}")
       
       # Validate TÜFE rate
       if 'value' in data:
           rate = data['value']
           if not isinstance(rate, (int, float)) or not (0 <= rate <= 200):
               errors.append(f"Invalid TÜFE rate: {rate}")
       
       if errors:
           raise TufeValidationError(f"Validation errors: {', '.join(errors)}")
       
       return True
   ```

2. **Handle Missing Data Gracefully**
   ```python
   def process_tufe_data_with_validation(data_list):
       valid_data = []
       invalid_data = []
       
       for item in data_list:
           try:
               validate_tufe_data(item)
               valid_data.append(item)
           except TufeValidationError as e:
               print(f"Invalid data item: {item} - {e}")
               invalid_data.append(item)
       
       print(f"Processed {len(valid_data)} valid items, {len(invalid_data)} invalid items")
       return valid_data
   ```

### 6. Performance Issues

#### Issue: "Slow response times" or "Timeout errors"

**Symptoms:**
- Requests taking longer than expected
- Timeout errors
- Application becoming unresponsive

**Solutions:**

1. **Optimize Request Timeouts**
   ```python
   # Set appropriate timeouts
   def make_optimized_request(url):
       try:
           response = requests.get(
               url, 
               timeout=(10, 30),  # (connect timeout, read timeout)
               headers={'Connection': 'keep-alive'}
           )
           return response
       except requests.exceptions.Timeout:
           print("Request timed out")
           return None
   ```

2. **Implement Request Pooling**
   ```python
   import requests
   from requests.adapters import HTTPAdapter
   from urllib3.util.retry import Retry
   
   def create_optimized_session():
       session = requests.Session()
       
       # Configure retry strategy
       retry_strategy = Retry(
           total=3,
           backoff_factor=1,
           status_forcelist=[429, 500, 502, 503, 504],
       )
       
       # Configure adapter
       adapter = HTTPAdapter(
           max_retries=retry_strategy,
           pool_connections=10,
           pool_maxsize=20
       )
       
       session.mount("http://", adapter)
       session.mount("https://", adapter)
       
       return session
   ```

3. **Use Asynchronous Requests**
   ```python
   import asyncio
   import aiohttp
   
   async def fetch_tufe_data_async(urls):
       async with aiohttp.ClientSession() as session:
           tasks = []
           for url in urls:
               task = fetch_single_url(session, url)
               tasks.append(task)
           
           results = await asyncio.gather(*tasks, return_exceptions=True)
           return results
   
   async def fetch_single_url(session, url):
       try:
           async with session.get(url, timeout=30) as response:
               return await response.text()
       except Exception as e:
           print(f"Error fetching {url}: {e}")
           return None
   ```

## Debugging Techniques

### 1. Enable Detailed Logging

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oecd_api_debug.log'),
        logging.StreamHandler()
    ]
)

# Enable requests logging
logging.getLogger("requests.packages.urllib3").setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
```

### 2. Use Debug Mode

```python
def debug_oecd_api_call(start_year, end_year):
    """Debug OECD API call with detailed output"""
    print(f"🔍 Debugging OECD API call for {start_year}-{end_year}")
    
    # Build URL
    url = f"https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime={start_year}&endTime={end_year}"
    print(f"📡 URL: {url}")
    
    try:
        # Make request with detailed logging
        response = requests.get(url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📏 Content Length: {len(response.content)} bytes")
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        print(f"📄 Content Type: {content_type}")
        
        # Preview content
        content_preview = response.content[:500].decode('utf-8', errors='ignore')
        print(f"📝 Content Preview: {content_preview}...")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
```

### 3. Test with Minimal Data

```python
def test_minimal_oecd_request():
    """Test with minimal data to isolate issues"""
    # Test with single year
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024&endTime=2024"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"✅ Minimal request successful: {response.status_code}")
        
        # Parse response
        root = ET.fromstring(response.content)
        print(f"✅ XML parsing successful")
        
        # Count data points
        namespaces = {
            'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'
        }
        obs_elements = root.findall('.//generic:Obs', namespaces)
        print(f"✅ Found {len(obs_elements)} data points")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal request failed: {e}")
        return False
```

## Error Code Reference

### HTTP Status Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | Data retrieved successfully |
| 400 | Bad Request | Check URL format and parameters |
| 404 | Not Found | Verify endpoint URL |
| 429 | Too Many Requests | Implement rate limiting |
| 500 | Internal Server Error | Retry with backoff |
| 502 | Bad Gateway | Retry with backoff |
| 503 | Service Unavailable | Retry with backoff |
| 504 | Gateway Timeout | Increase timeout, retry |

### Application Error Codes

| Error | Meaning | Solution |
|-------|---------|----------|
| `OECDApiError` | General API error | Check network, retry |
| `OECDDataParseError` | XML parsing failed | Validate response format |
| `RateLimitExceededError` | Rate limit hit | Implement backoff |
| `TufeValidationError` | Data validation failed | Check data format |
| `TufeCacheError` | Cache operation failed | Check cache configuration |

## Getting Help

### 1. Check Logs

```bash
# Check application logs
tail -f logs/application.log

# Check error logs
grep -i error logs/application.log

# Check OECD API specific logs
grep -i oecd logs/application.log
```

### 2. Enable Debug Mode

```python
# Set debug mode in configuration
DEBUG_MODE = True
VERBOSE_LOGGING = True
```

### 3. Test with External Tools

```bash
# Test API endpoint with curl
curl -v "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024&endTime=2024"

# Test with wget
wget -O response.xml "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024&endTime=2024"
```

### 4. Contact Information

If you continue to experience issues:

1. **Check OECD API Status**: Visit [OECD Statistics](https://stats.oecd.org) for service status
2. **Review Documentation**: Check [OECD SDMX API Documentation](https://stats.oecd.org/restsdmx/sdmx.ashx/GetDataStructure/ALL)
3. **Report Issues**: Create an issue in the project repository with:
   - Error messages
   - Steps to reproduce
   - Log files
   - System information

## Prevention Tips

### 1. Implement Proper Error Handling

```python
def robust_oecd_request(url, max_retries=3):
    """Make robust OECD API request with proper error handling"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise
            
        except requests.exceptions.ConnectionError:
            print(f"Connection error on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limited on attempt {attempt + 1}")
                time.sleep(2 ** attempt)
            else:
                raise
        
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
```

### 2. Monitor API Health

```python
def monitor_api_health():
    """Monitor OECD API health"""
    health_checks = [
        "https://stats.oecd.org",
        "https://stats.oecd.org/restsdmx/sdmx.ashx/GetDataStructure/ALL"
    ]
    
    for url in health_checks:
        try:
            response = requests.head(url, timeout=10)
            status = "✅ Healthy" if response.status_code == 200 else "❌ Unhealthy"
            print(f"{url}: {status} ({response.status_code})")
        except Exception as e:
            print(f"{url}: ❌ Error - {e}")
```

### 3. Regular Maintenance

```python
def perform_maintenance():
    """Perform regular maintenance tasks"""
    # Clean up expired cache
    expired_count = cache_service.cleanup_expired_cache()
    print(f"Cleaned up {expired_count} expired cache entries")
    
    # Update rate limit status
    rate_limit_status = rate_limit_handler.get_rate_limit_status()
    print(f"Rate limit status: {rate_limit_status}")
    
    # Check API health
    api_health = oecd_client.is_healthy()
    print(f"OECD API health: {'✅ Healthy' if api_health else '❌ Unhealthy'}")
```

This troubleshooting guide should help you resolve most common issues with the OECD API integration. Remember to always check the logs first and implement proper error handling to prevent issues from occurring in the first place.
