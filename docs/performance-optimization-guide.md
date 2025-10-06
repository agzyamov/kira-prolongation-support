# Performance Optimization Guide: OECD API Integration

**Version**: 1.0.0  
**Date**: 2025-01-27  
**Feature**: 005-omg-can-i

## Overview

This guide provides comprehensive strategies for optimizing the performance of the OECD API integration. It covers caching strategies, request optimization, data processing improvements, and monitoring techniques to ensure fast and efficient TÜFE data fetching.

## Performance Goals

### Target Metrics

- **Response Time**: < 2 seconds for TÜFE data fetch
- **Cache Hit Rate**: > 80% for repeated requests
- **API Request Reduction**: < 20% of requests should hit the API
- **Memory Usage**: < 100MB for cache operations
- **Concurrent Requests**: Support up to 10 simultaneous users

### Key Performance Indicators (KPIs)

1. **Latency Metrics**
   - Average response time
   - 95th percentile response time
   - Time to first byte (TTFB)

2. **Throughput Metrics**
   - Requests per second
   - Data points processed per second
   - Cache operations per second

3. **Efficiency Metrics**
   - Cache hit ratio
   - API request reduction percentage
   - Memory utilization

## Caching Strategies

### 1. Multi-Level Caching

Implement a hierarchical caching system for optimal performance:

```python
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import hashlib

class MultiLevelCache:
    """Multi-level caching system for optimal performance"""
    
    def __init__(self):
        self.l1_cache = {}  # In-memory cache (fastest)
        self.l2_cache = {}  # Database cache (persistent)
        self.l3_cache = {}  # File system cache (backup)
        
        # Cache configuration
        self.l1_ttl = timedelta(minutes=5)    # 5 minutes
        self.l2_ttl = timedelta(hours=24)     # 24 hours
        self.l3_ttl = timedelta(days=7)       # 7 days
        
        # Cache size limits
        self.l1_max_size = 1000
        self.l2_max_size = 10000
        self.l3_max_size = 100000
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from multi-level cache"""
        # Try L1 cache first (fastest)
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            if not self._is_expired(entry, self.l1_ttl):
                entry['access_count'] += 1
                entry['last_accessed'] = datetime.now()
                return entry['data']
            else:
                del self.l1_cache[key]
        
        # Try L2 cache (database)
        if key in self.l2_cache:
            entry = self.l2_cache[key]
            if not self._is_expired(entry, self.l2_ttl):
                # Promote to L1 cache
                self._promote_to_l1(key, entry['data'])
                return entry['data']
            else:
                del self.l2_cache[key]
        
        # Try L3 cache (file system)
        if key in self.l3_cache:
            entry = self.l3_cache[key]
            if not self._is_expired(entry, self.l3_ttl):
                # Promote to L2 and L1 cache
                self._promote_to_l2(key, entry['data'])
                self._promote_to_l1(key, entry['data'])
                return entry['data']
            else:
                del self.l3_cache[key]
        
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[timedelta] = None):
        """Set data in multi-level cache"""
        if ttl is None:
            ttl = self.l2_ttl
        
        entry = {
            'data': data,
            'created_at': datetime.now(),
            'access_count': 0,
            'last_accessed': datetime.now()
        }
        
        # Store in all levels
        self.l1_cache[key] = entry.copy()
        self.l2_cache[key] = entry.copy()
        self.l3_cache[key] = entry.copy()
        
        # Enforce size limits
        self._enforce_size_limits()
    
    def _is_expired(self, entry: Dict, ttl: timedelta) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() - entry['created_at'] > ttl
    
    def _promote_to_l1(self, key: str, data: Any):
        """Promote data to L1 cache"""
        self.l1_cache[key] = {
            'data': data,
            'created_at': datetime.now(),
            'access_count': 1,
            'last_accessed': datetime.now()
        }
    
    def _promote_to_l2(self, key: str, data: Any):
        """Promote data to L2 cache"""
        self.l2_cache[key] = {
            'data': data,
            'created_at': datetime.now(),
            'access_count': 1,
            'last_accessed': datetime.now()
        }
    
    def _enforce_size_limits(self):
        """Enforce cache size limits using LRU eviction"""
        if len(self.l1_cache) > self.l1_max_size:
            self._evict_lru(self.l1_cache, self.l1_max_size)
        
        if len(self.l2_cache) > self.l2_max_size:
            self._evict_lru(self.l2_cache, self.l2_max_size)
        
        if len(self.l3_cache) > self.l3_max_size:
            self._evict_lru(self.l3_cache, self.l3_max_size)
    
    def _evict_lru(self, cache: Dict, max_size: int):
        """Evict least recently used entries"""
        if len(cache) <= max_size:
            return
        
        # Sort by last accessed time
        sorted_items = sorted(
            cache.items(),
            key=lambda x: x[1]['last_accessed']
        )
        
        # Remove oldest entries
        to_remove = len(cache) - max_size
        for key, _ in sorted_items[:to_remove]:
            del cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'l1_size': len(self.l1_cache),
            'l2_size': len(self.l2_cache),
            'l3_size': len(self.l3_cache),
            'l1_hit_rate': self._calculate_hit_rate(self.l1_cache),
            'l2_hit_rate': self._calculate_hit_rate(self.l2_cache),
            'l3_hit_rate': self._calculate_hit_rate(self.l3_cache)
        }
    
    def _calculate_hit_rate(self, cache: Dict) -> float:
        """Calculate hit rate for cache level"""
        if not cache:
            return 0.0
        
        total_accesses = sum(entry['access_count'] for entry in cache.values())
        total_entries = len(cache)
        
        return total_accesses / total_entries if total_entries > 0 else 0.0
```

