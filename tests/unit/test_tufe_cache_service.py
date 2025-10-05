"""
Unit tests for TufeCacheService.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from decimal import Decimal
from src.services.tufe_cache_service import TufeCacheService
from src.models.tufe_data_cache import TufeDataCache
from src.storage import DataStore
from src.services.exceptions import TufeCacheError


class TestTufeCacheService:
    """Unit tests for TufeCacheService."""

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

    def test_get_cached_data_none(self):
        """Test getting cached data when none exists."""
        cached_data = self.service.get_cached_data(2024)
        assert cached_data is None

    def test_cache_data_success(self):
        """Test caching data successfully."""
        cache_id = self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        assert isinstance(cache_id, int)
        assert cache_id > 0

    def test_get_cached_data_success(self):
        """Test getting cached data successfully."""
        # Cache some data first
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Get the cached data
        cached_data = self.service.get_cached_data(2024)
        assert cached_data is not None
        assert cached_data.year == 2024
        assert cached_data.tufe_rate == Decimal("44.38")
        assert cached_data.source_name == "TCMB EVDS API"

    def test_is_cache_valid_true(self):
        """Test checking cache validity when valid."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Check if cache is valid
        is_valid = self.service.is_cache_valid(2024)
        assert is_valid is True

    def test_is_cache_valid_false(self):
        """Test checking cache validity when invalid."""
        # Check for non-existent cache
        is_valid = self.service.is_cache_valid(2024)
        assert is_valid is False

    def test_invalidate_cache_success(self):
        """Test invalidating cache successfully."""
        # Cache some data first
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Verify cache is initially valid
        assert self.service.is_cache_valid(2024) is True
        
        # Invalidate the cache
        result = self.service.invalidate_cache(2024)
        assert result is True
        
        # Verify cache is now invalid
        assert self.service.is_cache_valid(2024) is False

    def test_invalidate_cache_not_found(self):
        """Test invalidating non-existent cache."""
        result = self.service.invalidate_cache(2024)
        assert result is False

    def test_cleanup_expired_cache(self):
        """Test cleaning up expired cache entries."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Cleanup expired cache
        expired_count = self.service.cleanup_expired_cache()
        assert isinstance(expired_count, int)
        assert expired_count >= 0

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Get cache stats
        stats = self.service.get_cache_stats()
        
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "expired_entries" in stats
        assert "validity_rate" in stats
        assert stats["total_entries"] >= 1

    def test_get_data_lineage_success(self):
        """Test getting data lineage successfully."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Get data lineage
        lineage = self.service.get_data_lineage(2024)
        assert lineage is not None
        assert "TÜFE data for 2024" in lineage
        assert "44.38%" in lineage
        assert "TCMB EVDS API" in lineage

    def test_get_data_lineage_not_found(self):
        """Test getting data lineage for non-existent data."""
        lineage = self.service.get_data_lineage(2024)
        assert lineage is None

    def test_get_all_cached_years(self):
        """Test getting all cached years."""
        # Cache data for multiple years
        self.service.cache_data(
            year=2023,
            rate=Decimal("43.50"),
            source="TCMB EVDS API",
            api_response='{"data": "2023"}'
        )
        
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "2024"}'
        )
        
        # Get all cached years
        years = self.service.get_all_cached_years()
        assert 2023 in years
        assert 2024 in years
        assert years == sorted(years)  # Should be sorted

    def test_get_cache_by_source(self):
        """Test getting cache entries by source."""
        # Cache data from different sources
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "tcmb"}'
        )
        
        self.service.cache_data(
            year=2024,
            rate=Decimal("45.00"),
            source="Manual Entry",
            api_response='{"data": "manual"}'
        )
        
        # Get cache by source
        tcmb_cache = self.service.get_cache_by_source("TCMB EVDS API")
        manual_cache = self.service.get_cache_by_source("Manual Entry")
        
        assert len(tcmb_cache) == 1
        assert len(manual_cache) == 1
        assert tcmb_cache[0].source_name == "TCMB EVDS API"
        assert manual_cache[0].source_name == "Manual Entry"

    def test_extend_cache_expiration(self):
        """Test extending cache expiration."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Extend expiration
        result = self.service.extend_cache_expiration(2024, 12)  # 12 hours
        assert result is True

    def test_extend_cache_expiration_not_found(self):
        """Test extending expiration for non-existent cache."""
        result = self.service.extend_cache_expiration(2024, 12)
        assert result is False

    def test_mark_cache_as_validated(self):
        """Test marking cache as validated."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Mark as validated
        result = self.service.mark_cache_as_validated(2024)
        assert result is True

    def test_mark_cache_as_validated_not_found(self):
        """Test marking non-existent cache as validated."""
        result = self.service.mark_cache_as_validated(2024)
        assert result is False

    def test_get_cache_age(self):
        """Test getting cache age."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Get cache age
        age_hours = self.service.get_cache_age(2024)
        assert age_hours is not None
        assert age_hours >= 0

    def test_get_cache_age_not_found(self):
        """Test getting age for non-existent cache."""
        age_hours = self.service.get_cache_age(2024)
        assert age_hours is None

    def test_get_cache_remaining_time(self):
        """Test getting cache remaining time."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Get remaining time
        remaining_hours = self.service.get_cache_remaining_time(2024)
        assert remaining_hours is not None
        assert remaining_hours > 0

    def test_get_cache_remaining_time_not_found(self):
        """Test getting remaining time for non-existent cache."""
        remaining_hours = self.service.get_cache_remaining_time(2024)
        assert remaining_hours is None

    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Clear all cache
        count = self.service.clear_all_cache()
        assert isinstance(count, int)
        assert count >= 1

    def test_get_cache_summary(self):
        """Test getting cache summary."""
        # Cache some data
        self.service.cache_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Get cache summary
        summary = self.service.get_cache_summary()
        
        assert "statistics" in summary
        assert "cached_years" in summary
        assert "year_range" in summary
        assert "total_years" in summary
        assert summary["total_years"] >= 1

    def test_cache_data_validation_error(self):
        """Test caching data with validation error."""
        with pytest.raises(TufeCacheError):
            self.service.cache_data(
                year=1900,  # Invalid year
                rate=Decimal("44.38"),
                source="TCMB EVDS API",
                api_response='{"data": "test"}'
            )

    def test_cache_data_negative_rate_error(self):
        """Test caching data with negative rate."""
        with pytest.raises(TufeCacheError):
            self.service.cache_data(
                year=2024,
                rate=Decimal("-10.0"),  # Invalid negative rate
                source="TCMB EVDS API",
                api_response='{"data": "test"}'
            )

    def test_cache_data_empty_source_error(self):
        """Test caching data with empty source."""
        with pytest.raises(TufeCacheError):
            self.service.cache_data(
                year=2024,
                rate=Decimal("44.38"),
                source="",  # Invalid empty source
                api_response='{"data": "test"}'
            )
