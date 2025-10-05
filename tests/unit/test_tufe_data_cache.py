"""
Unit tests for TufeDataCache model.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from src.models.tufe_data_cache import TufeDataCache


class TestTufeDataCache:
    """Unit tests for TufeDataCache model."""

    def test_valid_tufe_data_cache_creation(self):
        """Test creating a valid TufeDataCache."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="TCMB EVDS API",
            api_response='{"data": "test"}',
            is_validated=True
        )
        
        assert cache.year == 2024
        assert cache.tufe_rate == Decimal("44.38")
        assert cache.source_name == "TCMB EVDS API"
        assert cache.api_response == '{"data": "test"}'
        assert cache.is_validated is True
        assert cache.fetched_at is not None
        assert cache.expires_at is not None

    def test_invalid_year_raises_error(self):
        """Test that invalid year raises ValueError."""
        with pytest.raises(ValueError, match="year must be between 2000 and 2100"):
            TufeDataCache(
                year=1900,
                tufe_rate=Decimal("44.38"),
                source_name="Test Source"
            )

    def test_invalid_tufe_rate_raises_error(self):
        """Test that invalid TÜFE rate raises ValueError."""
        with pytest.raises(ValueError, match="tufe_rate must be non-negative"):
            TufeDataCache(
                year=2024,
                tufe_rate=Decimal("-10.0"),
                source_name="Test Source"
            )

    def test_invalid_source_name_raises_error(self):
        """Test that invalid source name raises ValueError."""
        with pytest.raises(ValueError, match="source_name must be a non-empty string"):
            TufeDataCache(
                year=2024,
                tufe_rate=Decimal("44.38"),
                source_name=""
            )

    def test_to_dict_conversion(self):
        """Test converting TufeDataCache to dictionary."""
        cache = TufeDataCache(
            id=1,
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="TCMB EVDS API",
            api_response='{"data": "test"}',
            is_validated=True
        )
        
        data_dict = cache.to_dict()
        
        assert data_dict['id'] == 1
        assert data_dict['year'] == 2024
        assert data_dict['tufe_rate'] == "44.38"
        assert data_dict['source_name'] == "TCMB EVDS API"
        assert data_dict['api_response'] == '{"data": "test"}'
        assert data_dict['is_validated'] is True

    def test_from_dict_creation(self):
        """Test creating TufeDataCache from dictionary."""
        data_dict = {
            'id': 1,
            'year': 2024,
            'tufe_rate': '44.38',
            'source_name': 'TCMB EVDS API',
            'fetched_at': '2024-01-01T12:00:00',
            'expires_at': '2024-01-02T12:00:00',
            'api_response': '{"data": "test"}',
            'is_validated': True,
            'created_at': '2024-01-01T10:00:00'
        }
        
        cache = TufeDataCache.from_dict(data_dict)
        
        assert cache.id == 1
        assert cache.year == 2024
        assert cache.tufe_rate == Decimal("44.38")
        assert cache.source_name == "TCMB EVDS API"
        assert cache.fetched_at == datetime(2024, 1, 1, 12, 0, 0)
        assert cache.expires_at == datetime(2024, 1, 2, 12, 0, 0)
        assert cache.api_response == '{"data": "test"}'
        assert cache.is_validated is True
        assert cache.created_at == datetime(2024, 1, 1, 10, 0, 0)

    def test_is_expired(self):
        """Test checking if cache entry is expired."""
        # Create cache with past expiration
        past_expiry = datetime.now() - timedelta(hours=1)
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source"
        )
        cache.expires_at = past_expiry
        
        assert cache.is_expired() is True
        
        # Create cache with future expiration
        future_expiry = datetime.now() + timedelta(hours=1)
        cache.expires_at = future_expiry
        
        assert cache.is_expired() is False

    def test_is_valid(self):
        """Test checking if cache entry is valid."""
        # Valid cache
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source",
            is_validated=True
        )
        cache.expires_at = datetime.now() + timedelta(hours=1)
        
        assert cache.is_valid() is True
        
        # Expired cache
        cache.expires_at = datetime.now() - timedelta(hours=1)
        assert cache.is_valid() is False
        
        # Unvalidated cache
        cache.expires_at = datetime.now() + timedelta(hours=1)
        cache.is_validated = False
        assert cache.is_valid() is False

    def test_get_age_hours(self):
        """Test getting cache age in hours."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source"
        )
        
        # Set fetched time to 2 hours ago
        cache.fetched_at = datetime.now() - timedelta(hours=2)
        
        age_hours = cache.get_age_hours()
        assert age_hours is not None
        assert 1.9 <= age_hours <= 2.1  # Allow some tolerance

    def test_get_remaining_hours(self):
        """Test getting remaining hours until expiration."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source"
        )
        
        # Set expiration to 3 hours from now
        cache.expires_at = datetime.now() + timedelta(hours=3)
        
        remaining_hours = cache.get_remaining_hours()
        assert remaining_hours is not None
        assert 2.9 <= remaining_hours <= 3.1  # Allow some tolerance
        
        # Set expiration to past
        cache.expires_at = datetime.now() - timedelta(hours=1)
        remaining_hours = cache.get_remaining_hours()
        assert remaining_hours == 0.0

    def test_extend_expiration(self):
        """Test extending cache expiration."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source"
        )
        
        original_expiry = cache.expires_at
        cache.extend_expiration(12)  # Extend by 12 hours
        
        expected_expiry = original_expiry + timedelta(hours=12)
        assert cache.expires_at == expected_expiry

    def test_mark_as_validated(self):
        """Test marking cache as validated."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source",
            is_validated=False
        )
        
        assert cache.is_validated is False
        cache.mark_as_validated()
        assert cache.is_validated is True

    def test_mark_as_invalidated(self):
        """Test marking cache as invalidated."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source",
            is_validated=True
        )
        
        assert cache.is_validated is True
        cache.mark_as_invalidated()
        assert cache.is_validated is False

    def test_get_source_attribution(self):
        """Test getting source attribution string."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="TCMB EVDS API"
        )
        
        attribution = cache.get_source_attribution()
        assert attribution == "Data source: TCMB EVDS API"

    def test_get_data_lineage(self):
        """Test getting data lineage string."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="TCMB EVDS API"
        )
        cache.fetched_at = datetime(2024, 1, 1, 12, 0, 0)
        
        lineage = cache.get_data_lineage()
        assert "TÜFE data for 2024" in lineage
        assert "44.38%" in lineage
        assert "TCMB EVDS API" in lineage
        assert "fetched: 2024-01-01 12:00" in lineage

    def test_get_cache_status(self):
        """Test getting cache status string."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source"
        )
        
        # Valid cache
        cache.is_validated = True
        cache.expires_at = datetime.now() + timedelta(hours=1)
        assert cache.get_cache_status() == "Valid"
        
        # Expired cache
        cache.expires_at = datetime.now() - timedelta(hours=1)
        assert cache.get_cache_status() == "Expired"
        
        # Unvalidated cache
        cache.expires_at = datetime.now() + timedelta(hours=1)
        cache.is_validated = False
        assert cache.get_cache_status() == "Unvalidated"

    def test_get_remaining_time_str(self):
        """Test getting human-readable remaining time string."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="Test Source"
        )
        
        # Expired
        cache.expires_at = datetime.now() - timedelta(hours=1)
        assert cache.get_remaining_time_str() == "Expired"
        
        # Less than 1 hour
        cache.expires_at = datetime.now() + timedelta(minutes=30)
        remaining = cache.get_remaining_time_str()
        assert "minutes" in remaining
        
        # Less than 24 hours
        cache.expires_at = datetime.now() + timedelta(hours=5)
        remaining = cache.get_remaining_time_str()
        assert "hours" in remaining
        
        # More than 24 hours
        cache.expires_at = datetime.now() + timedelta(days=3)
        remaining = cache.get_remaining_time_str()
        assert "days" in remaining

    def test_string_representation(self):
        """Test string representation of TufeDataCache."""
        cache = TufeDataCache(
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="TCMB EVDS API",
            is_validated=True
        )
        
        str_repr = str(cache)
        assert "TufeDataCache" in str_repr
        assert "2024" in str_repr
        assert "44.38%" in str_repr
        assert "TCMB EVDS API" in str_repr
        assert "Valid" in str_repr

    def test_repr_representation(self):
        """Test detailed string representation of TufeDataCache."""
        cache = TufeDataCache(
            id=1,
            year=2024,
            tufe_rate=Decimal("44.38"),
            source_name="TCMB EVDS API",
            api_response='{"data": "test"}',
            is_validated=True
        )
        
        repr_str = repr(cache)
        assert "TufeDataCache" in repr_str
        assert "id=1" in repr_str
        assert "year=2024" in repr_str
        assert "tufe_rate=44.38" in repr_str
        assert "source_name='TCMB EVDS API'" in repr_str
        assert "is_validated=True" in repr_str
        # API response should be truncated
        assert '{"data": "test"}...' in repr_str
