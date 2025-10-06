"""
Integration tests for complete OECD fetch flow.

Tests the complete end-to-end flow from API request to database storage,
including error handling, caching, and data validation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from decimal import Decimal
import tempfile
import os

from src.storage.data_store import DataStore
from src.services.inflation_service import InflationService
from src.services.oecd_api_client import OECDApiClient
from src.services.rate_limit_handler import RateLimitHandler
from src.services.data_validator import DataValidator
from src.models.inflation_data import InflationData


class TestCompleteOECDFlow:
    """Integration tests for complete OECD fetch flow."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def data_store(self, temp_db):
        """Create DataStore with temporary database."""
        return DataStore(db_path=temp_db)
    
    @pytest.fixture
    def oecd_client(self):
        """Create OECDApiClient mock."""
        return Mock(spec=OECDApiClient)
    
    @pytest.fixture
    def rate_limit_handler(self):
        """Create RateLimitHandler mock."""
        return Mock(spec=RateLimitHandler)
    
    @pytest.fixture
    def data_validator(self):
        """Create DataValidator mock."""
        return Mock(spec=DataValidator)
    
    @pytest.fixture
    def inflation_service(self, data_store, oecd_client, rate_limit_handler, data_validator):
        """Create InflationService with mocked dependencies."""
        return InflationService(
            data_store=data_store,
            oecd_client=oecd_client,
            rate_limit_handler=rate_limit_handler,
            validator=data_validator
        )
    
    def test_complete_successful_fetch_flow(self, inflation_service, oecd_client, data_validator):
        """Test complete successful fetch flow from API to database."""
        # Mock successful API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'},
                {'year': 2020, 'month': 2, 'value': 11.0, 'source': 'OECD SDMX API'},
                {'year': 2020, 'month': 3, 'value': 11.5, 'source': 'OECD SDMX API'}
            ]
        }
        oecd_client.fetch_tufe_data.return_value = mock_api_result
        
        # Mock successful validation
        data_validator.validate_complete_record.return_value = None  # No exception
        
        # Execute the flow
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Verify API call
        oecd_client.fetch_tufe_data.assert_called_once_with(2020, 2020)
        
        # Verify validation calls
        assert data_validator.validate_complete_record.call_count == 3
        
        # Verify result
        assert len(result) == 3
        assert all(isinstance(item, InflationData) for item in result)
        assert result[0].year == 2020
        assert result[0].month == 1
        assert result[0].tufe_rate == Decimal("10.5")
        assert result[0].source == "OECD SDMX API"
    
    def test_fetch_flow_with_validation_errors(self, inflation_service, oecd_client, data_validator):
        """Test fetch flow with some validation errors."""
        from src.services.exceptions import TufeValidationError
        
        # Mock API response with mixed valid/invalid data
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'},  # Valid
                {'year': 1999, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'},  # Invalid year
                {'year': 2020, 'month': 2, 'value': 11.0, 'source': 'OECD SDMX API'}   # Valid
            ]
        }
        oecd_client.fetch_tufe_data.return_value = mock_api_result
        
        # Mock validation to raise error for invalid data
        def mock_validate(year, month, value, source):
            if year == 1999:
                raise TufeValidationError("Invalid year: 1999")
        
        data_validator.validate_complete_record.side_effect = mock_validate
        
        # Execute the flow
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Verify only valid data is returned
        assert len(result) == 2
        assert all(item.year == 2020 for item in result)
        assert result[0].month == 1
        assert result[1].month == 2
    
    def test_fetch_flow_with_api_error(self, inflation_service, oecd_client):
        """Test fetch flow with API error."""
        from src.services.exceptions import TufeApiError
        
        # Mock API to raise error
        oecd_client.fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        # Execute the flow and expect error
        with pytest.raises(TufeApiError, match="Failed to fetch TÜFE data from OECD API"):
            inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
    
    def test_fetch_and_cache_flow_success(self, inflation_service, oecd_client, data_validator):
        """Test complete fetch and cache flow."""
        # Mock successful API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}
            ]
        }
        oecd_client.fetch_tufe_data.return_value = mock_api_result
        
        # Mock successful validation
        data_validator.validate_complete_record.return_value = None
        
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Execute the flow
            result = inflation_service.fetch_and_cache_oecd_tufe_data(2020, 2020)
            
            # Verify API call
            oecd_client.fetch_tufe_data.assert_called_once_with(2020, 2020)
            
            # Verify caching
            mock_cache_service.cache_oecd_data.assert_called_once()
            cached_data = mock_cache_service.cache_oecd_data.call_args[0][0]
            assert len(cached_data) == 1
            assert isinstance(cached_data[0], InflationData)
            
            # Verify result
            assert len(result) == 1
            assert result[0].year == 2020
    
    def test_fetch_and_cache_flow_with_error(self, inflation_service, oecd_client):
        """Test fetch and cache flow with error."""
        from src.services.exceptions import TufeApiError
        
        # Mock API to raise error
        oecd_client.fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        # Execute the flow and expect error
        with pytest.raises(TufeApiError, match="Failed to fetch and cache OECD TÜFE data"):
            inflation_service.fetch_and_cache_oecd_tufe_data(2020, 2020)
    
    def test_cached_data_retrieval_flow(self, inflation_service):
        """Test cached data retrieval flow."""
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Mock cached data
            mock_cached_data = InflationData(
                year=2020,
                month=1,
                tufe_rate=Decimal("10.5"),
                source="OECD SDMX API"
            )
            mock_cache_service.get_cached_oecd_data.return_value = mock_cached_data
            
            # Execute the flow
            result = inflation_service.get_cached_oecd_tufe_data(2020, 1)
            
            # Verify cache call
            mock_cache_service.get_cached_oecd_data.assert_called_once_with(2020, 1)
            
            # Verify result
            assert result == mock_cached_data
    
    def test_cached_data_retrieval_not_found(self, inflation_service):
        """Test cached data retrieval when not found."""
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Mock no cached data
            mock_cache_service.get_cached_oecd_data.return_value = None
            
            # Execute the flow
            result = inflation_service.get_cached_oecd_tufe_data(2020, 1)
            
            # Verify result
            assert result is None
    
    def test_cached_data_retrieval_error(self, inflation_service):
        """Test cached data retrieval with error."""
        from src.services.exceptions import TufeApiError
        
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Mock cache error
            mock_cache_service.get_cached_oecd_data.side_effect = Exception("Cache error")
            
            # Execute the flow and expect error
            with pytest.raises(TufeApiError, match="Failed to get cached OECD TÜFE data"):
                inflation_service.get_cached_oecd_tufe_data(2020, 1)
    
    def test_api_health_check_flow(self, inflation_service, oecd_client):
        """Test API health check flow."""
        # Mock healthy API
        oecd_client.is_healthy.return_value = True
        
        # Execute the flow
        result = inflation_service.is_oecd_api_healthy()
        
        # Verify API call
        oecd_client.is_healthy.assert_called_once()
        
        # Verify result
        assert result is True
    
    def test_api_health_check_unhealthy(self, inflation_service, oecd_client):
        """Test API health check when unhealthy."""
        # Mock unhealthy API
        oecd_client.is_healthy.return_value = False
        
        # Execute the flow
        result = inflation_service.is_oecd_api_healthy()
        
        # Verify result
        assert result is False
    
    def test_api_health_check_error(self, inflation_service, oecd_client):
        """Test API health check with error."""
        # Mock API error
        oecd_client.is_healthy.side_effect = Exception("Health check error")
        
        # Execute the flow
        result = inflation_service.is_oecd_api_healthy()
        
        # Verify result (should return False on error)
        assert result is False
    
    def test_api_info_retrieval_flow(self, inflation_service, oecd_client):
        """Test API info retrieval flow."""
        # Mock API info
        mock_api_info = {
            "name": "OECD SDMX API Client",
            "base_url": "https://stats.oecd.org/restsdmx/sdmx.ashx",
            "series_code": "A.TUR.CPALTT01.M"
        }
        oecd_client.get_api_info.return_value = mock_api_info
        
        # Execute the flow
        result = inflation_service.get_oecd_api_info()
        
        # Verify API call
        oecd_client.get_api_info.assert_called_once()
        
        # Verify result
        assert result == mock_api_info
    
    def test_api_info_retrieval_error(self, inflation_service, oecd_client):
        """Test API info retrieval with error."""
        from src.services.exceptions import TufeApiError
        
        # Mock API error
        oecd_client.get_api_info.side_effect = Exception("API info error")
        
        # Execute the flow and expect error
        with pytest.raises(TufeApiError, match="Failed to get OECD API info"):
            inflation_service.get_oecd_api_info()
    
    def test_rate_limit_status_flow(self, inflation_service, rate_limit_handler):
        """Test rate limit status flow."""
        # Mock rate limit status
        mock_rate_status = {
            "can_make_request": True,
            "remaining_hour": 95,
            "remaining_day": 950
        }
        rate_limit_handler.get_rate_limit_status.return_value = mock_rate_status
        
        # Execute the flow
        result = inflation_service.get_rate_limit_status()
        
        # Verify handler call
        rate_limit_handler.get_rate_limit_status.assert_called_once()
        
        # Verify result
        assert result == mock_rate_status
    
    def test_rate_limit_status_error(self, inflation_service, rate_limit_handler):
        """Test rate limit status with error."""
        from src.services.exceptions import TufeApiError
        
        # Mock handler error
        rate_limit_handler.get_rate_limit_status.side_effect = Exception("Rate limit error")
        
        # Execute the flow and expect error
        with pytest.raises(TufeApiError, match="Failed to get rate limit status"):
            inflation_service.get_rate_limit_status()
    
    def test_data_validation_flow(self, inflation_service, data_validator):
        """Test data validation flow."""
        # Mock data to validate
        mock_data = [
            {"year": 2020, "month": 1, "value": 10.5, "source": "OECD SDMX API"},
            {"year": 2020, "month": 2, "value": 11.0, "source": "OECD SDMX API"}
        ]
        mock_validated_data = mock_data.copy()
        data_validator.validate_batch_data.return_value = mock_validated_data
        
        # Execute the flow
        result = inflation_service.validate_oecd_data(mock_data)
        
        # Verify validator call
        data_validator.validate_batch_data.assert_called_once_with(mock_data)
        
        # Verify result
        assert result == mock_validated_data
    
    def test_data_validation_error(self, inflation_service, data_validator):
        """Test data validation with error."""
        from src.services.exceptions import TufeValidationError
        
        # Mock data to validate
        mock_data = [{"year": 2020, "month": 1, "value": 10.5, "source": "OECD SDMX API"}]
        
        # Mock validator error
        data_validator.validate_batch_data.side_effect = Exception("Validation error")
        
        # Execute the flow and expect error
        with pytest.raises(TufeValidationError, match="Failed to validate OECD data"):
            inflation_service.validate_oecd_data(mock_data)
    
    def test_error_handling_chain(self, inflation_service, oecd_client, data_validator):
        """Test complete error handling chain."""
        from src.services.exceptions import TufeApiError, TufeValidationError
        
        # Test 1: API error
        oecd_client.fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        with pytest.raises(TufeApiError, match="Failed to fetch TÜFE data from OECD API"):
            inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Test 2: Validation error (should return empty list)
        oecd_client.fetch_tufe_data.side_effect = None
        oecd_client.fetch_tufe_data.return_value = {
            'items': [{'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}]
        }
        data_validator.validate_complete_record.side_effect = TufeValidationError("Invalid data")
        
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        assert result == []  # Should return empty list for validation errors
        
        # Test 3: Cache error
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            mock_cache_service.get_cached_oecd_data.side_effect = Exception("Cache error")
            
            with pytest.raises(TufeApiError, match="Failed to get cached OECD TÜFE data"):
                inflation_service.get_cached_oecd_tufe_data(2020, 1)
    
    def test_performance_characteristics(self, inflation_service, oecd_client, data_validator):
        """Test performance characteristics of the flow."""
        import time
        
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': i, 'value': 10.0 + i, 'source': 'OECD SDMX API'}
                for i in range(1, 13)  # 12 months of data
            ]
        }
        oecd_client.fetch_tufe_data.return_value = mock_api_result
        data_validator.validate_complete_record.return_value = None
        
        # Measure execution time
        start_time = time.time()
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verify result
        assert len(result) == 12
        assert execution_time < 1.0  # Should complete in less than 1 second
        
        # Verify all data is valid
        assert all(isinstance(item, InflationData) for item in result)
        assert all(item.year == 2020 for item in result)
        assert all(1 <= item.month <= 12 for item in result)
    
    def test_large_dataset_handling(self, inflation_service, oecd_client, data_validator):
        """Test handling of large datasets."""
        # Mock large API response (5 years of monthly data)
        mock_api_result = {
            'items': [
                {'year': year, 'month': month, 'value': 10.0 + (year - 2020) * 0.5, 'source': 'OECD SDMX API'}
                for year in range(2020, 2025)
                for month in range(1, 13)
            ]
        }
        oecd_client.fetch_tufe_data.return_value = mock_api_result
        data_validator.validate_complete_record.return_value = None
        
        # Execute the flow
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2024)
        
        # Verify result
        assert len(result) == 60  # 5 years * 12 months
        assert all(isinstance(item, InflationData) for item in result)
        
        # Verify data integrity
        years = set(item.year for item in result)
        assert years == {2020, 2021, 2022, 2023, 2024}
        
        months = set(item.month for item in result)
        assert months == set(range(1, 13))


if __name__ == "__main__":
    pytest.main([__file__])
