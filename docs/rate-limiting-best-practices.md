# Rate Limiting Best Practices: OECD API Integration

**Version**: 1.0.0  
**Date**: 2025-01-27  
**Feature**: 005-omg-can-i

## Overview

This document provides comprehensive guidance on rate limiting best practices for the OECD API integration. Proper rate limiting ensures sustainable API usage, prevents service disruptions, and maintains good relationships with data providers.

## Understanding Rate Limits

### What is Rate Limiting?

Rate limiting is a technique used to control the rate of requests sent to an API. It helps:
- Prevent API abuse
- Ensure fair usage across all users
- Maintain API stability and performance
- Protect against DDoS attacks

### OECD API Rate Limits

The OECD SDMX API has undocumented but observed rate limits:
- **Estimated hourly limit**: 100 requests per hour
- **Estimated daily limit**: 1000 requests per day
- **Response codes**: 429 (Too Many Requests) when limits are exceeded
- **Reset time**: Varies, typically 1 hour for hourly limits

## Implementation Strategy

### 1. Exponential Backoff with Jitter

**Principle**: Increase delay between retries exponentially, with randomization to avoid thundering herd.

```python
import time
import random

class RateLimitHandler:
    def __init__(self, max_retries=3, base_delay=1.0, backoff_factor=2.0, jitter_range=0.25):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.jitter_range = jitter_range
    
    def get_delay(self, attempt):
        """Calculate delay for retry attempt"""
        delay = self.base_delay * (self.backoff_factor ** attempt)
        return delay
    
    def add_jitter(self, delay):
        """Add randomization to delay"""
        jitter = random.uniform(-self.jitter_range, self.jitter_range)
        return delay * (1 + jitter)
    
    def should_retry(self, attempt, response):
        """Determine if request should be retried"""
        if attempt >= self.max_retries:
            return False
        
        # Retry on rate limit (429) and server errors (5xx)
        return response.status_code in [429, 500, 502, 503, 504]
```

### 2. Request Tracking and Monitoring

**Principle**: Track all API requests to monitor usage patterns and detect rate limiting.

```python
import sqlite3
from datetime import datetime, timedelta

class RequestTracker:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create tables for request tracking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    endpoint TEXT NOT NULL,
                    status_code INTEGER,
                    response_time REAL,
                    rate_limit_remaining INTEGER,
                    rate_limit_reset TIMESTAMP,
                    error_message TEXT
                )
            """)
            conn.commit()
    
    def log_request(self, endpoint, status_code, response_time, rate_limit_remaining=None, rate_limit_reset=None, error_message=None):
        """Log API request"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_request_logs 
                (endpoint, status_code, response_time, rate_limit_remaining, rate_limit_reset, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (endpoint, status_code, response_time, rate_limit_remaining, rate_limit_reset, error_message))
            conn.commit()
    
    def get_request_count(self, time_window=timedelta(hours=1)):
        """Get request count in time window"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM api_request_logs 
                WHERE timestamp > datetime('now', '-{} seconds')
            """.format(int(time_window.total_seconds())))
            return cursor.fetchone()[0]
    
    def get_rate_limit_status(self):
        """Get current rate limit status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rate_limit_remaining, rate_limit_reset 
                FROM api_request_logs 
                WHERE rate_limit_remaining IS NOT NULL 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            return result if result else (None, None)
```

### 3. Intelligent Caching

**Principle**: Cache API responses to minimize requests and respect rate limits.

```python
from datetime import datetime, timedelta
import hashlib
import json

class IntelligentCache:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create cache tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP
                )
            """)
            conn.commit()
    
    def _generate_cache_key(self, endpoint, params):
        """Generate cache key from endpoint and parameters"""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, endpoint, params):
        """Get cached data"""
        cache_key = self._generate_cache_key(endpoint, params)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data, expires_at FROM api_cache 
                WHERE cache_key = ? AND expires_at > datetime('now')
            """, (cache_key,))
            result = cursor.fetchone()
            
            if result:
                # Update hit count and last accessed
                cursor.execute("""
                    UPDATE api_cache 
                    SET hit_count = hit_count + 1, last_accessed = datetime('now')
                    WHERE cache_key = ?
                """, (cache_key,))
                conn.commit()
                
                return json.loads(result[0])
        
        return None
    
    def set(self, endpoint, params, data, ttl_hours=24):
        """Cache data with TTL"""
        cache_key = self._generate_cache_key(endpoint, params)
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO api_cache 
                (cache_key, data, expires_at) 
                VALUES (?, ?, ?)
            """, (cache_key, json.dumps(data), expires_at))
            conn.commit()
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_cache WHERE expires_at < datetime('now')")
            conn.commit()
            return cursor.rowcount
```

## Best Practices

### 1. Respect Rate Limits

**Always respect the API's rate limits:**
- Monitor response headers for rate limit information
- Implement proper backoff when rate limited
- Never attempt to bypass rate limits

