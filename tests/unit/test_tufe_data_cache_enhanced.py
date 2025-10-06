"""
Unit tests for enhanced TufeDataCache model.

Tests the enhanced TufeDataCache with TTL support, cache statistics,
and enhanced caching functionality.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.models.tufe_data_cache import TufeDataCache


class TestTufeDataCacheEnhanced:
    """Unit tests for enhanced TufeDataCache."""
    
    def test_initialization_default_values(self):
        """Test TufeDataCache initialization with default values."""
        cache = TufeDataCache()
        
        assert cache.id is None
        assert cache.year == 0
        assert cache.month == 1
        assert cache.tufe_rate == Decimal("0.00")
        assert cache.source_name == ""
        assert cache.fetched_at is not None  # Should be set to current time
        assert cache.expires_at is not None  # Should be set to fetched_at + 24 hours
        assert cache.api_response == ""
        assert cache.is_validated is False
        assert cache.created_at is None
        
        # Enhanced TTL fields
        assert cache.fetch_duration is None
        assert cache.retry_count == 0
        assert cache.cache_hit_count == 0
        assert cache.last_accessed is None
    
    def test_initialization_custom_values(self):
        """Test TufeDataCache initialization with custom values."""
        now = datetime.now()
        expires_at = now + timedelta(hours=24)
        last_accessed = now - timedelta(minutes=30)
        
        cache = TufeDataCache(
            id=1,
            year=2020,
            month=6,
            tufe_rate=Decimal("10.5"),
            source_name="OECD SDMX API",
            fetched_at=now,
            expires_at=expires_at,
            api_response='{"data": "test"}',
            is_validated=True,
            created_at=now,
            fetch_duration=1.5,
            retry_count=2,
            cache_hit_count=5,
            last_accessed=last_accessed
        )
        
        assert cache.id == 1
        assert cache.year == 2020
        assert cache.month == 6
        assert cache.tufe_rate == Decimal("10.5")
        assert cache.source_name == "OECD SDMX API"
        assert cache.fetched_at == now
        assert cache.expires_at == expires_at
        assert cache.api_response == '{"data": "test"}'
        assert cache.is_validated is True
        assert cache.created_at == now
        assert cache.fetch_duration == 1.5
        assert cache.retry_count == 2
        assert cache.cache_hit_count == 5
        assert cache.last_accessed == last_accessed
    
    def test_validation_year_range(self):
        """Test validation requires year in range 2000-2100."""
        # Valid years
        TufeDataCache(year=2000)
        TufeDataCache(year=2020)
        TufeDataCache(year=2100)
        
        # Invalid years
        with pytest.raises(ValueError, match="year must be between 2000 and 2100"):
            TufeDataCache(year=1999)
        
        with pytest.raises(ValueError, match="year must be between 2000 and 2100"):
            TufeDataCache(year=2101)
    
    def test_validation_month_range(self):
        """Test validation requires month in range 1-12."""
        # Valid months
        TufeDataCache(year=2020, month=1)
        TufeDataCache(year=2020, month=6)
        TufeDataCache(year=2020, month=12)
        
        # Invalid months
        with pytest.raises(ValueError, match="month must be between 1 and 12"):
            TufeDataCache(year=2020, month=0)
        
        with pytest.raises(ValueError, match="month must be between 1 and 12"):
            TufeDataCache(year=2020, month=13)
    
    def test_validation_tufe_rate_non_negative(self):
        """Test validation requires non-negative tufe_rate."""
        # Valid rates
        TufeDataCache(year=2020, tufe_rate=Decimal("0.0"))
        TufeDataCache(year=2020, tufe_rate=Decimal("10.5"))
        TufeDataCache(year=2020, tufe_rate=Decimal("100.0"))
        
        # Invalid rate
        with pytest.raises(ValueError, match="tufe_rate must be non-negative"):
            TufeDataCache(year=2020, tufe_rate=Decimal("-1.0"))
    
    def test_validation_source_name_required(self):
        """Test validation requires non-empty source_name."""
        with pytest.raises(ValueError, match="source_name must be a non-empty string"):
            TufeDataCache(year=2020, source_name="")
    
    def test_validation_is_validated_boolean(self):
        """Test validation requires boolean is_validated."""
        with pytest.raises(ValueError, match="is_validated must be a boolean"):
            TufeDataCache(year=2020, is_validated="yes")
    
    def test_validation_fetch_duration_non_negative(self):
        """Test validation requires non-negative fetch_duration."""
        # Valid durations
        TufeDataCache(year=2020, fetch_duration=0.0)
        TufeDataCache(year=2020, fetch_duration=1.5)
        TufeDataCache(year=2020, fetch_duration=None)
        
        # Invalid duration
        with pytest.raises(ValueError, match="fetch_duration must be non-negative"):
            TufeDataCache(year=2020, fetch_duration=-1.0)
    
    def test_validation_retry_count_non_negative(self):
        """Test validation requires non-negative retry_count."""
        # Valid counts
        TufeDataCache(year=2020, retry_count=0)
        TufeDataCache(year=2020, retry_count=5)
        
        # Invalid count
        with pytest.raises(ValueError, match="retry_count must be non-negative"):
            TufeDataCache(year=2020, retry_count=-1)
    
    def test_validation_cache_hit_count_non_negative(self):
        """Test validation requires non-negative cache_hit_count."""
        # Valid counts
        TufeDataCache(year=2020, cache_hit_count=0)
        TufeDataCache(year=2020, cache_hit_count=10)
        
        # Invalid count
        with pytest.raises(ValueError, match="cache_hit_count must be non-negative"):
            TufeDataCache(year=2020, cache_hit_count=-1)
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        now = datetime.now()
        expires_at = now + timedelta(hours=24)
        last_accessed = now - timedelta(minutes=30)
        
        cache = TufeDataCache(
            id=1,
            year=2020,
            month=6,
            tufe_rate=Decimal("10.5"),
            source_name="OECD SDMX API",
            fetched_at=now,
            expires_at=expires_at,
            api_response='{"data": "test"}',
            is_validated=True,
            created_at=now,
            fetch_duration=1.5,
            retry_count=2,
            cache_hit_count=5,
            last_accessed=last_accessed
        )
        
        result = cache.to_dict()
        
        assert result['id'] == 1
        assert result['year'] == 2020
        assert result['month'] == 6
        assert result['tufe_rate'] == 10.5
        assert result['source_name'] == "OECD SDMX API"
        assert result['fetched_at'] == now.isoformat()
        assert result['expires_at'] == expires_at.isoformat()
        assert result['api_response'] == '{"data": "test"}'
        assert result['is_validated'] is True
        assert result['created_at'] == now.isoformat()
        assert result['fetch_duration'] == 1.5
        assert result['retry_count'] == 2
        assert result['cache_hit_count'] == 5
        assert result['last_accessed'] == last_accessed.isoformat()
    
    def test_from_dict_conversion(self):
        """Test conversion from dictionary."""
        now = datetime.now()
        expires_at = now + timedelta(hours=24)
        last_accessed = now - timedelta(minutes=30)
        
        data = {
            'id': 1,
            'year': 2020,
            'month': 6,
            'tufe_rate': 10.5,
            'source_name': "OECD SDMX API",
            'fetched_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'api_response': '{"data": "test"}',
            'is_validated': True,
            'created_at': now.isoformat(),
            'fetch_duration': 1.5,
            'retry_count': 2,
            'cache_hit_count': 5,
            'last_accessed': last_accessed.isoformat()
        }
        
        cache = TufeDataCache.from_dict(data)
        
        assert cache.id == 1
        assert cache.year == 2020
        assert cache.month == 6
        assert cache.tufe_rate == Decimal("10.5")
        assert cache.source_name == "OECD SDMX API"
        assert cache.fetched_at == now
        assert cache.expires_at == expires_at
        assert cache.api_response == '{"data": "test"}'
        assert cache.is_validated is True
        assert cache.created_at == now
        assert cache.fetch_duration == 1.5
        assert cache.retry_count == 2
        assert cache.cache_hit_count == 5
        assert cache.last_accessed == last_accessed
    
    def test_from_dict_with_none_values(self):
        """Test conversion from dictionary with None values."""
        data = {
            'id': 1,
            'year': 2020,
            'month': 6,
            'tufe_rate': 10.5,
            'source_name': "OECD SDMX API",
            'fetched_at': None,
            'expires_at': None,
            'api_response': '{"data": "test"}',
            'is_validated': True,
            'created_at': None,
            'fetch_duration': None,
            'retry_count': 0,
            'cache_hit_count': 0,
            'last_accessed': None
        }
        
        cache = TufeDataCache.from_dict(data)
        
        assert cache.id == 1
        assert cache.year == 2020
        assert cache.month == 6
        assert cache.tufe_rate == Decimal("10.5")
        assert cache.source_name == "OECD SDMX API"
        assert cache.fetched_at is None
        assert cache.expires_at is None
        assert cache.api_response == '{"data": "test"}'
        assert cache.is_validated is True
        assert cache.created_at is None
        assert cache.fetch_duration is None
        assert cache.retry_count == 0
        assert cache.cache_hit_count == 0
        assert cache.last_accessed is None
    
    def test_is_expired_not_expired(self):
        """Test is_expired returns False for non-expired cache."""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        assert cache.is_expired() is False
    
    def test_is_expired_expired(self):
        """Test is_expired returns True for expired cache."""
        now = datetime.now()
        expires_at = now - timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        assert cache.is_expired() is True
    
    def test_is_expired_no_expiration(self):
        """Test is_expired returns False when no expiration set."""
        cache = TufeDataCache(
            year=2020,
            expires_at=None
        )
        
        assert cache.is_expired() is False
    
    def test_is_valid_not_expired_and_validated(self):
        """Test is_valid returns True for non-expired and validated cache."""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at,
            is_validated=True
        )
        
        assert cache.is_valid() is True
    
    def test_is_valid_expired(self):
        """Test is_valid returns False for expired cache."""
        now = datetime.now()
        expires_at = now - timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at,
            is_validated=True
        )
        
        assert cache.is_valid() is False
    
    def test_is_valid_not_validated(self):
        """Test is_valid returns False for non-validated cache."""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at,
            is_validated=False
        )
        
        assert cache.is_valid() is False
    
    def test_get_age_hours(self):
        """Test get_age_hours returns correct age in hours."""
        now = datetime.now()
        fetched_at = now - timedelta(hours=2, minutes=30)  # 2.5 hours ago
        
        cache = TufeDataCache(
            year=2020,
            fetched_at=fetched_at
        )
        
        age = cache.get_age_hours()
        assert 2.4 <= age <= 2.6  # Allow for small time differences
    
    def test_get_age_hours_no_fetch_time(self):
        """Test get_age_hours returns 0 when no fetch time."""
        cache = TufeDataCache(
            year=2020,
            fetched_at=None
        )
        
        assert cache.get_age_hours() == 0.0
    
    def test_get_remaining_hours(self):
        """Test get_remaining_hours returns correct remaining time."""
        now = datetime.now()
        expires_at = now + timedelta(hours=2, minutes=30)  # 2.5 hours from now
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        remaining = cache.get_remaining_hours()
        assert 2.4 <= remaining <= 2.6  # Allow for small time differences
    
    def test_get_remaining_hours_expired(self):
        """Test get_remaining_hours returns 0 for expired cache."""
        now = datetime.now()
        expires_at = now - timedelta(hours=1)  # 1 hour ago
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        assert cache.get_remaining_hours() == 0.0
    
    def test_get_remaining_hours_no_expiration(self):
        """Test get_remaining_hours returns 0 when no expiration set."""
        cache = TufeDataCache(
            year=2020,
            expires_at=None
        )
        
        assert cache.get_remaining_hours() == 0.0
    
    def test_extend_expiration(self):
        """Test extend_expiration extends expiration time."""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        cache.extend_expiration(24)  # Extend by 24 hours
        
        expected_expires_at = expires_at + timedelta(hours=24)
        assert cache.expires_at == expected_expires_at
    
    def test_extend_expiration_no_initial_expiration(self):
        """Test extend_expiration sets expiration when none exists."""
        cache = TufeDataCache(
            year=2020,
            expires_at=None
        )
        
        cache.extend_expiration(24)  # Set to 24 hours from now
        
        assert cache.expires_at is not None
        # Should be approximately 24 hours from now
        remaining = cache.get_remaining_hours()
        assert 23.9 <= remaining <= 24.1
    
    def test_mark_as_validated(self):
        """Test mark_as_validated sets is_validated to True."""
        cache = TufeDataCache(
            year=2020,
            is_validated=False
        )
        
        cache.mark_as_validated()
        
        assert cache.is_validated is True
    
    def test_mark_as_invalidated(self):
        """Test mark_as_invalidated sets is_validated to False."""
        cache = TufeDataCache(
            year=2020,
            is_validated=True
        )
        
        cache.mark_as_invalidated()
        
        assert cache.is_validated is False
    
    def test_get_source_attribution(self):
        """Test get_source_attribution returns formatted string."""
        cache = TufeDataCache(
            year=2020,
            source_name="OECD SDMX API"
        )
        
        attribution = cache.get_source_attribution()
        
        assert attribution == "Data source: OECD SDMX API"
    
    def test_is_ttl_expired(self):
        """Test is_ttl_expired is an alias for is_expired."""
        now = datetime.now()
        expires_at = now - timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        assert cache.is_ttl_expired() is True
        assert cache.is_ttl_expired() == cache.is_expired()
    
    def test_get_ttl_remaining(self):
        """Test get_ttl_remaining returns remaining time as timedelta."""
        now = datetime.now()
        expires_at = now + timedelta(hours=2, minutes=30)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        remaining = cache.get_ttl_remaining()
        
        assert isinstance(remaining, timedelta)
        assert remaining.total_seconds() > 0
        assert remaining.total_seconds() < 3 * 3600  # Less than 3 hours
    
    def test_get_ttl_remaining_expired(self):
        """Test get_ttl_remaining returns zero timedelta for expired cache."""
        now = datetime.now()
        expires_at = now - timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        remaining = cache.get_ttl_remaining()
        
        assert isinstance(remaining, timedelta)
        assert remaining.total_seconds() == 0
    
    def test_extend_ttl(self):
        """Test extend_ttl is an alias for extend_expiration."""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            expires_at=expires_at
        )
        
        cache.extend_ttl(24)  # Extend by 24 hours
        
        expected_expires_at = expires_at + timedelta(hours=24)
        assert cache.expires_at == expected_expires_at
    
    def test_mark_accessed(self):
        """Test mark_accessed updates access tracking."""
        cache = TufeDataCache(
            year=2020,
            cache_hit_count=5
        )
        
        cache.mark_accessed()
        
        assert cache.cache_hit_count == 6
        assert cache.last_accessed is not None
        assert isinstance(cache.last_accessed, datetime)
    
    def test_get_cache_efficiency(self):
        """Test get_cache_efficiency calculates efficiency score."""
        now = datetime.now()
        fetched_at = now - timedelta(hours=2)  # 2 hours ago
        
        cache = TufeDataCache(
            year=2020,
            fetched_at=fetched_at,
            cache_hit_count=10
        )
        
        efficiency = cache.get_cache_efficiency()
        
        # Should be 10 hits / 2 hours = 5 hits per hour
        assert 4.9 <= efficiency <= 5.1
    
    def test_get_cache_efficiency_no_fetch_time(self):
        """Test get_cache_efficiency returns 0 when no fetch time."""
        cache = TufeDataCache(
            year=2020,
            fetched_at=None,
            cache_hit_count=10
        )
        
        assert cache.get_cache_efficiency() == 0.0
    
    def test_get_cache_efficiency_no_hits(self):
        """Test get_cache_efficiency returns 0 when no hits."""
        now = datetime.now()
        fetched_at = now - timedelta(hours=2)
        
        cache = TufeDataCache(
            year=2020,
            fetched_at=fetched_at,
            cache_hit_count=0
        )
        
        assert cache.get_cache_efficiency() == 0.0
    
    def test_get_data_lineage(self):
        """Test get_data_lineage returns formatted lineage string."""
        now = datetime.now()
        fetched_at = now - timedelta(hours=1)
        
        cache = TufeDataCache(
            year=2020,
            month=6,
            tufe_rate=Decimal("10.5"),
            source_name="OECD SDMX API",
            fetched_at=fetched_at
        )
        
        lineage = cache.get_data_lineage()
        
        assert "TÜFE data for 2020: 10.5% from OECD SDMX API" in lineage
        assert "fetched:" in lineage
        assert fetched_at.strftime("%Y-%m-%d %H:%M") in lineage
    
    def test_get_data_lineage_no_fetch_time(self):
        """Test get_data_lineage handles missing fetch time."""
        cache = TufeDataCache(
            year=2020,
            month=6,
            tufe_rate=Decimal("10.5"),
            source_name="OECD SDMX API",
            fetched_at=None
        )
        
        lineage = cache.get_data_lineage()
        
        assert "TÜFE data for 2020: 10.5% from OECD SDMX API" in lineage
        assert "fetched: Unknown" in lineage
    
    def test_complete_oecd_cache_entry(self):
        """Test creating a complete OECD cache entry with all fields."""
        now = datetime.now()
        expires_at = now + timedelta(hours=168)  # 7 days
        last_accessed = now - timedelta(minutes=15)
        
        cache = TufeDataCache(
            id=1,
            year=2020,
            month=6,
            tufe_rate=Decimal("10.5"),
            source_name="OECD SDMX API",
            fetched_at=now,
            expires_at=expires_at,
            api_response='{"items": [{"year": 2020, "month": 6, "value": 10.5}]}',
            is_validated=True,
            created_at=now,
            fetch_duration=1.2,
            retry_count=0,
            cache_hit_count=3,
            last_accessed=last_accessed
        )
        
        # Verify all fields
        assert cache.id == 1
        assert cache.year == 2020
        assert cache.month == 6
        assert cache.tufe_rate == Decimal("10.5")
        assert cache.source_name == "OECD SDMX API"
        assert cache.fetched_at == now
        assert cache.expires_at == expires_at
        assert cache.api_response == '{"items": [{"year": 2020, "month": 6, "value": 10.5}]}'
        assert cache.is_validated is True
        assert cache.created_at == now
        assert cache.fetch_duration == 1.2
        assert cache.retry_count == 0
        assert cache.cache_hit_count == 3
        assert cache.last_accessed == last_accessed
        
        # Test methods
        assert cache.is_expired() is False
        assert cache.is_valid() is True
        assert cache.get_remaining_hours() > 0
        assert cache.get_cache_efficiency() > 0
        assert "OECD SDMX API" in cache.get_source_attribution()
        assert "2020" in cache.get_data_lineage()


if __name__ == "__main__":
    pytest.main([__file__])
