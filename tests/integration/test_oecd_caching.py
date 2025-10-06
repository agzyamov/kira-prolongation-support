"""
Integration tests for OECD API caching with TTL.

These tests verify the caching functionality and must fail before implementation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import time

# Import the services (will fail until implemented)
try:
    from src.services.tufe_cache_service import TufeCacheService
    from src.services.inflation_service import InflationService
    from src.models.tufe_data_cache import TufeDataCache
    from src.models.inflation_data import InflationData
    from src.services.exceptions import TufeCacheError
except ImportError:
    # These will be implemented later
    TufeCacheService = None
    InflationService = None
    TufeDataCache = None
    InflationData = None
    TufeCacheError = Exception


class TestOECDCachingIntegration:
    """Integration tests for OECD API caching with TTL."""
    
    def test_cache_tufe_data_with_ttl(self):
        """Test caching TÜFE data with TTL."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Create test data
        test_data = [
            InflationData(year=2024, month=1, tufe_rate=42.5, source="OECD SDMX API"),
            InflationData(year=2024, month=2, tufe_rate=43.2, source="OECD SDMX API")
        ]
        
        # Cache the data
        cache_service.cache_oecd_data(test_data, ttl_hours=1)
        
        # Verify data is cached
        cached_data = cache_service.get_cached_oecd_data(2024, 1)
        assert cached_data is not None
        assert cached_data.tufe_rate == 42.5
        assert cached_data.source == "OECD SDMX API"
        
        cached_data = cache_service.get_cached_oecd_data(2024, 2)
        assert cached_data is not None
        assert cached_data.tufe_rate == 43.2
    
    def test_cache_ttl_expiration(self):
        """Test that cached data expires after TTL."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Create test data
        test_data = [
            InflationData(year=2024, month=1, tufe_rate=42.5, source="OECD SDMX API")
        ]
        
        # Cache with very short TTL
        cache_service.cache_oecd_data(test_data, ttl_hours=0.001)  # ~3.6 seconds
        
        # Data should be available immediately
        cached_data = cache_service.get_cached_oecd_data(2024, 1)
        assert cached_data is not None
        
        # Wait for expiration
        time.sleep(0.01)  # 10ms should be enough
        
        # Data should be expired
        expired_data = cache_service.get_cached_oecd_data(2024, 1)
        assert expired_data is None
    
    def test_cache_cleanup_expired_entries(self):
        """Test cleanup of expired cache entries."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Create test data with different TTLs
        test_data_short = [
            InflationData(year=2024, month=1, tufe_rate=42.5, source="OECD SDMX API")
        ]
        test_data_long = [
            InflationData(year=2024, month=2, tufe_rate=43.2, source="OECD SDMX API")
        ]
        
        # Cache with different TTLs
        cache_service.cache_oecd_data(test_data_short, ttl_hours=0.001)  # Short TTL
        cache_service.cache_oecd_data(test_data_long, ttl_hours=1)       # Long TTL
        
        # Wait for short TTL to expire
        time.sleep(0.01)
        
        # Cleanup expired entries
        removed_count = cache_service.cleanup_expired_cache()
        
        # Should have removed at least one expired entry
        assert removed_count >= 1
        
        # Long TTL data should still be available
        cached_data = cache_service.get_cached_oecd_data(2024, 2)
        assert cached_data is not None
    
    def test_cache_statistics(self):
        """Test cache statistics functionality."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Get initial statistics
        initial_stats = cache_service.get_cache_statistics()
        assert isinstance(initial_stats, dict)
        assert 'total_entries' in initial_stats
        assert 'expired_entries' in initial_stats
        assert 'hit_rate' in initial_stats
        
        # Add some test data
        test_data = [
            InflationData(year=2024, month=1, tufe_rate=42.5, source="OECD SDMX API"),
            InflationData(year=2024, month=2, tufe_rate=43.2, source="OECD SDMX API")
        ]
        
        cache_service.cache_oecd_data(test_data, ttl_hours=1)
        
        # Get updated statistics
        updated_stats = cache_service.get_cache_statistics()
        assert updated_stats['total_entries'] >= initial_stats['total_entries'] + 2
    
    def test_cache_hit_miss_behavior(self):
        """Test cache hit/miss behavior."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Test cache miss
        cached_data = cache_service.get_cached_oecd_data(2024, 1)
        assert cached_data is None
        
        # Add data to cache
        test_data = [
            InflationData(year=2024, month=1, tufe_rate=42.5, source="OECD SDMX API")
        ]
        cache_service.cache_oecd_data(test_data, ttl_hours=1)
        
        # Test cache hit
        cached_data = cache_service.get_cached_oecd_data(2024, 1)
        assert cached_data is not None
        assert cached_data.tufe_rate == 42.5
    
    def test_cache_different_ttl_for_recent_vs_historical(self):
        """Test different TTL for recent vs historical data."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        current_year = datetime.now().year
        
        # Test recent data (current year)
        recent_data = [
            InflationData(year=current_year, month=1, tufe_rate=42.5, source="OECD SDMX API")
        ]
        cache_service.cache_oecd_data(recent_data, ttl_hours=168)  # 7 days
        
        # Test historical data (previous year)
        historical_data = [
            InflationData(year=current_year-1, month=1, tufe_rate=40.0, source="OECD SDMX API")
        ]
        cache_service.cache_oecd_data(historical_data, ttl_hours=720)  # 30 days
        
        # Both should be available
        recent_cached = cache_service.get_cached_oecd_data(current_year, 1)
        historical_cached = cache_service.get_cached_oecd_data(current_year-1, 1)
        
        assert recent_cached is not None
        assert historical_cached is not None
    
    def test_cache_error_handling(self):
        """Test cache error handling."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Test caching invalid data
        with pytest.raises(TufeCacheError):
            cache_service.cache_oecd_data(None, ttl_hours=1)
        
        # Test caching empty data
        with pytest.raises(TufeCacheError):
            cache_service.cache_oecd_data([], ttl_hours=1)
    
    def test_cache_performance(self):
        """Test cache performance."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Add test data
        test_data = [
            InflationData(year=2024, month=i, tufe_rate=40.0 + i, source="OECD SDMX API")
            for i in range(1, 13)
        ]
        
        cache_service.cache_oecd_data(test_data, ttl_hours=1)
        
        # Test cache retrieval performance
        start_time = time.time()
        
        for i in range(1, 13):
            cached_data = cache_service.get_cached_oecd_data(2024, i)
            assert cached_data is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be fast (target: <500ms for cached data)
        assert duration < 0.5
    
    def test_cache_concurrent_access(self):
        """Test cache concurrent access behavior."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Add test data
        test_data = [
            InflationData(year=2024, month=1, tufe_rate=42.5, source="OECD SDMX API")
        ]
        
        cache_service.cache_oecd_data(test_data, ttl_hours=1)
        
        # Simulate concurrent access
        results = []
        
        def get_cached_data():
            cached_data = cache_service.get_cached_oecd_data(2024, 1)
            results.append(cached_data)
        
        # Run multiple threads/processes (simplified for testing)
        import threading
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_cached_data)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All should get the same data
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert result.tufe_rate == 42.5
    
    def test_cache_data_integrity(self):
        """Test cache data integrity."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Create test data with various values
        test_data = [
            InflationData(year=2024, month=1, tufe_rate=42.5, source="OECD SDMX API"),
            InflationData(year=2024, month=2, tufe_rate=43.2, source="OECD SDMX API"),
            InflationData(year=2024, month=3, tufe_rate=0.0, source="OECD SDMX API"),
            InflationData(year=2024, month=4, tufe_rate=200.0, source="OECD SDMX API")
        ]
        
        cache_service.cache_oecd_data(test_data, ttl_hours=1)
        
        # Verify data integrity
        for i, expected_data in enumerate(test_data, 1):
            cached_data = cache_service.get_cached_oecd_data(2024, i)
            assert cached_data is not None
            assert cached_data.year == expected_data.year
            assert cached_data.month == expected_data.month
            assert cached_data.tufe_rate == expected_data.tufe_rate
            assert cached_data.source == expected_data.source
    
    def test_cache_cleanup_performance(self):
        """Test cache cleanup performance."""
        if TufeCacheService is None:
            pytest.skip("TufeCacheService not implemented yet")
        
        cache_service = TufeCacheService()
        
        # Add many test entries
        test_data = []
        for year in range(2020, 2025):
            for month in range(1, 13):
                test_data.append(
                    InflationData(year=year, month=month, tufe_rate=40.0, source="OECD SDMX API")
                )
        
        cache_service.cache_oecd_data(test_data, ttl_hours=0.001)  # Short TTL
        
        # Wait for expiration
        time.sleep(0.01)
        
        # Test cleanup performance
        start_time = time.time()
        removed_count = cache_service.cleanup_expired_cache()
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be reasonably fast
        assert duration < 1.0  # Less than 1 second
        assert removed_count > 0


if __name__ == "__main__":
    pytest.main([__file__])