```python
def make_api_request_with_rate_limiting(url, max_retries=3):
    """Make API request with proper rate limiting"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    wait_time = int(retry_after)
                else:
                    wait_time = 2 ** attempt  # Exponential backoff
                
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            
            # Check for other retryable errors
            if response.status_code >= 500:
                wait_time = 2 ** attempt
                print(f"Server error {response.status_code}, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            
            # Success
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Request failed: {e}, waiting {wait_time} seconds...")
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")
```

### 2. Implement Circuit Breaker Pattern

**Prevent cascading failures by implementing circuit breaker:**

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful request"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### 3. Use Request Queuing

**Queue requests to prevent overwhelming the API:**

```python
import queue
import threading
import time

class RequestQueue:
    def __init__(self, max_concurrent=5, delay_between_requests=1.0):
        self.max_concurrent = max_concurrent
        self.delay_between_requests = delay_between_requests
        self.request_queue = queue.Queue()
        self.active_requests = 0
        self.lock = threading.Lock()
        self.worker_threads = []
        
        # Start worker threads
        for _ in range(max_concurrent):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self.worker_threads.append(thread)
    
    def _worker(self):
        """Worker thread to process requests"""
        while True:
            try:
                request_func, callback, error_callback = self.request_queue.get(timeout=1)
                
                with self.lock:
                    self.active_requests += 1
                
                try:
                    result = request_func()
                    if callback:
                        callback(result)
                except Exception as e:
                    if error_callback:
                        error_callback(e)
                finally:
                    with self.lock:
                        self.active_requests -= 1
                    
                    self.request_queue.task_done()
                    time.sleep(self.delay_between_requests)
                    
            except queue.Empty:
                continue
    
    def add_request(self, request_func, callback=None, error_callback=None):
        """Add request to queue"""
        self.request_queue.put((request_func, callback, error_callback))
    
    def wait_for_completion(self):
        """Wait for all requests to complete"""
        self.request_queue.join()
```

### 4. Monitor and Alert

**Implement monitoring and alerting for rate limit issues:**

```python
import logging
from datetime import datetime, timedelta

class RateLimitMonitor:
    def __init__(self, alert_threshold=0.8):
        self.alert_threshold = alert_threshold
        self.logger = logging.getLogger(__name__)
    
    def check_rate_limit_status(self, rate_limit_remaining, rate_limit_total):
        """Check if rate limit is approaching threshold"""
        if rate_limit_remaining is None or rate_limit_total is None:
            return
        
        usage_ratio = (rate_limit_total - rate_limit_remaining) / rate_limit_total
        
        if usage_ratio >= self.alert_threshold:
            self.logger.warning(f"Rate limit usage at {usage_ratio:.1%} ({rate_limit_remaining}/{rate_limit_total} remaining)")
            
            if usage_ratio >= 0.95:
                self.logger.error("Rate limit usage critical! Consider reducing request frequency.")
    
    def monitor_request_patterns(self, request_logs):
        """Monitor request patterns for anomalies"""
        if len(request_logs) < 10:
            return
        
        # Check for sudden spikes in requests
        recent_requests = [log for log in request_logs if log['timestamp'] > datetime.now() - timedelta(minutes=5)]
        
        if len(recent_requests) > 20:  # More than 20 requests in 5 minutes
            self.logger.warning("High request frequency detected in last 5 minutes")
        
        # Check for high error rate
        error_requests = [log for log in recent_requests if log['status_code'] >= 400]
        error_rate = len(error_requests) / len(recent_requests) if recent_requests else 0
        
        if error_rate > 0.1:  # More than 10% error rate
            self.logger.warning(f"High error rate detected: {error_rate:.1%}")
```

## Configuration

### Rate Limiting Configuration

```python
# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    # OECD API limits (estimated)
    'oecd': {
        'max_requests_per_hour': 100,
        'max_requests_per_day': 1000,
        'backoff_factor': 2.0,
        'max_retries': 3,
        'jitter_range': 0.25,
        'circuit_breaker': {
            'failure_threshold': 5,
            'recovery_timeout': 60
        }
    },
    
    # Request queue configuration
    'request_queue': {
        'max_concurrent': 5,
        'delay_between_requests': 1.0
    },
    
    # Cache configuration
    'cache': {
        'default_ttl_hours': 24,
        'recent_data_ttl_hours': 7,
        'historical_data_ttl_hours': 168,
        'cleanup_interval_hours': 6
    },
    
    # Monitoring configuration
    'monitoring': {
        'alert_threshold': 0.8,
        'check_interval_seconds': 300
    }
}
```

### Environment Variables

```bash
# Rate limiting configuration
OECD_MAX_REQUESTS_PER_HOUR=100
OECD_MAX_REQUESTS_PER_DAY=1000
OECD_BACKOFF_FACTOR=2.0
OECD_MAX_RETRIES=3

# Cache configuration
CACHE_DEFAULT_TTL_HOURS=24
CACHE_CLEANUP_INTERVAL_HOURS=6

# Monitoring configuration
RATE_LIMIT_ALERT_THRESHOLD=0.8
MONITORING_CHECK_INTERVAL=300
```

