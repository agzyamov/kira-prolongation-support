"""
End-to-end tests for OECD API UI integration.

Tests the complete user journey from Streamlit UI to database storage,
including error handling, user feedback, and data display.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
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


class TestOECDUIIntegration:
    """End-to-end tests for OECD API UI integration."""
    
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
    def mock_services(self):
        """Create mocked services for UI testing."""
        oecd_client = Mock(spec=OECDApiClient)
        rate_limit_handler = Mock(spec=RateLimitHandler)
        data_validator = Mock(spec=DataValidator)
        
        return {
            'oecd_client': oecd_client,
            'rate_limit_handler': rate_limit_handler,
            'data_validator': data_validator
        }
    
    @pytest.fixture
    def inflation_service(self, data_store, mock_services):
        """Create InflationService with mocked dependencies."""
        return InflationService(
            data_store=data_store,
            oecd_client=mock_services['oecd_client'],
            rate_limit_handler=mock_services['rate_limit_handler'],
            validator=mock_services['data_validator']
        )
    
    def test_ui_fetch_button_success_flow(self, inflation_service, mock_services):
        """Test successful UI fetch button flow."""
        # Mock successful API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'},
                {'year': 2020, 'month': 2, 'value': 11.0, 'source': 'OECD SDMX API'}
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Simulate UI fetch button click
            result = inflation_service.fetch_and_cache_oecd_tufe_data(2020, 2020)
            
            # Verify API call
            mock_services['oecd_client'].fetch_tufe_data.assert_called_once_with(2020, 2020)
            
            # Verify validation
            assert mock_services['data_validator'].validate_complete_record.call_count == 2
            
            # Verify caching
            mock_cache_service.cache_oecd_data.assert_called_once()
            
            # Verify result for UI display
            assert len(result) == 2
            assert all(isinstance(item, InflationData) for item in result)
            assert result[0].year == 2020
            assert result[0].month == 1
            assert result[0].tufe_rate == Decimal("10.5")
            assert result[0].source == "OECD SDMX API"
    
    def test_ui_fetch_button_error_flow(self, inflation_service, mock_services):
        """Test UI fetch button error flow."""
        from src.services.exceptions import TufeApiError
        
        # Mock API error
        mock_services['oecd_client'].fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        # Simulate UI fetch button click with error
        with pytest.raises(TufeApiError, match="Failed to fetch and cache OECD TÜFE data"):
            inflation_service.fetch_and_cache_oecd_tufe_data(2020, 2020)
        
        # Verify API call was attempted
        mock_services['oecd_client'].fetch_tufe_data.assert_called_once_with(2020, 2020)
    
    def test_ui_rate_limit_display(self, inflation_service, mock_services):
        """Test UI rate limit status display."""
        # Mock rate limit status
        mock_rate_status = {
            "can_make_request": True,
            "remaining_hour": 95,
            "remaining_day": 950,
            "message": "Requests allowed."
        }
        mock_services['rate_limit_handler'].get_rate_limit_status.return_value = mock_rate_status
        
        # Get rate limit status for UI display
        result = inflation_service.get_rate_limit_status()
        
        # Verify result for UI display
        assert result['can_make_request'] is True
        assert result['remaining_hour'] == 95
        assert result['remaining_day'] == 950
        assert result['message'] == "Requests allowed."
    
    def test_ui_rate_limit_exceeded_display(self, inflation_service, mock_services):
        """Test UI rate limit exceeded display."""
        # Mock rate limit exceeded status
        mock_rate_status = {
            "can_make_request": False,
            "remaining_hour": 0,
            "remaining_day": 0,
            "message": "Rate limit exceeded. Please try again later."
        }
        mock_services['rate_limit_handler'].get_rate_limit_status.return_value = mock_rate_status
        
        # Get rate limit status for UI display
        result = inflation_service.get_rate_limit_status()
        
        # Verify result for UI display
        assert result['can_make_request'] is False
        assert result['remaining_hour'] == 0
        assert result['remaining_day'] == 0
        assert result['message'] == "Rate limit exceeded. Please try again later."
    
    def test_ui_api_health_display(self, inflation_service, mock_services):
        """Test UI API health status display."""
        # Mock healthy API
        mock_services['oecd_client'].is_healthy.return_value = True
        
        # Get API health for UI display
        result = inflation_service.is_oecd_api_healthy()
        
        # Verify result for UI display
        assert result is True
        
        # Mock unhealthy API
        mock_services['oecd_client'].is_healthy.return_value = False
        
        # Get API health for UI display
        result = inflation_service.is_oecd_api_healthy()
        
        # Verify result for UI display
        assert result is False
    
    def test_ui_cached_data_display(self, inflation_service):
        """Test UI cached data display."""
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
            
            # Get cached data for UI display
            result = inflation_service.get_cached_oecd_tufe_data(2020, 1)
            
            # Verify result for UI display
            assert result is not None
            assert result.year == 2020
            assert result.month == 1
            assert result.tufe_rate == Decimal("10.5")
            assert result.source == "OECD SDMX API"
    
    def test_ui_no_cached_data_display(self, inflation_service):
        """Test UI display when no cached data is available."""
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Mock no cached data
            mock_cache_service.get_cached_oecd_data.return_value = None
            
            # Get cached data for UI display
            result = inflation_service.get_cached_oecd_tufe_data(2020, 1)
            
            # Verify result for UI display
            assert result is None
    
    def test_ui_api_info_display(self, inflation_service, mock_services):
        """Test UI API info display."""
        # Mock API info
        mock_api_info = {
            "name": "OECD SDMX API Client",
            "base_url": "https://stats.oecd.org/restsdmx/sdmx.ashx",
            "series_code": "A.TUR.CPALTT01.M",
            "last_checked": "2025-01-27T10:30:00Z"
        }
        mock_services['oecd_client'].get_api_info.return_value = mock_api_info
        
        # Get API info for UI display
        result = inflation_service.get_oecd_api_info()
        
        # Verify result for UI display
        assert result['name'] == "OECD SDMX API Client"
        assert result['base_url'] == "https://stats.oecd.org/restsdmx/sdmx.ashx"
        assert result['series_code'] == "A.TUR.CPALTT01.M"
        assert result['last_checked'] == "2025-01-27T10:30:00Z"
    
    def test_ui_error_message_display(self, inflation_service, mock_services):
        """Test UI error message display."""
        from src.services.exceptions import TufeApiError, TufeValidationError
        
        # Test API error message
        mock_services['oecd_client'].fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        with pytest.raises(TufeApiError) as exc_info:
            inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Verify error message is user-friendly
        assert "Failed to fetch TÜFE data from OECD API" in str(exc_info.value)
        
        # Test validation error message
        mock_services['oecd_client'].fetch_tufe_data.side_effect = None
        mock_services['oecd_client'].fetch_tufe_data.return_value = {
            'items': [{'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}]
        }
        mock_services['data_validator'].validate_complete_record.side_effect = TufeValidationError("Invalid data")
        
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Verify validation errors are handled gracefully
        assert result == []  # Should return empty list for validation errors
    
    def test_ui_progress_indicator_simulation(self, inflation_service, mock_services):
        """Test UI progress indicator simulation."""
        import time
        
        # Mock API response with delay
        def mock_fetch_with_delay(*args, **kwargs):
            time.sleep(0.1)  # Simulate API delay
            return {
                'items': [
                    {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}
                ]
            }
        
        mock_services['oecd_client'].fetch_tufe_data.side_effect = mock_fetch_with_delay
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Simulate UI progress indicator
        start_time = time.time()
        
        # Show loading spinner (simulated)
        with patch('builtins.print') as mock_print:
            mock_print("🔄 Fetching TÜFE data from OECD API...")
            
            result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Show success message (simulated)
            mock_print(f"✅ Successfully fetched {len(result)} TÜFE data points")
        
        # Verify progress indicator timing
        assert duration >= 0.1  # Should take at least the simulated delay
        assert duration < 1.0   # Should complete within reasonable time
        
        # Verify result
        assert len(result) == 1
        assert result[0].year == 2020
    
    def test_ui_data_table_display(self, inflation_service, mock_services):
        """Test UI data table display."""
        # Mock API response with multiple data points
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'},
                {'year': 2020, 'month': 2, 'value': 11.0, 'source': 'OECD SDMX API'},
                {'year': 2020, 'month': 3, 'value': 11.5, 'source': 'OECD SDMX API'},
                {'year': 2020, 'month': 4, 'value': 12.0, 'source': 'OECD SDMX API'}
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Get data for UI table display
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Verify data structure for UI table
        assert len(result) == 4
        
        # Verify each row has required fields for UI display
        for i, item in enumerate(result):
            assert isinstance(item, InflationData)
            assert item.year == 2020
            assert item.month == i + 1
            assert isinstance(item.tufe_rate, Decimal)
            assert item.source == "OECD SDMX API"
    
    def test_ui_cache_statistics_display(self, inflation_service):
        """Test UI cache statistics display."""
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Mock cache statistics
            mock_cache_stats = {
                'total_entries': 50,
                'expired_entries': 5,
                'active_entries': 45,
                'total_hits': 120,
                'hit_rate': 0.85,
                'avg_fetch_duration': 1.2
            }
            mock_cache_service.get_cache_statistics.return_value = mock_cache_stats
            
            # Get cache statistics for UI display
            result = inflation_service.get_cache_statistics()
            
            # Verify result for UI display
            assert result['total_entries'] == 50
            assert result['expired_entries'] == 5
            assert result['active_entries'] == 45
            assert result['total_hits'] == 120
            assert result['hit_rate'] == 0.85
            assert result['avg_fetch_duration'] == 1.2
    
    def test_ui_manual_entry_fallback(self, inflation_service, mock_services):
        """Test UI manual entry fallback when API fails."""
        from src.services.exceptions import TufeApiError
        
        # Mock API failure
        mock_services['oecd_client'].fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        # Simulate UI fallback to manual entry
        try:
            result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        except TufeApiError as e:
            # UI should show error message and suggest manual entry
            error_message = str(e)
            assert "Failed to fetch TÜFE data from OECD API" in error_message
            
            # UI should provide manual entry option
            # This would be handled by the Streamlit UI, not the service
            pass
    
    def test_ui_data_source_attribution(self, inflation_service, mock_services):
        """Test UI data source attribution display."""
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Get data for UI display
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Verify data source attribution
        assert len(result) == 1
        assert result[0].source == "OECD SDMX API"
        
        # UI should display: "Data source: OECD SDMX API"
        attribution = f"Data source: {result[0].source}"
        assert attribution == "Data source: OECD SDMX API"
    
    def test_ui_year_month_selection(self, inflation_service, mock_services):
        """Test UI year and month selection."""
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2023, 'month': 6, 'value': 15.5, 'source': 'OECD SDMX API'}
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Simulate UI year/month selection
        selected_year = 2023
        selected_month = 6
        
        # Get data for selected year/month
        result = inflation_service.fetch_tufe_from_oecd_api(selected_year, selected_year)
        
        # Verify API call with selected parameters
        mock_services['oecd_client'].fetch_tufe_data.assert_called_once_with(selected_year, selected_year)
        
        # Verify result matches selection
        assert len(result) == 1
        assert result[0].year == selected_year
        assert result[0].month == selected_month
    
    def test_ui_bulk_fetch_display(self, inflation_service, mock_services):
        """Test UI bulk fetch display."""
        # Mock API response for multiple years
        mock_api_result = {
            'items': [
                {'year': year, 'month': month, 'value': 10.0 + (year - 2020) * 0.5, 'source': 'OECD SDMX API'}
                for year in range(2020, 2023)  # 3 years
                for month in range(1, 13)  # 12 months
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Simulate UI bulk fetch
        start_year = 2020
        end_year = 2022
        
        result = inflation_service.fetch_tufe_from_oecd_api(start_year, end_year)
        
        # Verify bulk fetch result
        assert len(result) == 36  # 3 years * 12 months
        
        # Verify data covers the requested range
        years = set(item.year for item in result)
        assert years == {2020, 2021, 2022}
        
        months = set(item.month for item in result)
        assert months == set(range(1, 13))
    
    def test_ui_error_recovery_flow(self, inflation_service, mock_services):
        """Test UI error recovery flow."""
        from src.services.exceptions import TufeApiError
        
        # Mock initial API failure
        mock_services['oecd_client'].fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        # Simulate UI error handling
        try:
            result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        except TufeApiError:
            # UI should show error message
            pass
        
        # Mock API recovery
        mock_services['oecd_client'].fetch_tufe_data.side_effect = None
        mock_services['oecd_client'].fetch_tufe_data.return_value = {
            'items': [{'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}]
        }
        
        # Simulate UI retry
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        # Verify recovery
        assert len(result) == 1
        assert result[0].year == 2020
        assert result[0].tufe_rate == Decimal("10.5")


if __name__ == "__main__":
    pytest.main([__file__])
