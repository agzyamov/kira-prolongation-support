"""
Integration tests for data validation.
Tests comprehensive TÜFE data validation with quality scoring and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.utils.tufe_validator import TufeValidator
from src.services.tufe_fetch_service import TufeFetchService
from src.services.tufe_source_manager import TufeSourceManager
from src.models.validation_result import ValidationResult
from src.models.tufe_data import TufeData
from src.models.tufe_data_source import TufeDataSource
from src.services.exceptions import ValidationError


class TestDataValidation:
    """Test data validation integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TufeValidator()
        self.test_data_store = Mock()
        self.source_manager = TufeSourceManager(self.test_data_store)
        self.fetch_service = TufeFetchService(self.test_data_store, self.source_manager)
    
    def test_data_validation_success_high_quality(self):
        """Test successful data validation with high quality data."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=False
        )
        
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
        
        # Act
        result = self.validator.validate_tufe_data(data, source)
        
        # Assert
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.quality_score > 0.8  # High quality
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert "source_attribution" in result.validation_details
        assert "data_freshness" in result.validation_details
        assert "rate_reasonableness" in result.validation_details
    
    def test_data_validation_invalid_rate(self):
        """Test data validation with invalid TÜFE rate."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=200.0,  # Invalid rate (too high)
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=False
        )
        
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
        
        # Act & Assert
        with pytest.raises(ValidationError, match="TÜFE data validation failed"):
            self.validator.validate_tufe_data(data, source)
    
    def test_data_validation_source_attribution_mismatch(self):
        """Test data validation with source attribution mismatch."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TÜİK API",  # Different source
            fetched_at=datetime.now(),
            is_validated=False
        )
        
        source = TufeDataSource(
            id=1,
            source_name="TCMB EVDS API",  # Different source name
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
        
        # Act
        result = self.validator.validate_tufe_data(data, source)
        
        # Assert
        assert result.valid is False
        assert result.quality_score < 0.5  # Low quality due to attribution mismatch
        assert len(result.errors) > 0
        assert any("attribution" in error.lower() for error in result.errors)
    
    def test_data_validation_stale_data(self):
        """Test data validation with stale data."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now() - timedelta(days=2),  # 2 days ago
            is_validated=False
        )
        
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
        
        # Act
        result = self.validator.validate_tufe_data(data, source)
        
        # Assert
        assert result.valid is False
        assert result.quality_score < 0.5  # Low quality due to stale data
        assert len(result.errors) > 0
        assert any("fresh" in error.lower() or "stale" in error.lower() for error in result.errors)
    
    def test_data_validation_with_warnings(self):
        """Test data validation that produces warnings but is still valid."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now() - timedelta(hours=25),  # Slightly stale
            is_validated=False
        )
        
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
        
        # Act
        result = self.validator.validate_tufe_data(data, source)
        
        # Assert
        assert result.valid is True  # Still valid
        assert result.quality_score < 1.0  # But lower quality
        assert len(result.warnings) > 0  # Has warnings
        assert len(result.errors) == 0  # No errors
        assert any("fresh" in warning.lower() for warning in result.warnings)
    
    def test_data_validation_quality_score_calculation(self):
        """Test data quality score calculation."""
        # Arrange
        high_quality_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        low_quality_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=150.0,  # Invalid rate
            source="Unknown Source",  # Unknown source
            fetched_at=datetime.now() - timedelta(days=30),  # Stale data
            is_validated=False
        )
        
        # Act
        high_quality_score = self.validator.get_data_quality_score(high_quality_data)
        low_quality_score = self.validator.get_data_quality_score(low_quality_data)
        
        # Assert
        assert high_quality_score > 0.8  # High quality
        assert low_quality_score < 0.5  # Low quality
        assert high_quality_score > low_quality_score
        assert 0.0 <= high_quality_score <= 1.0
        assert 0.0 <= low_quality_score <= 1.0
    
    def test_data_validation_rate_reasonableness(self):
        """Test rate reasonableness validation."""
        # Arrange
        reasonable_rate = 64.27
        unreasonable_high_rate = 200.0
        unreasonable_low_rate = 5.0
        year = 2023
        
        # Act
        reasonable_result = self.validator.validate_rate_reasonableness(reasonable_rate, year)
        high_rate_result = self.validator.validate_rate_reasonableness(unreasonable_high_rate, year)
        low_rate_result = self.validator.validate_rate_reasonableness(unreasonable_low_rate, year)
        
        # Assert
        assert reasonable_result is True
        assert high_rate_result is False
        assert low_rate_result is False
    
    def test_data_validation_integration_with_fetch_service(self):
        """Test data validation integration with fetch service."""
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
        
        valid_data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        # Mock successful fetch with validation
        with patch.object(self.source_manager, 'get_best_source', return_value=source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=valid_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True):
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.data.is_validated is True
    
    def test_data_validation_integration_with_fetch_service_validation_failure(self):
        """Test data validation integration when validation fails."""
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
        
        # Mock fetch success but validation failure
        with patch.object(self.source_manager, 'get_best_source', return_value=source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=invalid_data), \
             patch.object(self.fetch_service, '_validate_data', return_value=False), \
             patch.object(self.source_manager, 'mark_source_failed') as mock_mark_failed:
            
            # Act & Assert
            with pytest.raises(Exception, match="Data validation failed"):
                self.fetch_service.fetch_tufe_easy(year)
            
            mock_mark_failed.assert_called_once()
    
    def test_data_validation_performance_requirement(self):
        """Test that data validation meets performance requirements."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=False
        )
        
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
        
        # Act
        start_time = datetime.now()
        result = self.validator.validate_tufe_data(data, source)
        end_time = datetime.now()
        
        # Assert
        duration_ms = (end_time - start_time).total_seconds() * 1000
        assert duration_ms < 100  # Should be very fast
        assert result.valid is True
    
    def test_data_validation_comprehensive_checks(self):
        """Test comprehensive data validation checks."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=False
        )
        
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
        
        # Act
        result = self.validator.validate_tufe_data(data, source)
        
        # Assert
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.quality_score > 0.0
        assert "validation_details" in result.validation_details
        assert "source_attribution" in result.validation_details
        assert "data_freshness" in result.validation_details
        assert "rate_reasonableness" in result.validation_details
        assert "format_validation" in result.validation_details
        assert "historical_comparison" in result.validation_details
    
    def test_data_validation_error_messages_are_descriptive(self):
        """Test that validation error messages are descriptive and actionable."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=200.0,  # Invalid rate
            source="Unknown Source",  # Unknown source
            fetched_at=datetime.now() - timedelta(days=30),  # Stale data
            is_validated=False
        )
        
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
        
        # Act
        result = self.validator.validate_tufe_data(data, source)
        
        # Assert
        assert result.valid is False
        assert len(result.errors) > 0
        
        # Check that error messages are descriptive
        error_messages = " ".join(result.errors).lower()
        assert "rate" in error_messages or "inflation" in error_messages
        assert "source" in error_messages or "attribution" in error_messages
        assert "fresh" in error_messages or "stale" in error_messages or "date" in error_messages
    
    def test_data_validation_warning_messages_are_helpful(self):
        """Test that validation warning messages are helpful."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now() - timedelta(hours=25),  # Slightly stale
            is_validated=False
        )
        
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
        
        # Act
        result = self.validator.validate_tufe_data(data, source)
        
        # Assert
        assert result.valid is True
        assert len(result.warnings) > 0
        
        # Check that warning messages are helpful
        warning_messages = " ".join(result.warnings).lower()
        assert "fresh" in warning_messages or "stale" in warning_messages or "date" in warning_messages