## Testing Rate Limiting

### Unit Tests

```python
import pytest
import time
from unittest.mock import Mock, patch

class TestRateLimiting:
    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        handler = RateLimitHandler(base_delay=1.0, backoff_factor=2.0)
        
        assert handler.get_delay(0) == 1.0
        assert handler.get_delay(1) == 2.0
        assert handler.get_delay(2) == 4.0
        assert handler.get_delay(3) == 8.0
    
    def test_jitter_addition(self):
        """Test jitter addition to delays"""
        handler = RateLimitHandler(jitter_range=0.25)
        
        delay = 2.0
        jittered_delay = handler.add_jitter(delay)
        
        # Should be within 25% of original delay
        assert 1.5 <= jittered_delay <= 2.5
    
    def test_rate_limit_detection(self):
        """Test rate limit detection"""
        handler = RateLimitHandler()
        
        # Mock 429 response
        response_429 = Mock()
        response_429.status_code = 429
        
        assert handler.is_rate_limited(response_429) is True
        
        # Mock 200 response
        response_200 = Mock()
        response_200.status_code = 200
        
        assert handler.is_rate_limited(response_200) is False
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality"""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        
        # Mock failing function
        def failing_func():
            raise Exception("API error")
        
        # Should fail 3 times then open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(failing_func)
        
        # Circuit should be open now
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            breaker.call(failing_func)
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Should be half-open now
        assert breaker.state == CircuitState.HALF_OPEN
```

### Integration Tests

```python
class TestRateLimitingIntegration:
    def test_api_request_with_rate_limiting(self):
        """Test API request with rate limiting"""
        with patch('requests.get') as mock_get:
            # Mock rate limited response
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '1'}
            mock_get.return_value = mock_response
            
            # Should retry with backoff
            with pytest.raises(Exception):
                make_api_request_with_rate_limiting("https://api.example.com")
            
            # Should have made multiple requests
            assert mock_get.call_count > 1
    
    def test_cache_effectiveness(self):
        """Test cache effectiveness in reducing API calls"""
        cache = IntelligentCache(":memory:")
        
        # First request should hit API
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_get.return_value = mock_response
            
            result1 = make_cached_request("https://api.example.com", {"param": "value"})
            assert mock_get.call_count == 1
        
        # Second request should hit cache
        with patch('requests.get') as mock_get:
            result2 = make_cached_request("https://api.example.com", {"param": "value"})
            assert mock_get.call_count == 0
            assert result1 == result2
```

## Monitoring and Metrics

### Key Metrics to Monitor

1. **Request Rate**
   - Requests per minute/hour
   - Peak request times
   - Request distribution

2. **Rate Limit Usage**
   - Current rate limit remaining
   - Rate limit reset time
   - Usage percentage

3. **Error Rates**
   - 429 (Rate Limited) errors
   - 5xx (Server Error) errors
   - Network timeout errors

4. **Cache Performance**
   - Cache hit rate
   - Cache miss rate
   - Cache size and growth

5. **Response Times**
   - Average response time
   - 95th percentile response time
   - Timeout rate

### Monitoring Dashboard

```python
def generate_monitoring_report():
    """Generate comprehensive monitoring report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'rate_limits': {
            'remaining_hour': get_rate_limit_remaining('hour'),
            'remaining_day': get_rate_limit_remaining('day'),
            'reset_time': get_rate_limit_reset_time()
        },
        'request_stats': {
            'total_requests_1h': get_request_count(timedelta(hours=1)),
            'total_requests_24h': get_request_count(timedelta(hours=24)),
            'error_rate_1h': get_error_rate(timedelta(hours=1)),
            'avg_response_time': get_average_response_time(timedelta(hours=1))
        },
        'cache_stats': {
            'hit_rate': get_cache_hit_rate(),
            'total_entries': get_cache_entry_count(),
            'expired_entries': get_expired_cache_count()
        },
        'circuit_breaker': {
            'state': get_circuit_breaker_state(),
            'failure_count': get_circuit_breaker_failure_count()
        }
    }
    
    return report
```

## Conclusion

Proper rate limiting is essential for sustainable API usage. By implementing these best practices:

1. **Respect API limits** through proper backoff and retry logic
2. **Monitor usage patterns** to detect issues early
3. **Cache responses** to minimize API calls
4. **Implement circuit breakers** to prevent cascading failures
5. **Use request queuing** to control concurrency
6. **Monitor and alert** on rate limit issues

You can ensure reliable, efficient, and respectful API usage while maintaining good relationships with data providers.

Remember: Rate limiting is not just about avoiding errors—it's about being a good citizen in the API ecosystem and ensuring long-term access to valuable data sources.
