"""
Unit tests for InflationService OECD integration.

Tests the enhanced InflationService with OECD API integration,
including fetching, caching, validation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from decimal import Decimal

from src.services.inflation_service import InflationService
from src.services.exceptions import TufeApiError, TufeValidationError
from src.models.inflation_data import InflationData


class TestInflationServiceOECD:
    """Unit tests for InflationService OECD integration."""
    
    def test_initialization_with_oecd_services(self):
        """Test InflationService initialization with OECD services."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        assert service.data_store == mock_data_store
        assert service.oecd_client == mock_oecd_client
        assert service.rate_limit_handler == mock_rate_limit_handler
        assert service.data_validator == mock_data_validator
    
    def test_fetch_tufe_from_oecd_api_success(self):
        """Test successful TÜFE data fetching from OECD API."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'},
                {'year': 2020, 'month': 2, 'value': 11.0, 'source': 'OECD SDMX API'}
            ]
        }
        mock_oecd_client.fetch_tufe_data.return_value = mock_api_result
        
        result = service.fetch_tufe_from_oecd_api(2020, 2020)
        
        assert len(result) == 2
        assert result[0].year == 2020
        assert result[0].month == 1
        assert result[0].tufe_rate == Decimal("10.5")
        assert result[0].source == "OECD SDMX API"
        
        mock_oecd_client.fetch_tufe_data.assert_called_once_with(2020, 2020)
        assert mock_data_validator.validate_complete_record.call_count == 2
    
    def test_fetch_tufe_from_oecd_api_validation_error(self):
        """Test TÜFE data fetching with validation error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        # Mock API response with invalid data
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'},  # Valid
                {'year': 1999, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}  # Invalid year
            ]
        }
        mock_oecd_client.fetch_tufe_data.return_value = mock_api_result
        
        # Mock validator to raise error for invalid data
        def mock_validate(year, month, value, source):
            if year == 1999:
                raise TufeValidationError("Invalid year: 1999")
        
        mock_data_validator.validate_complete_record.side_effect = mock_validate
        
        result = service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Should return only valid data
        assert len(result) == 1
        assert result[0].year == 2020
    
    def test_fetch_tufe_from_oecd_api_api_error(self):
        """Test TÜFE data fetching with API error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        # Mock API to raise error
        mock_oecd_client.fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        with pytest.raises(TufeApiError, match="Failed to fetch TÜFE data from OECD API"):
            service.fetch_tufe_from_oecd_api(2020, 2020)
    
    def test_fetch_and_cache_oecd_tufe_data_success(self):
        """Test fetch and cache OECD TÜFE data successfully."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        # Mock successful fetch
        mock_inflation_data = [
            InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")
        ]
        
        with patch.object(service, 'fetch_tufe_from_oecd_api', return_value=mock_inflation_data):
            with patch.object(service, 'cache_oecd_tufe_data') as mock_cache:
                result = service.fetch_and_cache_oecd_tufe_data(2020, 2020)
                
                assert result == mock_inflation_data
                mock_cache.assert_called_once_with(mock_inflation_data)
    
    def test_fetch_and_cache_oecd_tufe_data_error(self):
        """Test fetch and cache OECD TÜFE data with error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        # Mock fetch to raise error
        with patch.object(service, 'fetch_tufe_from_oecd_api', side_effect=TufeApiError("API error")):
            with pytest.raises(TufeApiError, match="Failed to fetch and cache OECD TÜFE data"):
                service.fetch_and_cache_oecd_tufe_data(2020, 2020)
    
    def test_cache_oecd_tufe_data_success(self):
        """Test caching OECD TÜFE data successfully."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_inflation_data = [
            InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")
        ]
        
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            service.cache_oecd_tufe_data(mock_inflation_data)
            
            mock_cache_service.cache_oecd_data.assert_called_once_with(mock_inflation_data, ttl_hours=168)
    
    def test_cache_oecd_tufe_data_error(self):
        """Test caching OECD TÜFE data with error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_inflation_data = [
            InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")
        ]
        
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service.cache_oecd_data.side_effect = Exception("Cache error")
            mock_cache_service_class.return_value = mock_cache_service
            
            with pytest.raises(TufeApiError, match="Failed to cache OECD TÜFE data"):
                service.cache_oecd_tufe_data(mock_inflation_data)
    
    def test_get_cached_oecd_tufe_data_found(self):
        """Test getting cached OECD TÜFE data when found."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_cached_data = InflationData(year=2020, month=1, tufe_rate=Decimal("10.5"), source="OECD SDMX API")
        
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service.get_cached_oecd_data.return_value = mock_cached_data
            mock_cache_service_class.return_value = mock_cache_service
            
            result = service.get_cached_oecd_tufe_data(2020, 1)
            
            assert result == mock_cached_data
            mock_cache_service.get_cached_oecd_data.assert_called_once_with(2020, 1)
    
    def test_get_cached_oecd_tufe_data_not_found(self):
        """Test getting cached OECD TÜFE data when not found."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service.get_cached_oecd_data.return_value = None
            mock_cache_service_class.return_value = mock_cache_service
            
            result = service.get_cached_oecd_tufe_data(2020, 1)
            
            assert result is None
    
    def test_get_cached_oecd_tufe_data_error(self):
        """Test getting cached OECD TÜFE data with error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service.get_cached_oecd_data.side_effect = Exception("Cache error")
            mock_cache_service_class.return_value = mock_cache_service
            
            with pytest.raises(TufeApiError, match="Failed to get cached OECD TÜFE data"):
                service.get_cached_oecd_tufe_data(2020, 1)
    
    def test_is_oecd_api_healthy_true(self):
        """Test OECD API health check when healthy."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_oecd_client.is_healthy.return_value = True
        
        result = service.is_oecd_api_healthy()
        
        assert result is True
        mock_oecd_client.is_healthy.assert_called_once()
    
    def test_is_oecd_api_healthy_false(self):
        """Test OECD API health check when unhealthy."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_oecd_client.is_healthy.return_value = False
        
        result = service.is_oecd_api_healthy()
        
        assert result is False
    
    def test_is_oecd_api_healthy_error(self):
        """Test OECD API health check with error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_oecd_client.is_healthy.side_effect = Exception("Health check error")
        
        result = service.is_oecd_api_healthy()
        
        assert result is False
    
    def test_get_oecd_api_info_success(self):
        """Test getting OECD API info successfully."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_api_info = {
            "name": "OECD SDMX API Client",
            "base_url": "https://stats.oecd.org/restsdmx/sdmx.ashx",
            "series_code": "A.TUR.CPALTT01.M"
        }
        mock_oecd_client.get_api_info.return_value = mock_api_info
        
        result = service.get_oecd_api_info()
        
        assert result == mock_api_info
        mock_oecd_client.get_api_info.assert_called_once()
    
    def test_get_oecd_api_info_error(self):
        """Test getting OECD API info with error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_oecd_client.get_api_info.side_effect = Exception("API info error")
        
        with pytest.raises(TufeApiError, match="Failed to get OECD API info"):
            service.get_oecd_api_info()
    
    def test_get_rate_limit_status_success(self):
        """Test getting rate limit status successfully."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_rate_status = {
            "can_make_request": True,
            "remaining_hour": 95,
            "remaining_day": 950
        }
        mock_rate_limit_handler.get_rate_limit_status.return_value = mock_rate_status
        
        result = service.get_rate_limit_status()
        
        assert result == mock_rate_status
        mock_rate_limit_handler.get_rate_limit_status.assert_called_once()
    
    def test_get_rate_limit_status_error(self):
        """Test getting rate limit status with error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_rate_limit_handler.get_rate_limit_status.side_effect = Exception("Rate limit error")
        
        with pytest.raises(TufeApiError, match="Failed to get rate limit status"):
            service.get_rate_limit_status()
    
    def test_validate_oecd_data_success(self):
        """Test validating OECD data successfully."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_data = [
            {"year": 2020, "month": 1, "value": 10.5, "source": "OECD SDMX API"},
            {"year": 2020, "month": 2, "value": 11.0, "source": "OECD SDMX API"}
        ]
        mock_validated_data = mock_data.copy()
        mock_data_validator.validate_batch_data.return_value = mock_validated_data
        
        result = service.validate_oecd_data(mock_data)
        
        assert result == mock_validated_data
        mock_data_validator.validate_batch_data.assert_called_once_with(mock_data)
    
    def test_validate_oecd_data_error(self):
        """Test validating OECD data with error."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        mock_data = [{"year": 2020, "month": 1, "value": 10.5, "source": "OECD SDMX API"}]
        mock_data_validator.validate_batch_data.side_effect = Exception("Validation error")
        
        with pytest.raises(TufeValidationError, match="Failed to validate OECD data"):
            service.validate_oecd_data(mock_data)
    
    def test_integration_flow_success(self):
        """Test complete integration flow from fetch to cache."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        # Mock successful API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}
            ]
        }
        mock_oecd_client.fetch_tufe_data.return_value = mock_api_result
        
        # Mock successful caching
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            result = service.fetch_and_cache_oecd_tufe_data(2020, 2020)
            
            # Verify API call
            mock_oecd_client.fetch_tufe_data.assert_called_once_with(2020, 2020)
            
            # Verify validation
            mock_data_validator.validate_complete_record.assert_called_once()
            
            # Verify caching
            mock_cache_service.cache_oecd_data.assert_called_once()
            
            # Verify result
            assert len(result) == 1
            assert result[0].year == 2020
            assert result[0].month == 1
            assert result[0].tufe_rate == Decimal("10.5")
    
    def test_error_handling_chain(self):
        """Test error handling chain from API to user."""
        mock_data_store = Mock()
        mock_oecd_client = Mock()
        mock_rate_limit_handler = Mock()
        mock_data_validator = Mock()
        
        service = InflationService(
            data_store=mock_data_store,
            oecd_client=mock_oecd_client,
            rate_limit_handler=mock_rate_limit_handler,
            validator=mock_data_validator
        )
        
        # Test API error
        mock_oecd_client.fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        with pytest.raises(TufeApiError, match="Failed to fetch TÜFE data from OECD API"):
            service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Test validation error
        mock_oecd_client.fetch_tufe_data.side_effect = None
        mock_data_validator.validate_complete_record.side_effect = TufeValidationError("Invalid data")
        
        result = service.fetch_tufe_from_oecd_api(2020, 2020)
        assert result == []  # Should return empty list for validation errors
        
        # Test cache error
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service.get_cached_oecd_data.side_effect = Exception("Cache error")
            mock_cache_service_class.return_value = mock_cache_service
            
            with pytest.raises(TufeApiError, match="Failed to get cached OECD TÜFE data"):
                service.get_cached_oecd_tufe_data(2020, 1)


if __name__ == "__main__":
    pytest.main([__file__])