### 2. Intelligent Cache Warming

Pre-populate cache with frequently accessed data:

```python
class CacheWarmer:
    """Intelligent cache warming for frequently accessed data"""
    
    def __init__(self, cache_service, api_client):
        self.cache_service = cache_service
        self.api_client = api_client
        self.access_patterns = {}
    
    def track_access_pattern(self, year: int, month: int):
        """Track data access patterns"""
        key = f"{year}_{month}"
        if key not in self.access_patterns:
            self.access_patterns[key] = {
                'count': 0,
                'last_accessed': datetime.now(),
                'frequency': 0.0
            }
        
        self.access_patterns[key]['count'] += 1
        self.access_patterns[key]['last_accessed'] = datetime.now()
        
        # Calculate frequency (accesses per hour)
        time_since_first = datetime.now() - self.access_patterns[key]['last_accessed']
        hours = max(1, time_since_first.total_seconds() / 3600)
        self.access_patterns[key]['frequency'] = self.access_patterns[key]['count'] / hours
    
    def identify_hot_data(self, threshold: float = 2.0) -> List[Tuple[int, int]]:
        """Identify frequently accessed data"""
        hot_data = []
        for key, pattern in self.access_patterns.items():
            if pattern['frequency'] >= threshold:
                year, month = map(int, key.split('_'))
                hot_data.append((year, month))
        
        return sorted(hot_data, key=lambda x: self.access_patterns[f"{x[0]}_{x[1]}"]['frequency'], reverse=True)
    
    def warm_cache(self, max_items: int = 50):
        """Warm cache with frequently accessed data"""
        hot_data = self.identify_hot_data()
        
        for year, month in hot_data[:max_items]:
            try:
                # Check if already in cache
                if self.cache_service.get_cached_data(year, month):
                    continue
                
                # Fetch and cache data
                data = self.api_client.fetch_tufe_data(year, year)
                self.cache_service.cache_data(data, ttl_hours=24)
                
                print(f"Warmed cache for {year}-{month:02d}")
                
            except Exception as e:
                print(f"Failed to warm cache for {year}-{month:02d}: {e}")
    
    def schedule_cache_warming(self, interval_hours: int = 6):
        """Schedule periodic cache warming"""
        import threading
        import time
        
        def warm_periodically():
            while True:
                try:
                    self.warm_cache()
                    time.sleep(interval_hours * 3600)
                except Exception as e:
                    print(f"Cache warming error: {e}")
                    time.sleep(3600)  # Wait 1 hour before retry
        
        thread = threading.Thread(target=warm_periodically, daemon=True)
        thread.start()
```

### 3. Cache Compression

Implement data compression to reduce memory usage:

