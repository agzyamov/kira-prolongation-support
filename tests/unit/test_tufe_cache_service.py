"""
Unit tests for TufeCacheService.

Tests caching functionality including TTL support, cache validation,
cache statistics, and cache management operations.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from decimal import Decimal

from src.services.tufe_cache_service import TufeCacheService
from src.services.exceptions import TufeCacheError, TufeValidationError
from src.models.tufe_data_cache import TufeDataCache
from src.models.inflation_data import InflationData


class TestTufeCacheService:
    """Unit tests for TufeCacheService."""
    
    def test_initialization(self):
        """Test TufeCacheService initialization."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        assert service.data_store == mock_data_store
    
    def test_cache_oecd_data_valid(self):
        """Test cache_oecd_data with valid data."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        inflation_data = [
            InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API"),
            InflationData(year=2020, month=2, tufe_rate=Decimal("11.0"), source="OECD SDMX API")
        ]
        
        result = service.cache_oecd_data(inflation_data, ttl_hours=24)
        
        assert result == 2
        assert mock_data_store.save_tufe_data_cache.call_count == 2
    
    def test_cache_oecd_data_empty_list(self):
        """Test cache_oecd_data with empty list."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        with pytest.raises(TufeCacheError, match="No data to cache"):
            service.cache_oecd_data([])
    
    def test_cache_oecd_data_invalid_type(self):
        """Test cache_oecd_data with invalid data type."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        with pytest.raises(TufeCacheError, match="Data must be a list"):
            service.cache_oecd_data("invalid")
    
    def test_cache_oecd_data_invalid_item_type(self):
        """Test cache_oecd_data with invalid item type."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        invalid_data = [{"year": 2020, "month": 1, "value": 10.5}]
        
        with pytest.raises(TufeValidationError, match="Item must be an InflationData object"):
            service.cache_oecd_data(invalid_data)
    
    def test_cache_oecd_data_invalid_year(self):
        """Test cache_oecd_data with invalid year."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        invalid_data = [InflationData(year=1999, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")]
        
        with pytest.raises(TufeValidationError, match="Invalid year: 1999"):
            service.cache_oecd_data(invalid_data)
    
    def test_cache_oecd_data_invalid_month(self):
        """Test cache_oecd_data with invalid month."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        invalid_data = [InflationData(year=2020, month=13, tufe_rate=Decimal("10.5"), source="OECD SDMX API")]
        
        with pytest.raises(TufeValidationError, match="Invalid month: 13"):
            service.cache_oecd_data(invalid_data)
    
    def test_cache_oecd_data_invalid_tufe_rate(self):
        """Test cache_oecd_data with invalid TÜFE rate."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        invalid_data = [InflationData(year=2020, month=1, tufe_rate=Decimal("-1.0"), source="OECD SDMX API")]
        
        with pytest.raises(TufeValidationError, match="Invalid TÜFE rate: -1.0"):
            service.cache_oecd_data(invalid_data)
    
    def test_cache_oecd_data_default_ttl(self):
        """Test cache_oecd_data with default TTL."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        inflation_data = [InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")]
        
        with patch('src.services.tufe_cache_service.CACHE_CONFIG', {
            "recent_data_ttl_hours": 24,
            "historical_data_ttl_hours": 168
        }):
            result = service.cache_oecd_data(inflation_data)
        
        assert result == 1
        mock_data_store.save_tufe_data_cache.assert_called_once()
    
    def test_cache_oecd_data_custom_ttl(self):
        """Test cache_oecd_data with custom TTL."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        inflation_data = [InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")]
        
        result = service.cache_oecd_data(inflation_data, ttl_hours=48)
        
        assert result == 1
        mock_data_store.save_tufe_data_cache.assert_called_once()
    
    def test_get_cached_oecd_data_found(self):
        """Test get_cached_oecd_data when data is found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = False
        mock_cache_entry.year = 2020
        mock_cache_entry.month = 1
        mock_cache_entry.tufe_rate = Decimal("10.5")
        mock_cache_entry.source_name = "OECD SDMX API"
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.get_cached_oecd_data(2020, 1)
        
        assert result is not None
        assert result.year == 2020
        assert result.month == 1
        assert result.tufe_rate == Decimal("10.5")
        assert result.source == "OECD SDMX API"
    
    def test_get_cached_oecd_data_not_found(self):
        """Test get_cached_oecd_data when data is not found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = None
        
        result = service.get_cached_oecd_data(2020, 1)
        
        assert result is None
    
    def test_get_cached_oecd_data_expired(self):
        """Test get_cached_oecd_data when data is expired."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock expired cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = True
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.get_cached_oecd_data(2020, 1)
        
        assert result is None
    
    def test_get_cached_oecd_data_without_month(self):
        """Test get_cached_oecd_data without specifying month."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = False
        mock_cache_entry.year = 2020
        mock_cache_entry.month = 1
        mock_cache_entry.tufe_rate = Decimal("10.5")
        mock_cache_entry.source_name = "OECD SDMX API"
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.get_cached_oecd_data(2020)
        
        assert result is not None
        assert result.year == 2020
        assert result.month == 1
    
    def test_get_cached_data_by_year_month_found(self):
        """Test get_cached_data_by_year_month when data is found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.get_cached_data_by_year_month(2020, 1)
        
        assert result == mock_cache_entry
        mock_data_store.get_tufe_data_cache_by_year_month.assert_called_once_with(2020, 1)
    
    def test_get_cached_data_by_year_month_not_found(self):
        """Test get_cached_data_by_year_month when data is not found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = None
        
        result = service.get_cached_data_by_year_month(2020, 1)
        
        assert result is None
    
    def test_get_cached_data_by_year_month_without_month(self):
        """Test get_cached_data_by_year_month without specifying month."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.get_cached_data_by_year_month(2020)
        
        assert result == mock_cache_entry
        mock_data_store.get_tufe_data_cache_by_year_month.assert_called_once_with(2020, 1)
    
    def test_cleanup_expired_cache(self):
        """Test cleanup_expired_cache."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entries
        mock_entry1 = Mock()
        mock_entry1.is_expired.return_value = True
        mock_entry1.id = 1
        
        mock_entry2 = Mock()
        mock_entry2.is_expired.return_value = False
        mock_entry2.id = 2
        
        mock_data_store.get_all_tufe_data_cache.return_value = [mock_entry1, mock_entry2]
        mock_data_store._row_to_tufe_data_cache.side_effect = [mock_entry1, mock_entry2]
        
        result = service.cleanup_expired_cache()
        
        assert result == 1
        mock_data_store.delete_tufe_data_cache.assert_called_once_with(1)
    
    def test_cleanup_expired_cache_no_expired(self):
        """Test cleanup_expired_cache with no expired entries."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entries
        mock_entry1 = Mock()
        mock_entry1.is_expired.return_value = False
        mock_entry1.id = 1
        
        mock_entry2 = Mock()
        mock_entry2.is_expired.return_value = False
        mock_entry2.id = 2
        
        mock_data_store.get_all_tufe_data_cache.return_value = [mock_entry1, mock_entry2]
        mock_data_store._row_to_tufe_data_cache.side_effect = [mock_entry1, mock_entry2]
        
        result = service.cleanup_expired_cache()
        
        assert result == 0
        mock_data_store.delete_tufe_data_cache.assert_not_called()
    
    def test_get_cache_statistics(self):
        """Test get_cache_statistics."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entries
        mock_entry1 = Mock()
        mock_entry1.is_expired.return_value = True
        mock_entry1.cache_hit_count = 5
        mock_entry1.fetch_duration = 1.5
        
        mock_entry2 = Mock()
        mock_entry2.is_expired.return_value = False
        mock_entry2.cache_hit_count = 10
        mock_entry2.fetch_duration = 2.0
        
        mock_data_store.get_all_tufe_data_cache.return_value = [mock_entry1, mock_entry2]
        mock_data_store._row_to_tufe_data_cache.side_effect = [mock_entry1, mock_entry2]
        
        result = service.get_cache_statistics()
        
        assert result['total_entries'] == 2
        assert result['expired_entries'] == 1
        assert result['active_entries'] == 1
        assert result['total_hits'] == 15
        assert result['hit_rate'] == 7.5
        assert result['avg_fetch_duration'] == 1.75
    
    def test_get_cache_statistics_empty(self):
        """Test get_cache_statistics with empty cache."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_all_tufe_data_cache.return_value = []
        
        result = service.get_cache_statistics()
        
        assert result['total_entries'] == 0
        assert result['expired_entries'] == 0
        assert result['active_entries'] == 0
        assert result['total_hits'] == 0
        assert result['hit_rate'] == 0.0
        assert result['avg_fetch_duration'] == 0.0
    
    def test_calculate_cache_efficiency(self):
        """Test _calculate_cache_efficiency."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entries
        mock_entry1 = Mock()
        mock_entry1.get_cache_efficiency.return_value = 0.8
        
        mock_entry2 = Mock()
        mock_entry2.get_cache_efficiency.return_value = 0.6
        
        mock_data_store._row_to_tufe_data_cache.side_effect = [mock_entry1, mock_entry2]
        
        result = service._calculate_cache_efficiency([mock_entry1, mock_entry2])
        
        assert result == 0.7  # (0.8 + 0.6) / 2
    
    def test_calculate_cache_efficiency_empty(self):
        """Test _calculate_cache_efficiency with empty entries."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        result = service._calculate_cache_efficiency([])
        
        assert result == 0.0
    
    def test_calculate_cache_efficiency_with_errors(self):
        """Test _calculate_cache_efficiency with some entries causing errors."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entries
        mock_entry1 = Mock()
        mock_entry1.get_cache_efficiency.return_value = 0.8
        
        mock_entry2 = Mock()
        mock_entry2.get_cache_efficiency.side_effect = Exception("Error")
        
        mock_data_store._row_to_tufe_data_cache.side_effect = [mock_entry1, mock_entry2]
        
        result = service._calculate_cache_efficiency([mock_entry1, mock_entry2])
        
        assert result == 0.8  # Only valid entry
    
    def test_is_cache_valid_found_and_valid(self):
        """Test is_cache_valid when data is found and valid."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = False
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.is_cache_valid(2020, 1)
        
        assert result is True
    
    def test_is_cache_valid_found_but_expired(self):
        """Test is_cache_valid when data is found but expired."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = True
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.is_cache_valid(2020, 1)
        
        assert result is False
    
    def test_is_cache_valid_not_found(self):
        """Test is_cache_valid when data is not found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = None
        
        result = service.is_cache_valid(2020, 1)
        
        assert result is False
    
    def test_is_cache_valid_with_error(self):
        """Test is_cache_valid when an error occurs."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.side_effect = Exception("Database error")
        
        result = service.is_cache_valid(2020, 1)
        
        assert result is False
    
    def test_extend_cache_ttl_found_and_valid(self):
        """Test extend_cache_ttl when data is found and valid."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = False
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.extend_cache_ttl(2020, 24, 1)
        
        assert result is True
        mock_cache_entry.extend_ttl.assert_called_once_with(24)
        mock_data_store.update_tufe_data_cache.assert_called_once_with(mock_cache_entry)
    
    def test_extend_cache_ttl_not_found(self):
        """Test extend_cache_ttl when data is not found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = None
        
        result = service.extend_cache_ttl(2020, 24, 1)
        
        assert result is False
    
    def test_extend_cache_ttl_expired(self):
        """Test extend_cache_ttl when data is expired."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = True
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.extend_cache_ttl(2020, 24, 1)
        
        assert result is False
    
    def test_extend_cache_ttl_with_error(self):
        """Test extend_cache_ttl when an error occurs."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.side_effect = Exception("Database error")
        
        with pytest.raises(TufeCacheError, match="Failed to extend cache TTL"):
            service.extend_cache_ttl(2020, 24, 1)
    
    def test_get_cache_ttl_info_found(self):
        """Test get_cache_ttl_info when data is found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        # Mock cache entry
        mock_cache_entry = Mock()
        mock_cache_entry.is_expired.return_value = False
        mock_cache_entry.get_ttl_remaining.return_value = timedelta(hours=12)
        mock_cache_entry.expires_at = datetime.now() + timedelta(hours=12)
        mock_cache_entry.cache_hit_count = 5
        mock_cache_entry.last_accessed = datetime.now() - timedelta(hours=1)
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = mock_cache_entry
        mock_data_store._row_to_tufe_data_cache.return_value = mock_cache_entry
        
        result = service.get_cache_ttl_info(2020, 1)
        
        assert result['is_expired'] is False
        assert result['ttl_remaining'] == 43200.0  # 12 hours in seconds
        assert result['expires_at'] is not None
        assert result['cache_hit_count'] == 5
        assert result['last_accessed'] is not None
    
    def test_get_cache_ttl_info_not_found(self):
        """Test get_cache_ttl_info when data is not found."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.return_value = None
        
        result = service.get_cache_ttl_info(2020, 1)
        
        assert result['is_expired'] is True
        assert result['ttl_remaining'] == 0
        assert result['expires_at'] is None
        assert result['cache_hit_count'] == 0
        assert result['last_accessed'] is None
    
    def test_get_cache_ttl_info_with_error(self):
        """Test get_cache_ttl_info when an error occurs."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.side_effect = Exception("Database error")
        
        with pytest.raises(TufeCacheError, match="Failed to get cache TTL info"):
            service.get_cache_ttl_info(2020, 1)
    
    def test_cache_oecd_data_with_mixed_valid_invalid(self):
        """Test cache_oecd_data with mixed valid and invalid data."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mixed_data = [
            InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API"),  # Valid
            InflationData(year=1999, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API"),  # Invalid year
            InflationData(year=2020, month=2, tufe_rate=Decimal("11.0"), source="OECD SDMX API")   # Valid
        ]
        
        result = service.cache_oecd_data(mixed_data)
        
        # Should cache only valid data
        assert result == 2
        assert mock_data_store.save_tufe_data_cache.call_count == 2
    
    def test_cache_oecd_data_with_database_error(self):
        """Test cache_oecd_data with database error."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        inflation_data = [InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")]
        
        mock_data_store.save_tufe_data_cache.side_effect = Exception("Database error")
        
        with pytest.raises(TufeCacheError, match="Failed to cache OECD TÜFE data"):
            service.cache_oecd_data(inflation_data)
    
    def test_get_cached_oecd_data_with_database_error(self):
        """Test get_cached_oecd_data with database error."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_tufe_data_cache_by_year_month.side_effect = Exception("Database error")
        
        with pytest.raises(TufeCacheError, match="Failed to get cached OECD data"):
            service.get_cached_oecd_data(2020, 1)
    
    def test_cleanup_expired_cache_with_database_error(self):
        """Test cleanup_expired_cache with database error."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_all_tufe_data_cache.side_effect = Exception("Database error")
        
        with pytest.raises(TufeCacheError, match="Failed to cleanup expired cache"):
            service.cleanup_expired_cache()
    
    def test_get_cache_statistics_with_database_error(self):
        """Test get_cache_statistics with database error."""
        mock_data_store = Mock()
        service = TufeCacheService(mock_data_store)
        
        mock_data_store.get_all_tufe_data_cache.side_effect = Exception("Database error")
        
        with pytest.raises(TufeCacheError, match="Failed to get cache statistics"):
            service.get_cache_statistics()


if __name__ == "__main__":
    pytest.main([__file__])