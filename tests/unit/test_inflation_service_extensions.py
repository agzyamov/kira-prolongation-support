"""
Unit tests for extended InflationService methods.
"""

import pytest
import tempfile
import os
from decimal import Decimal
from src.services.inflation_service import InflationService
from src.storage import DataStore
from src.services.exceptions import TufeApiError, TufeValidationError


class TestInflationServiceExtensions:
    """Unit tests for extended InflationService methods."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.data_store = DataStore(self.db_path)
        self.service = InflationService(self.data_store)

    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_fetch_tufe_from_tcmb_api_no_api_key(self):
        """Test fetching TÜFE from TCMB API without API key."""
        with pytest.raises(TufeValidationError, match="API key is required"):
            self.service.fetch_tufe_from_tcmb_api(2024, "")

    def test_fetch_tufe_from_tcmb_api_invalid_year(self):
        """Test fetching TÜFE from TCMB API with invalid year."""
        with pytest.raises(TufeValidationError, match="Invalid year"):
            self.service.fetch_tufe_from_tcmb_api(1900, "test_key")

    def test_fetch_tufe_from_tcmb_api_invalid_year_high(self):
        """Test fetching TÜFE from TCMB API with year too high."""
        with pytest.raises(TufeValidationError, match="Invalid year"):
            self.service.fetch_tufe_from_tcmb_api(2101, "test_key")

    def test_fetch_tufe_from_tcmb_api_network_error(self):
        """Test fetching TÜFE from TCMB API with network error."""
        with pytest.raises(TufeApiError):
            self.service.fetch_tufe_from_tcmb_api(2024, "test_key")

    def test_get_tufe_data_sources(self):
        """Test getting TÜFE data sources."""
        sources = self.service.get_tufe_data_sources()
        assert isinstance(sources, list)

    def test_get_active_tufe_source(self):
        """Test getting active TÜFE source."""
        source = self.service.get_active_tufe_source()
        # Should return None or a valid source
        assert source is None or hasattr(source, 'source_name')

    def test_cache_tufe_data_success(self):
        """Test caching TÜFE data successfully."""
        cache_id = self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        assert isinstance(cache_id, int)
        assert cache_id > 0

    def test_cache_tufe_data_invalid_year(self):
        """Test caching TÜFE data with invalid year."""
        with pytest.raises(TufeApiError):
            self.service.cache_tufe_data(
                year=1900,  # Invalid year
                rate=Decimal("44.38"),
                source="TCMB EVDS API",
                api_response='{"data": "test"}'
            )

    def test_cache_tufe_data_negative_rate(self):
        """Test caching TÜFE data with negative rate."""
        with pytest.raises(TufeApiError):
            self.service.cache_tufe_data(
                year=2024,
                rate=Decimal("-10.0"),  # Invalid negative rate
                source="TCMB EVDS API",
                api_response='{"data": "test"}'
            )

    def test_cache_tufe_data_empty_source(self):
        """Test caching TÜFE data with empty source."""
        with pytest.raises(TufeApiError):
            self.service.cache_tufe_data(
                year=2024,
                rate=Decimal("44.38"),
                source="",  # Invalid empty source
                api_response='{"data": "test"}'
            )

    def test_get_cached_tufe_data_success(self):
        """Test getting cached TÜFE data successfully."""
        # Cache some data first
        self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Get cached data
        cached_data = self.service.get_cached_tufe_data(2024)
        assert cached_data is not None
        assert cached_data.year == 2024
        assert cached_data.tufe_rate == Decimal("44.38")

    def test_get_cached_tufe_data_not_found(self):
        """Test getting cached TÜFE data when none exists."""
        cached_data = self.service.get_cached_tufe_data(2024)
        assert cached_data is None

    def test_is_tufe_cache_valid_true(self):
        """Test checking TÜFE cache validity when valid."""
        # Cache some data
        self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "test"}'
        )
        
        # Check cache validity
        is_valid = self.service.is_tufe_cache_valid(2024)
        assert is_valid is True

    def test_is_tufe_cache_valid_false(self):
        """Test checking TÜFE cache validity when invalid."""
        # Check for non-existent cache
        is_valid = self.service.is_tufe_cache_valid(2024)
        assert is_valid is False

    def test_fetch_tufe_from_tcmb_api_integration(self):
        """Test TCMB API integration (will fail due to network call)."""
        # This test will fail in unit test environment due to network call
        # but we can test the method structure
        with pytest.raises(TufeApiError):
            self.service.fetch_tufe_from_tcmb_api(2024, "test_api_key")

    def test_cache_tufe_data_with_different_sources(self):
        """Test caching TÜFE data from different sources."""
        # Cache data from TCMB
        tcmb_cache_id = self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "tcmb"}'
        )
        
        # Cache data from manual entry
        manual_cache_id = self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("45.00"),
            source="Manual Entry",
            api_response='{"data": "manual"}'
        )
        
        assert tcmb_cache_id != manual_cache_id
        assert tcmb_cache_id > 0
        assert manual_cache_id > 0

    def test_get_cached_tufe_data_latest(self):
        """Test getting the latest cached TÜFE data."""
        # Cache data for the same year from different sources
        self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response='{"data": "tcmb"}'
        )
        
        self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("45.00"),
            source="Manual Entry",
            api_response='{"data": "manual"}'
        )
        
        # Get cached data (should return the latest)
        cached_data = self.service.get_cached_tufe_data(2024)
        assert cached_data is not None
        assert cached_data.year == 2024

    def test_cache_tufe_data_with_large_response(self):
        """Test caching TÜFE data with large API response."""
        large_response = '{"data": "' + "x" * 1000 + '"}'
        
        cache_id = self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API",
            api_response=large_response
        )
        
        assert cache_id > 0
        
        # Verify the data was cached
        cached_data = self.service.get_cached_tufe_data(2024)
        assert cached_data is not None
        assert len(cached_data.api_response) == len(large_response)

    def test_cache_tufe_data_with_special_characters(self):
        """Test caching TÜFE data with special characters in source."""
        cache_id = self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TCMB EVDS API v2.0",
            api_response='{"data": "test"}'
        )
        
        assert cache_id > 0
        
        # Verify the data was cached
        cached_data = self.service.get_cached_tufe_data(2024)
        assert cached_data is not None
        assert cached_data.source_name == "TCMB EVDS API v2.0"

    def test_cache_tufe_data_with_unicode_source(self):
        """Test caching TÜFE data with Unicode characters in source."""
        cache_id = self.service.cache_tufe_data(
            year=2024,
            rate=Decimal("44.38"),
            source="TÜFE Veri Kaynağı",
            api_response='{"data": "test"}'
        )
        
        assert cache_id > 0
        
        # Verify the data was cached
        cached_data = self.service.get_cached_tufe_data(2024)
        assert cached_data is not None
        assert cached_data.source_name == "TÜFE Veri Kaynağı"