```python
import gzip
import pickle
import base64

class CompressedCache:
    """Cache with data compression for memory efficiency"""
    
    def __init__(self, compression_level: int = 6):
        self.compression_level = compression_level
        self.cache = {}
    
    def _compress_data(self, data: Any) -> str:
        """Compress data using gzip and base64"""
        # Serialize data
        serialized = pickle.dumps(data)
        
        # Compress data
        compressed = gzip.compress(serialized, compresslevel=self.compression_level)
        
        # Encode as base64 string
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        return encoded
    
    def _decompress_data(self, compressed_data: str) -> Any:
        """Decompress data from base64 and gzip"""
        # Decode from base64
        compressed = base64.b64decode(compressed_data.encode('utf-8'))
        
        # Decompress data
        serialized = gzip.decompress(compressed)
        
        # Deserialize data
        data = pickle.loads(serialized)
        
        return data
    
    def set(self, key: str, data: Any, ttl: Optional[timedelta] = None):
        """Set compressed data in cache"""
        compressed_data = self._compress_data(data)
        
        entry = {
            'data': compressed_data,
            'created_at': datetime.now(),
            'ttl': ttl or timedelta(hours=24),
            'access_count': 0,
            'last_accessed': datetime.now()
        }
        
        self.cache[key] = entry
    
    def get(self, key: str) -> Optional[Any]:
        """Get and decompress data from cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if datetime.now() - entry['created_at'] > entry['ttl']:
            del self.cache[key]
            return None
        
        # Update access statistics
        entry['access_count'] += 1
        entry['last_accessed'] = datetime.now()
        
        # Decompress and return data
        return self._decompress_data(entry['data'])
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        total_original_size = 0
        total_compressed_size = 0
        
        for entry in self.cache.values():
            # Estimate original size (rough approximation)
            original_size = len(entry['data']) * 2  # Assume 50% compression
            total_original_size += original_size
            total_compressed_size += len(entry['data'])
        
        compression_ratio = total_compressed_size / total_original_size if total_original_size > 0 else 0
        
        return {
            'total_entries': len(self.cache),
            'estimated_original_size': total_original_size,
            'compressed_size': total_compressed_size,
            'compression_ratio': compression_ratio,
            'space_saved': total_original_size - total_compressed_size
        }
```

## Request Optimization

### 1. Connection Pooling

Optimize HTTP connections with connection pooling:

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
import ssl

class OptimizedHTTPClient:
    """Optimized HTTP client with connection pooling"""
    
    def __init__(self, max_connections: int = 20, max_keepalive: int = 10):
        self.session = requests.Session()
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=max_connections,
            pool_maxsize=max_keepalive,
            max_retries=Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Configure SSL context for better performance
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'TÜFE Data Fetcher/1.0',
            'Accept': 'application/xml, text/xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Optimized GET request"""
        # Set default timeout
        kwargs.setdefault('timeout', (10, 30))
        
        # Enable streaming for large responses
        if 'stream' not in kwargs:
            kwargs['stream'] = True
        
        response = self.session.get(url, **kwargs)
        
        # Handle streaming response
        if kwargs.get('stream'):
            response.content  # Consume the response
        
        return response
    
    def close(self):
        """Close the session"""
        self.session.close()
