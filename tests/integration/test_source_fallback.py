"""
Integration tests for source fallback mechanism.
Tests automatic source switching when primary sources fail.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.tufe_fetch_service import TufeFetchService
from src.services.tufe_source_manager import TufeSourceManager
from src.models.tufe_fetch_result import TufeFetchResult
from src.models.tufe_data import TufeData
from src.models.tufe_data_source import TufeDataSource


class TestSourceFallback:
    """Test source fallback integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data_store = Mock()
        self.source_manager = TufeSourceManager(self.test_data_store)
        self.fetch_service = TufeFetchService(self.test_data_store, self.source_manager)
    
    def test_source_fallback_primary_fails_backup_succeeds(self):
        """Test fallback when primary source fails but backup succeeds."""
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
        
        # Mock primary failure, backup success
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=[primary_source, backup_source]), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=[Exception("Connection timeout"), expected_data]), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed, \
             patch.object(self.source_manager, 'mark_source_success') as mock_mark_success:
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.data.source == "TÜİK API"
            assert len(result.attempts) == 2
            assert result.attempts[0].success is False
            assert result.attempts[0].error_message == "Connection timeout"
            assert result.attempts[1].success is True
            assert result.attempts[1].error_message is None
            
            # Verify source status updates
            mock_mark_failed.assert_called_once_with(1, "Connection timeout")
            mock_mark_success.assert_called_once()
    
    def test_source_fallback_all_sources_fail(self):
        """Test fallback when all sources fail."""
        # Arrange
        year = 2023
        
        sources = [
            TufeDataSource(id=1, source_name="TCMB", priority=1, health_status="healthy"),
            TufeDataSource(id=2, source_name="TÜİK", priority=2, health_status="healthy"),
            TufeDataSource(id=3, source_name="EPİAŞ", priority=3, health_status="healthy")
        ]
        
        # Mock all sources failing
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=sources), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=Exception("All sources failed")), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed:
            
            # Act & Assert
            with pytest.raises(Exception, match="All sources failed"):
                self.fetch_service.fetch_tufe_easy(year)
            
            # Verify all sources were marked as failed
            assert mock_mark_failed.call_count == 3
    
    def test_source_fallback_health_status_updates(self):
        """Test that source health status is updated during fallback."""
        # Arrange
        year = 2023
        
        healthy_source = TufeDataSource(
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
        
        degraded_source = TufeDataSource(
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
            health_status="degraded"
        )
        
        expected_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TÜİK API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        # Mock primary failure, degraded source success
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=[healthy_source, degraded_source]), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=[Exception("Rate limit exceeded"), expected_data]), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed, \
             patch.object(self.source_manager, 'mark_source_success') as mock_mark_success, \
             patch.object(self.source_manager, 'update_source_health') as mock_update_health:
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.data.source == "TÜİK API"
            
            # Verify health status updates
            mock_mark_failed.assert_called_once_with(1, "Rate limit exceeded")
            mock_mark_success.assert_called_once()
            mock_update_health.assert_called()
    
    def test_source_fallback_reliability_score_updates(self):
        """Test that source reliability scores are updated during fallback."""
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
            health_status="healthy",
            failure_count=0,
            success_count=10
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
             patch.object(self.fetch_service, '_cache_data', return_value=True), \
             patch.object(self.source_manager, 'mark_source_success') as mock_mark_success:
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            mock_mark_success.assert_called_once()
            
            # Verify reliability score would be updated (success count increased)
            call_args = mock_mark_success.call_args
            assert call_args[0][0] == 1  # source_id
            assert call_args[0][1] > 0  # response_time
    
    def test_source_fallback_performance_requirement(self):
        """Test that source fallback meets performance requirements."""
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
        
        # Mock primary failure, backup success
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=[primary_source, backup_source]), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=[Exception("Timeout"), expected_data]), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True), \
             patch.object(self.source_manager, 'mark_source_failed'), \
             patch.object(self.source_manager, 'mark_source_success'):
            
            # Act
            start_time = datetime.now()
            result = self.fetch_service.fetch_tufe_easy(year)
            end_time = datetime.now()
            
            # Assert
            total_duration = (end_time - start_time).total_seconds()
            assert total_duration < 5.0  # Fallback should complete within 5 seconds
            assert result.success is True
            assert result.fetch_duration < 5.0
    
    def test_source_fallback_priority_order_respected(self):
        """Test that source fallback respects priority order."""
        # Arrange
        year = 2023
        
        high_priority_source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            priority=1,
            reliability_score=0.95,
            health_status="healthy"
        )
        
        medium_priority_source = TufeDataSource(
            id=2,
            source_name="TÜİK API",
            priority=2,
            reliability_score=0.90,
            health_status="healthy"
        )
        
        low_priority_source = TufeDataSource(
            id=3,
            source_name="EPİAŞ API",
            priority=3,
            reliability_score=0.85,
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
        
        # Mock first two sources fail, third succeeds
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=[high_priority_source, medium_priority_source, low_priority_source]), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=[Exception("Failed"), Exception("Failed"), expected_data]), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed, \
             patch.object(self.source_manager, 'mark_source_success') as mock_mark_success:
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.data.source == "EPİAŞ API"
            assert len(result.attempts) == 3
            
            # Verify attempts were made in priority order
            assert result.attempts[0].source_id == 1  # Highest priority first
            assert result.attempts[1].source_id == 2  # Medium priority second
            assert result.attempts[2].source_id == 3  # Lowest priority third
            
            # Verify all failures were marked
            assert mock_mark_failed.call_count == 2
            assert mock_mark_success.call_count == 1
    
    def test_source_fallback_health_check_integration(self):
        """Test that source fallback integrates with health check system."""
        # Arrange
        year = 2023
        
        unhealthy_source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",
            priority=1,
            reliability_score=0.95,
            health_status="failed"  # Marked as failed
        )
        
        healthy_source = TufeDataSource(
            id=2,
            source_name="TÜİK API",
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
        
        # Mock unhealthy source skipped, healthy source succeeds
        with patch.object(self.source_manager, 'get_healthy_sources', return_value=[healthy_source]), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=expected_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True), \
             patch.object(self.source_manager, 'mark_source_success') as mock_mark_success:
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.data.source == "TÜİK API"
            assert len(result.attempts) == 1  # Only healthy source attempted
            assert result.attempts[0].source_id == 2
            mock_mark_success.assert_called_once()
    
    def test_source_fallback_error_propagation(self):
        """Test that source fallback properly propagates errors."""
        # Arrange
        year = 2023
        
        sources = [
            TufeDataSource(id=1, source_name="TCMB", priority=1, health_status="healthy"),
            TufeDataSource(id=2, source_name="TÜİK", priority=2, health_status="healthy")
        ]
        
        # Mock all sources failing with different errors
        with patch.object(self.source_manager, 'get_source_priority_order', return_value=sources), \
             patch.object(self.fetch_service, '_fetch_from_source', side_effect=[Exception("Connection timeout"), Exception("Authentication failed")]), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed:
            
            # Act & Assert
            with pytest.raises(Exception, match="All sources failed"):
                self.fetch_service.fetch_tufe_easy(year)
            
            # Verify each source was marked with its specific error
            assert mock_mark_failed.call_count == 2
            call_args_list = mock_mark_failed.call_args_list
            assert "Connection timeout" in str(call_args_list[0])
            assert "Authentication failed" in str(call_args_list[1])
