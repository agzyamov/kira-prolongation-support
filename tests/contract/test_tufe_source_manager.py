"""
Contract tests for TufeSourceManager.
Tests the service interface and expected behavior for source management and health monitoring.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.tufe_source_manager import TufeSourceManager
from src.services.exceptions import SourceNotFoundError
from src.models.tufe_data_source import TufeDataSource


class TestTufeSourceManager:
    """Test TufeSourceManager contract and interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_data_store = Mock()
        self.service = TufeSourceManager(self.mock_data_store)
    
    def test_get_best_source_success(self):
        """Test getting the best available source."""
        # Arrange
        year = 2023
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
            health_status="healthy",
            failure_count=0,
            success_count=10,
            avg_response_time=500.0,
            rate_limit_remaining=1000
        )
        
        with patch.object(self.service, '_get_healthy_sources') as mock_healthy:
            mock_healthy.return_value = [expected_source]
            
            # Act
            result = self.service.get_best_source(year)
            
            # Assert
            assert result is not None
            assert result.id == 1
            assert result.source_name == "TCMB EVDS API"
            assert result.health_status == "healthy"
            mock_healthy.assert_called_once()
    
    def test_get_best_source_no_sources_available(self):
        """Test getting best source when no sources are available."""
        # Arrange
        year = 2023
        
        with patch.object(self.service, '_get_healthy_sources') as mock_healthy:
            mock_healthy.return_value = []
            
            # Act
            result = self.service.get_best_source(year)
            
            # Assert
            assert result is None
            mock_healthy.assert_called_once()
    
    def test_get_source_priority_order(self):
        """Test getting sources ordered by priority and reliability."""
        # Arrange
        sources = [
            TufeDataSource(id=1, source_name="TCMB", priority=1, reliability_score=0.95, health_status="healthy"),
            TufeDataSource(id=2, source_name="TÜİK", priority=2, reliability_score=0.90, health_status="healthy"),
            TufeDataSource(id=3, source_name="EPİAŞ", priority=3, reliability_score=0.85, health_status="degraded")
        ]
        
        self.mock_data_store.get_all_tufe_data_sources.return_value = sources
        
        # Act
        result = self.service.get_source_priority_order()
        
        # Assert
        assert len(result) == 3
        assert result[0].id == 1  # Highest priority
        assert result[1].id == 2
        assert result[2].id == 3  # Lowest priority
        self.mock_data_store.get_all_tufe_data_sources.assert_called_once()
    
    def test_update_source_health_success(self):
        """Test updating source health status successfully."""
        # Arrange
        source_id = 1
        is_healthy = True
        response_time = 500.0
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = Mock()
        self.mock_data_store.update_tufe_data_source.return_value = True
        
        # Act
        self.service.update_source_health(source_id, is_healthy, response_time)
        
        # Assert
        self.mock_data_store.get_tufe_data_source_by_id.assert_called_once_with(source_id)
        self.mock_data_store.update_tufe_data_source.assert_called_once()
    
    def test_update_source_health_source_not_found(self):
        """Test updating health for non-existent source."""
        # Arrange
        source_id = 999
        is_healthy = True
        response_time = 500.0
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(SourceNotFoundError, match="Source 999 not found"):
            self.service.update_source_health(source_id, is_healthy, response_time)
    
    def test_mark_source_failed_success(self):
        """Test marking a source as failed successfully."""
        # Arrange
        source_id = 1
        error_message = "Connection timeout"
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = Mock()
        self.mock_data_store.update_tufe_data_source.return_value = True
        
        # Act
        self.service.mark_source_failed(source_id, error_message)
        
        # Assert
        self.mock_data_store.get_tufe_data_source_by_id.assert_called_once_with(source_id)
        self.mock_data_store.update_tufe_data_source.assert_called_once()
    
    def test_mark_source_failed_source_not_found(self):
        """Test marking non-existent source as failed."""
        # Arrange
        source_id = 999
        error_message = "Connection timeout"
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(SourceNotFoundError, match="Source 999 not found"):
            self.service.mark_source_failed(source_id, error_message)
    
    def test_mark_source_success_success(self):
        """Test marking a source as successful."""
        # Arrange
        source_id = 1
        response_time = 300.0
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = Mock()
        self.mock_data_store.update_tufe_data_source.return_value = True
        
        # Act
        self.service.mark_source_success(source_id, response_time)
        
        # Assert
        self.mock_data_store.get_tufe_data_source_by_id.assert_called_once_with(source_id)
        self.mock_data_store.update_tufe_data_source.assert_called_once()
    
    def test_mark_source_success_source_not_found(self):
        """Test marking non-existent source as successful."""
        # Arrange
        source_id = 999
        response_time = 300.0
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(SourceNotFoundError, match="Source 999 not found"):
            self.service.mark_source_success(source_id, response_time)
    
    def test_get_source_reliability_score_success(self):
        """Test getting source reliability score."""
        # Arrange
        source_id = 1
        expected_score = 0.95
        
        source = Mock()
        source.reliability_score = expected_score
        self.mock_data_store.get_tufe_data_source_by_id.return_value = source
        
        # Act
        result = self.service.get_source_reliability_score(source_id)
        
        # Assert
        assert result == expected_score
        self.mock_data_store.get_tufe_data_source_by_id.assert_called_once_with(source_id)
    
    def test_get_source_reliability_score_source_not_found(self):
        """Test getting reliability score for non-existent source."""
        # Arrange
        source_id = 999
        self.mock_data_store.get_tufe_data_source_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(SourceNotFoundError, match="Source 999 not found"):
            self.service.get_source_reliability_score(source_id)
    
    def test_run_health_checks_success(self):
        """Test running health checks on all active sources."""
        # Arrange
        sources = [
            Mock(id=1, api_endpoint="https://api1.com", health_status="healthy"),
            Mock(id=2, api_endpoint="https://api2.com", health_status="degraded"),
            Mock(id=3, api_endpoint="https://api3.com", health_status="failed")
        ]
        
        self.mock_data_store.get_active_tufe_data_sources.return_value = sources
        
        with patch.object(self.service, '_check_source_health') as mock_check:
            mock_check.side_effect = [True, False, False]  # Health check results
            
            # Act
            result = self.service.run_health_checks()
            
            # Assert
            assert result == {1: True, 2: False, 3: False}
            assert mock_check.call_count == 3
            self.mock_data_store.get_active_tufe_data_sources.assert_called_once()
    
    def test_run_health_checks_performance_requirement(self):
        """Test that health checks meet performance requirement (<500ms per source)."""
        # Arrange
        sources = [Mock(id=1, api_endpoint="https://api1.com")]
        self.mock_data_store.get_active_tufe_data_sources.return_value = sources
        
        with patch.object(self.service, '_check_source_health') as mock_check:
            mock_check.return_value = True
            
            # Act
            start_time = datetime.now()
            result = self.service.run_health_checks()
            end_time = datetime.now()
            
            # Assert
            duration_ms = (end_time - start_time).total_seconds() * 1000
            assert duration_ms < 500  # Should be fast
            assert result == {1: True}
    
    def test_source_health_status_transitions(self):
        """Test that source health status transitions work correctly."""
        # Arrange
        source_id = 1
        source = Mock()
        source.health_status = "unknown"
        source.failure_count = 0
        source.success_count = 0
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = source
        self.mock_data_store.update_tufe_data_source.return_value = True
        
        # Act - First successful health check
        self.service.update_source_health(source_id, True, 500.0)
        
        # Assert - Should transition from unknown to healthy
        update_call = self.mock_data_store.update_tufe_data_source.call_args
        updated_source = update_call[0][0]
        assert updated_source.health_status == "healthy"
        assert updated_source.success_count == 1
        assert updated_source.failure_count == 0
    
    def test_source_reliability_score_calculation(self):
        """Test that reliability scores are calculated correctly."""
        # Arrange
        source_id = 1
        source = Mock()
        source.success_count = 8
        source.failure_count = 2
        source.reliability_score = 0.5  # Initial score
        
        self.mock_data_store.get_tufe_data_source_by_id.return_value = source
        self.mock_data_store.update_tufe_data_source.return_value = True
        
        # Act - Mark another success
        self.service.mark_source_success(source_id, 400.0)
        
        # Assert - Reliability score should be updated
        update_call = self.mock_data_store.update_tufe_data_source.call_args
        updated_source = update_call[0][0]
        expected_score = 9 / (9 + 2)  # 9 successes out of 11 total attempts
        assert abs(updated_source.reliability_score - expected_score) < 0.01
    
    def test_source_priority_ordering(self):
        """Test that sources are ordered by priority correctly."""
        # Arrange
        sources = [
            TufeDataSource(id=3, source_name="Low Priority", priority=5, reliability_score=0.99, health_status="healthy"),
            TufeDataSource(id=1, source_name="High Priority", priority=1, reliability_score=0.80, health_status="healthy"),
            TufeDataSource(id=2, source_name="Medium Priority", priority=3, reliability_score=0.90, health_status="healthy")
        ]
        
        self.mock_data_store.get_all_tufe_data_sources.return_value = sources
        
        # Act
        result = self.service.get_source_priority_order()
        
        # Assert - Should be ordered by priority (lower number = higher priority)
        assert result[0].id == 1  # Priority 1
        assert result[1].id == 2  # Priority 3
        assert result[2].id == 3  # Priority 5
