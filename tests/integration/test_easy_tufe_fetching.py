"""
Integration tests for one-click TÜFE fetching.
Tests the complete user workflow for easy TÜFE data fetching.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.services.tufe_fetch_service import TufeFetchService
from src.services.tufe_source_manager import TufeSourceManager
from src.services.tufe_auto_config import TufeAutoConfig
from src.models.tufe_fetch_result import TufeFetchResult
from src.models.tufe_data import TufeData
from src.models.tufe_data_source import TufeDataSource


class TestEasyTufeFetching:
    """Test one-click TÜFE fetching integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data_store = Mock()
        self.source_manager = TufeSourceManager(self.test_data_store)
        self.auto_config = TufeAutoConfig(self.test_data_store)
        self.fetch_service = TufeFetchService(self.test_data_store, self.source_manager)
    
    def test_one_click_tufe_fetching_success(self):
        """Test successful one-click TÜFE fetching workflow."""
        # Arrange
        year = 2023
        expected_tufe_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        expected_source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True,
            priority=1,
            reliability_score=0.95,
            health_status="healthy"
        )
        
        # Mock the complete workflow
        with patch.object(self.auto_config, 'is_auto_config_enabled', return_value=True), \
             patch.object(self.source_manager, 'get_best_source', return_value=expected_source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=expected_tufe_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True):
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert isinstance(result, TufeFetchResult)
            assert result.success is True
            assert result.data is not None
            assert result.data.inflation_rate_percent == 64.27
            assert result.source is not None
            assert result.source.source_name == "TCMB EVDS API"
            assert result.fetch_duration < 2.0  # Performance requirement
            assert result.cached is False  # First fetch, not cached
    
    def test_one_click_tufe_fetching_with_cached_data(self):
        """Test one-click TÜFE fetching with cached data."""
        # Arrange
        year = 2023
        cached_tufe_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now() - timedelta(hours=1),
            is_validated=True
        )
        
        # Mock cache hit
        with patch.object(self.fetch_service, '_check_cache', return_value=cached_tufe_data):
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.cached is True
            assert result.fetch_duration < 0.1  # Cache should be very fast
            assert result.data.inflation_rate_percent == 64.27
    
    def test_one_click_tufe_fetching_auto_config_setup(self):
        """Test one-click TÜFE fetching with automatic configuration setup."""
        # Arrange
        year = 2023
        
        # Mock auto-config setup
        with patch.object(self.auto_config, 'is_auto_config_enabled', return_value=False), \
             patch.object(self.auto_config, 'setup_zero_config', return_value=Mock()), \
             patch.object(self.auto_config, 'discover_available_sources', return_value=[Mock()]), \
             patch.object(self.auto_config, 'auto_configure_sources', return_value=[Mock()]), \
             patch.object(self.source_manager, 'get_best_source', return_value=Mock()), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=Mock()), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True):
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            # Verify auto-config was set up
            self.auto_config.setup_zero_config.assert_called_once()
            self.auto_config.discover_available_sources.assert_called_once()
            self.auto_config.auto_configure_sources.assert_called_once()
    
    def test_one_click_tufe_fetching_source_fallback(self):
        """Test one-click TÜFE fetching with automatic source fallback."""
        # Arrange
        year = 2023
        
        primary_source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True,
            priority=1,
            reliability_score=0.95,
            health_status="healthy"
        )
        
        backup_source = TufeDataSource(
            id=2,
            source_name="TÜİK API",
            api_endpoint="https://data.tuik.gov.tr/api/",
            series_code="TUF01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=200,
            is_active=True,
            priority=2,
            reliability_score=0.90,
            health_status="healthy"
        )
        
        expected_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TÜİK API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        # Mock primary source failure and backup success
        with patch.object(self.source_manager, 'get_best_source', side_effect=[primary_source, backup_source]), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=[Exception("Primary source failed"), expected_data]), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed, \
             patch.object(self.source_manager, 'mark_source_success') as mock_mark_success:
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.data.source == "TÜİK API"
            assert len(result.attempts) == 2  # Two attempts
            assert result.attempts[0].success is False
            assert result.attempts[1].success is True
            mock_mark_failed.assert_called_once_with(1, "Primary source failed")
            mock_mark_success.assert_called_once_with(2, pytest.approx(0.0, abs=1.0))
    
    def test_one_click_tufe_fetching_all_sources_fail(self):
        """Test one-click TÜFE fetching when all sources fail."""
        # Arrange
        year = 2023
        
        sources = [
            TufeDataSource(id=1, source_name="TCMB", priority=1, health_status="healthy"),
            TufeDataSource(id=2, source_name="TÜİK", priority=2, health_status="healthy"),
            TufeDataSource(id=3, source_name="EPİAŞ", priority=3, health_status="healthy")
        ]
        
        # Mock all sources failing
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=sources), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=Exception("Source failed")), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed:
            
            # Act & Assert
            with pytest.raises(Exception, match="All sources failed"):
                self.fetch_service.fetch_tufe_easy(year)
            
            # Verify all sources were marked as failed
            assert mock_mark_failed.call_count == 3
    
    def test_one_click_tufe_fetching_data_validation_failure(self):
        """Test one-click TÜFE fetching with data validation failure."""
        # Arrange
        year = 2023
        
        source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True,
            priority=1,
            reliability_score=0.95,
            health_status="healthy"
        )
        
        invalid_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=200.0,  # Invalid rate
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=False
        )
        
        # Mock source success but validation failure
        with patch.object(self.source_manager, 'get_best_source', return_value=source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=invalid_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=False), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed:
            
            # Act & Assert
            with pytest.raises(Exception, match="Data validation failed"):
                self.fetch_service.fetch_tufe_easy(year)
            
            mock_mark_failed.assert_called_once()
    
    def test_one_click_tufe_fetching_performance_requirements(self):
        """Test that one-click TÜFE fetching meets performance requirements."""
        # Arrange
        year = 2023
        
        source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True,
            priority=1,
            reliability_score=0.95,
            health_status="healthy"
        )
        
        expected_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        # Mock fast response
        with patch.object(self.source_manager, 'get_best_source', return_value=source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=expected_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True):
            
            # Act
            start_time = datetime.now()
            result = self.fetch_service.fetch_tufe_easy(year)
            end_time = datetime.now()
            
            # Assert
            total_duration = (end_time - start_time).total_seconds()
            assert total_duration < 2.0  # Must be under 2 seconds
            assert result.success is True
            assert result.fetch_duration < 2.0
    
    def test_one_click_tufe_fetching_user_feedback(self):
        """Test that one-click TÜFE fetching provides clear user feedback."""
        # Arrange
        year = 2023
        
        source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True,
            priority=1,
            reliability_score=0.95,
            health_status="healthy"
        )
        
        expected_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        # Mock successful fetch
        with patch.object(self.source_manager, 'get_best_source', return_value=source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=expected_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True):
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.error_message is None
            assert result.data is not None
            assert result.source is not None
            assert result.session_id is not None
            assert result.fetch_duration > 0
    
    def test_one_click_tufe_fetching_error_handling(self):
        """Test one-click TÜFE fetching error handling and user feedback."""
        # Arrange
        year = 2023
        
        # Mock all sources failing
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=[]):
            
            # Act & Assert
            with pytest.raises(Exception, match="No sources available"):
                self.fetch_service.fetch_tufe_easy(year)
    
    def test_one_click_tufe_fetching_source_attribution(self):
        """Test that one-click TÜFE fetching maintains proper source attribution."""
        # Arrange
        year = 2023
        
        source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True,
            priority=1,
            reliability_score=0.95,
            health_status="healthy"
        )
        
        expected_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        # Mock successful fetch
        with patch.object(self.source_manager, 'get_best_source', return_value=source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=expected_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True):
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.data.source == "TCMB EVDS API"
            assert result.source.source_name == "TCMB EVDS API"
            assert result.data.is_validated is True
