"""
Contract tests for TufeValidator.
Tests the service interface and expected behavior for TÜFE data validation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.utils.tufe_validator import TufeValidator
from src.services.exceptions import ValidationError
from src.models.validation_result import ValidationResult
from src.models.tufe_data import TufeData
from src.models.tufe_data_source import TufeDataSource


class TestTufeValidator:
    """Test TufeValidator contract and interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TufeValidator()
    
    def test_validate_tufe_data_success(self):
        """Test successful TÜFE data validation."""
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
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_tufe_data_invalid_rate(self):
        """Test validation with invalid TÜFE rate."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=150.0,  # Invalid rate (too high)
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
        assert result.valid is False
        assert result.quality_score < 1.0
        assert len(result.errors) > 0
        assert any("rate" in error.lower() for error in result.errors)
    
    def test_validate_tufe_data_negative_rate(self):
        """Test validation with negative TÜFE rate."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=-5.0,  # Invalid rate (negative)
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
        assert result.valid is False
        assert result.quality_score < 1.0
        assert len(result.errors) > 0
        assert any("negative" in error.lower() or "rate" in error.lower() for error in result.errors)
    
    def test_validate_source_attribution_success(self):
        """Test successful source attribution validation."""
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
        result = self.validator.validate_source_attribution(data, source)
        
        # Assert
        assert result is True
    
    def test_validate_source_attribution_mismatch(self):
        """Test source attribution validation with mismatched source."""
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
        result = self.validator.validate_source_attribution(data, source)
        
        # Assert
        assert result is False
    
    def test_validate_data_freshness_success(self):
        """Test successful data freshness validation."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now() - timedelta(hours=1),  # 1 hour ago
            is_validated=False
        )
        
        # Act
        result = self.validator.validate_data_freshness(data)
        
        # Assert
        assert result is True
    
    def test_validate_data_freshness_stale(self):
        """Test data freshness validation with stale data."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now() - timedelta(days=2),  # 2 days ago
            is_validated=False
        )
        
        # Act
        result = self.validator.validate_data_freshness(data)
        
        # Assert
        assert result is False
    
    def test_validate_rate_reasonableness_success(self):
        """Test successful rate reasonableness validation."""
        # Arrange
        rate = 64.27
        year = 2023
        
        # Act
        result = self.validator.validate_rate_reasonableness(rate, year)
        
        # Assert
        assert result is True
    
    def test_validate_rate_reasonableness_unreasonable(self):
        """Test rate reasonableness validation with unreasonable rate."""
        # Arrange
        rate = 200.0  # Unreasonably high rate
        year = 2023
        
        # Act
        result = self.validator.validate_rate_reasonableness(rate, year)
        
        # Assert
        assert result is False
    
    def test_validate_rate_reasonableness_historical_comparison(self):
        """Test rate reasonableness with historical comparison."""
        # Arrange
        rate = 5.0  # Very low rate for 2023
        year = 2023
        
        # Act
        result = self.validator.validate_rate_reasonableness(rate, year)
        
        # Assert
        assert result is False  # Should be unreasonable compared to historical data
    
    def test_get_data_quality_score_high_quality(self):
        """Test getting high quality score for good data."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=64.27,
            source="TCMB EVDS API",
            fetched_at=datetime.now(),
            is_validated=True
        )
        
        # Act
        result = self.validator.get_data_quality_score(data)
        
        # Assert
        assert result > 0.8  # High quality score
        assert result <= 1.0  # Maximum quality score
    
    def test_get_data_quality_score_low_quality(self):
        """Test getting low quality score for poor data."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=150.0,  # Invalid rate
            source="Unknown Source",  # Unknown source
            fetched_at=datetime.now() - timedelta(days=30),  # Stale data
            is_validated=False
        )
        
        # Act
        result = self.validator.get_data_quality_score(data)
        
        # Assert
        assert result < 0.5  # Low quality score
        assert result >= 0.0  # Minimum quality score
    
    def test_validate_tufe_data_with_warnings(self):
        """Test validation that produces warnings but is still valid."""
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
    
    def test_validate_tufe_data_comprehensive_validation(self):
        """Test comprehensive validation with multiple checks."""
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
    
    def test_validate_tufe_data_validation_error_exception(self):
        """Test that validation errors raise ValidationError exception."""
        # Arrange
        data = TufeData(
            year=2023,
            month=12,
            inflation_rate_percent=200.0,  # Invalid rate
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
    
    def test_validate_tufe_data_performance_requirement(self):
        """Test that validation meets performance requirements."""
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