```

### 2. Batch Request Processing

Process multiple requests efficiently:

```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class BatchRequestProcessor:
    """Process multiple API requests efficiently"""
    
    def __init__(self, max_concurrent: int = 10, delay_between_batches: float = 0.1):
        self.max_concurrent = max_concurrent
        self.delay_between_batches = delay_between_batches
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of URLs concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                task = self._fetch_with_semaphore(session, url)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'url': urls[i],
                        'error': str(result),
                        'success': False
                    })
                else:
                    processed_results.append({
                        'url': urls[i],
                        'data': result,
                        'success': True
                    })
            
            return processed_results
    
    async def _fetch_with_semaphore(self, session: aiohttp.ClientSession, url: str) -> Any:
        """Fetch URL with semaphore to limit concurrency"""
        async with self.semaphore:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_response(content)
                    else:
                        raise Exception(f"HTTP {response.status}")
            except Exception as e:
                raise Exception(f"Request failed: {e}")
    
    def _parse_response(self, content: str) -> Any:
        """Parse response content"""
        # Implement parsing logic based on content type
        if content.startswith('<?xml'):
            return self._parse_xml(content)
        else:
            return self._parse_json(content)
    
    def _parse_xml(self, content: str) -> Any:
        """Parse XML content"""
        # Implement XML parsing
        pass
    
    def _parse_json(self, content: str) -> Any:
        """Parse JSON content"""
        # Implement JSON parsing
        pass
    
    async def process_year_range(self, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Process multiple years efficiently"""
        urls = []
        for year in range(start_year, end_year + 1):
            url = f"https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime={year}&endTime={year}"
            urls.append(url)
        
        # Process in batches
        batch_size = self.max_concurrent
        all_results = []
        
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            batch_results = await self.process_batch(batch_urls)
            all_results.extend(batch_results)
            
            # Add delay between batches
            if i + batch_size < len(urls):
                await asyncio.sleep(self.delay_between_batches)
        
        return all_results
```

### 3. Request Deduplication

Prevent duplicate requests:

```python
import hashlib
from typing import Set, Dict, Any
import asyncio

class RequestDeduplicator:
    """Prevent duplicate requests using request deduplication"""
    
    def __init__(self):
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.completed_requests: Dict[str, Any] = {}
        self.request_hashes: Set[str] = set()
    
    def _generate_request_hash(self, url: str, params: Dict[str, Any] = None) -> str:
        """Generate hash for request deduplication"""
        request_data = {
            'url': url,
            'params': params or {}
        }
        request_string = str(sorted(request_data.items()))
        return hashlib.md5(request_string.encode()).hexdigest()
    
    async def make_request(self, url: str, params: Dict[str, Any] = None) -> Any:
        """Make request with deduplication"""
        request_hash = self._generate_request_hash(url, params)
        
        # Check if request is already completed
        if request_hash in self.completed_requests:
            return self.completed_requests[request_hash]
        
        # Check if request is already pending
        if request_hash in self.pending_requests:
            return await self.pending_requests[request_hash]
        
        # Create new request
        future = asyncio.Future()
        self.pending_requests[request_hash] = future
        
        try:
            # Make the actual request
            result = await self._execute_request(url, params)
            
            # Store result
            self.completed_requests[request_hash] = result
            
            # Complete the future
            future.set_result(result)
            
            return result
            
        except Exception as e:
            # Complete the future with error
            future.set_exception(e)
            raise
        
        finally:
            # Clean up pending request
            if request_hash in self.pending_requests:
                del self.pending_requests[request_hash]
    
    async def _execute_request(self, url: str, params: Dict[str, Any] = None) -> Any:
        """Execute the actual request"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"HTTP {response.status}")
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        return {
            'pending_requests': len(self.pending_requests),
            'completed_requests': len(self.completed_requests),
            'total_hashes': len(self.request_hashes),
            'deduplication_rate': len(self.completed_requests) / max(1, len(self.request_hashes))
        }
```

## Data Processing Optimization

### 1. Parallel Data Processing

Process data in parallel for better performance:

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import List, Any, Callable

class ParallelDataProcessor:
    """Parallel data processing for better performance"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers * 2)
    
    def process_data_parallel(self, data: List[Any], process_func: Callable, use_threads: bool = False) -> List[Any]:
        """Process data in parallel"""
        if use_threads:
            with self.thread_pool as executor:
                results = list(executor.map(process_func, data))
        else:
            with self.process_pool as executor:
                results = list(executor.map(process_func, data))
        
        return results
    
    def process_data_chunks(self, data: List[Any], process_func: Callable, chunk_size: int = 100) -> List[Any]:
        """Process data in chunks for memory efficiency"""
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        results = []
        for chunk in chunks:
            chunk_results = self.process_data_parallel(chunk, process_func)
            results.extend(chunk_results)
        
        return results
    
    def process_with_progress(self, data: List[Any], process_func: Callable, progress_callback: Callable = None) -> List[Any]:
        """Process data with progress tracking"""
        results = []
        total = len(data)
        
        for i, item in enumerate(data):
            result = process_func(item)
            results.append(result)
            
            if progress_callback:
                progress = (i + 1) / total
                progress_callback(progress, i + 1, total)
        
        return results
    
    def close(self):
        """Close thread and process pools"""
        self.process_pool.shutdown(wait=True)
        self.thread_pool.shutdown(wait=True)
```

### 2. Memory-Efficient Data Processing

Process large datasets without excessive memory usage:

```python
import gc
from typing import Iterator, Any, Callable

class MemoryEfficientProcessor:
    """Memory-efficient data processing"""
    
    def __init__(self, chunk_size: int = 1000, gc_threshold: int = 10000):
        self.chunk_size = chunk_size
        self.gc_threshold = gc_threshold
        self.processed_count = 0
    
    def process_large_dataset(self, data: Iterator[Any], process_func: Callable) -> Iterator[Any]:
        """Process large dataset in chunks"""
        chunk = []
        
        for item in data:
            chunk.append(item)
            
            if len(chunk) >= self.chunk_size:
                # Process chunk
                for result in self._process_chunk(chunk, process_func):
                    yield result
                
                # Clear chunk and trigger garbage collection
                chunk.clear()
                self.processed_count += self.chunk_size
                
                if self.processed_count >= self.gc_threshold:
                    gc.collect()
                    self.processed_count = 0
        
        # Process remaining items
        if chunk:
            for result in self._process_chunk(chunk, process_func):
                yield result
    
    def _process_chunk(self, chunk: List[Any], process_func: Callable) -> Iterator[Any]:
        """Process a chunk of data"""
        for item in chunk:
            try:
                result = process_func(item)
                yield result
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
    
    def process_with_memory_monitoring(self, data: List[Any], process_func: Callable) -> List[Any]:
        """Process data with memory monitoring"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        results = []
        for i, item in enumerate(data):
            result = process_func(item)
            results.append(result)
            
            # Monitor memory usage
            if i % 1000 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                if memory_increase > 100:  # More than 100MB increase
                    print(f"Memory usage increased by {memory_increase:.1f}MB")
                    gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - initial_memory
        
        print(f"Total memory increase: {total_increase:.1f}MB")
        return results
```

### 3. Data Validation Optimization

Optimize data validation for better performance:

```python
import re
from typing import List, Dict, Any, Set

class OptimizedDataValidator:
    """Optimized data validation for better performance"""
    
    def __init__(self):
        # Pre-compile regex patterns
        self.year_pattern = re.compile(r'^(19|20)\d{2}$')
        self.month_pattern = re.compile(r'^(0?[1-9]|1[0-2])$')
        self.rate_pattern = re.compile(r'^\d+(\.\d+)?$')
        
        # Cache validation results
        self.validation_cache: Dict[str, bool] = {}
        
        # Set up validation rules
        self.validation_rules = {
            'year': self._validate_year,
            'month': self._validate_month,
            'rate': self._validate_rate,
            'source': self._validate_source
        }
    
    def validate_batch_optimized(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimized batch validation"""
        valid_data = []
        invalid_data = []
        
        for item in data:
            # Check cache first
            cache_key = self._generate_cache_key(item)
            if cache_key in self.validation_cache:
                if self.validation_cache[cache_key]:
                    valid_data.append(item)
                else:
                    invalid_data.append(item)
                continue
            
            # Validate item
            is_valid = self._validate_item_fast(item)
            self.validation_cache[cache_key] = is_valid
            
            if is_valid:
                valid_data.append(item)
            else:
                invalid_data.append(item)
        
        return valid_data
    
    def _validate_item_fast(self, item: Dict[str, Any]) -> bool:
        """Fast validation using pre-compiled patterns"""
        try:
            # Validate year
            year = str(item.get('year', ''))
            if not self.year_pattern.match(year):
                return False
            
            # Validate month
            month = str(item.get('month', ''))
            if not self.month_pattern.match(month):
                return False
            
            # Validate rate
            rate = str(item.get('value', ''))
            if not self.rate_pattern.match(rate):
                return False
            
            # Validate source
            source = item.get('source', '')
            if not source or not isinstance(source, str):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_year(self, year: Any) -> bool:
        """Validate year field"""
        if not isinstance(year, (int, str)):
            return False
        
        year_str = str(year)
        return self.year_pattern.match(year_str) is not None
    
    def _validate_month(self, month: Any) -> bool:
        """Validate month field"""
        if not isinstance(month, (int, str)):
            return False
        
        month_str = str(month)
        return self.month_pattern.match(month_str) is not None
    
    def _validate_rate(self, rate: Any) -> bool:
        """Validate rate field"""
        if not isinstance(rate, (int, float, str)):
            return False
        
        rate_str = str(rate)
        if not self.rate_pattern.match(rate_str):
            return False
        
        rate_float = float(rate_str)
        return 0 <= rate_float <= 200
    
    def _validate_source(self, source: Any) -> bool:
        """Validate source field"""
        return isinstance(source, str) and len(source.strip()) > 0
    
    def _generate_cache_key(self, item: Dict[str, Any]) -> str:
        """Generate cache key for validation result"""
        key_parts = [
            str(item.get('year', '')),
            str(item.get('month', '')),
            str(item.get('value', '')),
            str(item.get('source', ''))
        ]
        return '|'.join(key_parts)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        total_validations = len(self.validation_cache)
        valid_count = sum(1 for is_valid in self.validation_cache.values() if is_valid)
        invalid_count = total_validations - valid_count
        
        return {
            'total_validations': total_validations,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'validation_rate': valid_count / total_validations if total_validations > 0 else 0,
            'cache_hit_rate': total_validations / max(1, total_validations)
        }
```

## Monitoring and Profiling

### 1. Performance Monitoring

Monitor performance metrics in real-time:

```python
import time
import psutil
import threading
from typing import Dict, Any, List
from collections import deque
import json

class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics = {
            'response_times': deque(maxlen=max_samples),
            'memory_usage': deque(maxlen=max_samples),
            'cpu_usage': deque(maxlen=max_samples),
            'cache_hits': deque(maxlen=max_samples),
            'api_requests': deque(maxlen=max_samples)
        }
        
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time': 2.0,  # seconds
            'max_memory_usage': 100,   # MB
            'max_cpu_usage': 80,       # percentage
            'min_cache_hit_rate': 0.8  # 80%
        }
    
    def start_monitoring(self, interval: float = 1.0):
        """Start performance monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Collect system metrics
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
                
                # Store metrics
                self.metrics['memory_usage'].append(memory_mb)
                self.metrics['cpu_usage'].append(cpu_percent)
                
                # Check thresholds
                self._check_thresholds(memory_mb, cpu_percent)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def record_response_time(self, response_time: float):
        """Record API response time"""
        self.metrics['response_times'].append(response_time)
        
        # Check threshold
        if response_time > self.thresholds['max_response_time']:
            print(f"⚠️ High response time: {response_time:.2f}s")
    
    def record_cache_hit(self, hit: bool):
        """Record cache hit/miss"""
        self.metrics['cache_hits'].append(1 if hit else 0)
    
    def record_api_request(self, success: bool):
        """Record API request"""
        self.metrics['api_requests'].append(1 if success else 0)
    
    def _check_thresholds(self, memory_mb: float, cpu_percent: float):
        """Check performance thresholds"""
        if memory_mb > self.thresholds['max_memory_usage']:
            print(f"⚠️ High memory usage: {memory_mb:.1f}MB")
        
        if cpu_percent > self.thresholds['max_cpu_usage']:
            print(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
        
        # Check cache hit rate
        if len(self.metrics['cache_hits']) > 100:
            hit_rate = sum(self.metrics['cache_hits']) / len(self.metrics['cache_hits'])
            if hit_rate < self.thresholds['min_cache_hit_rate']:
                print(f"⚠️ Low cache hit rate: {hit_rate:.1%}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    'current': values[-1] if values else 0,
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        return summary
    
    def export_metrics(self, filename: str):
        """Export metrics to file"""
        data = {
            'timestamp': time.time(),
            'metrics': dict(self.metrics),
            'summary': self.get_performance_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
```

### 2. Profiling Integration

Integrate profiling for detailed performance analysis:

```python
import cProfile
import pstats
import io
from contextlib import contextmanager

class Profiler:
    """Performance profiler for detailed analysis"""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.profiles = {}
    
    @contextmanager
    def profile(self, name: str):
        """Context manager for profiling"""
        self.profiler.enable()
        try:
            yield
        finally:
            self.profiler.disable()
            self.profiles[name] = pstats.Stats(self.profiler)
    
    def get_profile_summary(self, name: str, top_n: int = 10) -> str:
        """Get profile summary"""
        if name not in self.profiles:
            return f"Profile '{name}' not found"
        
        stats = self.profiles[name]
        
        # Capture output
        output = io.StringIO()
        stats.print_stats(top_n, file=output)
        
        return output.getvalue()
    
    def compare_profiles(self, name1: str, name2: str) -> str:
        """Compare two profiles"""
        if name1 not in self.profiles or name2 not in self.profiles:
            return "One or both profiles not found"
        
        stats1 = self.profiles[name1]
        stats2 = self.profiles[name2]
        
        # Capture output
        output = io.StringIO()
        stats1.print_stats(file=output)
        output.write("\n" + "="*50 + "\n")
        stats2.print_stats(file=output)
        
        return output.getvalue()
    
    def export_profile(self, name: str, filename: str):
        """Export profile to file"""
        if name not in self.profiles:
            return
        
        stats = self.profiles[name]
        stats.dump_stats(filename)
    
    def get_all_profiles(self) -> List[str]:
        """Get list of all profile names"""
        return list(self.profiles.keys())
```

## Configuration and Tuning

### 1. Performance Configuration

```python
# Performance configuration
PERFORMANCE_CONFIG = {
    # Caching configuration
    'cache': {
        'l1_ttl_minutes': 5,
        'l2_ttl_hours': 24,
        'l3_ttl_days': 7,
        'l1_max_size': 1000,
        'l2_max_size': 10000,
        'l3_max_size': 100000,
        'compression_level': 6
    },
    
    # HTTP configuration
    'http': {
        'max_connections': 20,
        'max_keepalive': 10,
        'timeout_connect': 10,
        'timeout_read': 30,
        'retry_total': 3,
        'retry_backoff_factor': 1
    },
    
    # Processing configuration
    'processing': {
        'max_workers': None,  # Auto-detect
        'chunk_size': 1000,
        'gc_threshold': 10000,
        'batch_size': 10,
        'delay_between_batches': 0.1
    },
    
    # Monitoring configuration
    'monitoring': {
        'monitor_interval': 1.0,
        'max_samples': 1000,
        'thresholds': {
            'max_response_time': 2.0,
            'max_memory_usage': 100,
            'max_cpu_usage': 80,
            'min_cache_hit_rate': 0.8
        }
    }
}
```

### 2. Environment-Specific Tuning

```python
def get_optimized_config(environment: str) -> Dict[str, Any]:
    """Get optimized configuration for specific environment"""
    
    base_config = PERFORMANCE_CONFIG.copy()
    
    if environment == 'development':
        # Development: More verbose logging, smaller caches
        base_config['cache']['l1_max_size'] = 100
        base_config['cache']['l2_max_size'] = 1000
        base_config['http']['max_connections'] = 5
        base_config['processing']['max_workers'] = 2
        
    elif environment == 'production':
        # Production: Optimized for performance and reliability
        base_config['cache']['l1_max_size'] = 5000
        base_config['cache']['l2_max_size'] = 50000
        base_config['http']['max_connections'] = 50
        base_config['processing']['max_workers'] = None  # Auto-detect
        
    elif environment == 'testing':
        # Testing: Fast, minimal resources
        base_config['cache']['l1_max_size'] = 50
        base_config['cache']['l2_max_size'] = 500
        base_config['http']['max_connections'] = 2
        base_config['processing']['max_workers'] = 1
        
    return base_config
```

## Best Practices Summary

### 1. Caching Best Practices

- **Use multi-level caching** for optimal performance
- **Implement cache warming** for frequently accessed data
- **Use compression** to reduce memory usage
- **Monitor cache hit rates** and adjust TTL accordingly
- **Implement cache invalidation** strategies

### 2. Request Optimization

- **Use connection pooling** to reuse HTTP connections
- **Implement request deduplication** to prevent duplicate calls
- **Use batch processing** for multiple requests
- **Implement proper backoff** for rate limiting
- **Monitor request patterns** and optimize accordingly

### 3. Data Processing

- **Use parallel processing** for CPU-intensive tasks
- **Process data in chunks** to manage memory usage
- **Optimize validation** with pre-compiled patterns
- **Use streaming** for large datasets
- **Implement progress tracking** for long operations

### 4. Monitoring and Profiling

- **Monitor key metrics** in real-time
- **Set performance thresholds** and alerts
- **Use profiling** to identify bottlenecks
- **Export metrics** for analysis
- **Regular performance reviews** and optimization

### 5. Configuration Management

- **Environment-specific tuning** for different deployments
- **Configurable thresholds** for monitoring
- **Easy configuration updates** without code changes
- **Performance testing** with different configurations
- **Documentation** of configuration options

By following these optimization strategies, you can achieve significant performance improvements in the OECD API integration while maintaining reliability and scalability.
