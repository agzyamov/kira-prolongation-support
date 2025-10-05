"""
Contract tests for TufeCacheService.
Tests the service interface before implementation.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from decimal import Decimal
from src.services.tufe_cache_service import TufeCacheService
from src.models.tufe_data_cache import TufeDataCache
from src.storage import DataStore


class TestTufeCacheService:
    """Contract tests for TufeCacheService."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.data_store = DataStore(self.db_path)
        self.service = TufeCacheService(self.data_store)

    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_get_cached_data_returns_cache_or_none(self):
        """Test that get_cached_data returns TufeDataCache or None."""
        cached_data = self.service.get_cached_data(2024)
        assert cached_data is None or isinstance(cached_data, TufeDataCache)

    def test_cache_data_returns_id(self):
        """Test that cache_data returns an integer ID."""
        cache_id = self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        assert isinstance(cache_id, int)
        assert cache_id > 0

    def test_is_cache_valid_returns_boolean(self):
        """Test that is_cache_valid returns a boolean."""
        # Test with no cached data
        is_valid = self.service.is_cache_valid(2024)
        assert isinstance(is_valid, bool)
        assert not is_valid  # Should be False for non-existent data

    def test_invalidate_cache_returns_boolean(self):
        """Test that invalidate_cache returns a boolean."""
        # First cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Invalidate the cache
        result = self.service.invalidate_cache(2024)
        assert isinstance(result, bool)

    def test_cleanup_expired_cache_returns_count(self):
        """Test that cleanup_expired_cache returns an integer count."""
        count = self.service.cleanup_expired_cache()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_cache_stats_returns_dict(self):
        """Test that get_cache_stats returns a dictionary."""
        stats = self.service.get_cache_stats()
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "expired_entries" in stats

    def test_get_data_lineage_returns_string_or_none(self):
        """Test that get_data_lineage returns string or None."""
        lineage = self.service.get_data_lineage(2024)
        assert lineage is None or isinstance(lineage, str)

    def test_cache_expiration_handling(self):
        """Test that cache expiration is handled correctly."""
        # Cache data with short expiration
        cache_id = self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Check if cache is valid
        is_valid = self.service.is_cache_valid(2024)
        assert is_valid  # Should be valid immediately after caching

    def test_multiple_sources_caching(self):
        """Test that multiple sources can cache data for the same year."""
        # Cache data from different sources
        cache_id_1 = self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "tcmb"}'
        )
        cache_id_2 = self.service.cache_data(
            year=2024,
            rate=Decimal("45.00"),
            source="Manual Entry",
            api_response='{"data": "manual"}'
        )
        
        assert cache_id_1 != cache_id_2
        assert cache_id_1 > 0
        assert cache_id_2 > 0

    def test_cache_data_validation(self):
        """Test that cache_data validates input data."""
        # Test with invalid year
        with pytest.raises(ValueError):
            self.service.cache_data(
                year=1900,  # Invalid year
                rate=Decimal("44.38"),
                source="TCMB EVDS API",
                api_response='{"data": "test"}'
            )
        
        # Test with negative rate
        with pytest.raises(ValueError):
            self.service.cache_data(
                year=2024,
                rate=Decimal("-10.0"),  # Invalid rate
                source="TCMB EVDS API",
                api_response='{"data": "test"}'
            )
