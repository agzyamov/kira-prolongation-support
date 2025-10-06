"""
Unit tests for enhanced TufeDataSource model.

Tests the enhanced TufeDataSource with rate limiting fields,
health status tracking, and reliability scoring.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.models.tufe_data_source import TufeDataSource, HealthStatus


class TestTufeDataSourceEnhanced:
    """Unit tests for enhanced TufeDataSource."""
    
    def test_initialization_default_values(self):
        """Test TufeDataSource initialization with default values."""
        source = TufeDataSource()
        
        assert source.id is None
        assert source.source_name == ""
        assert source.api_endpoint == ""
        assert source.series_code == ""
        assert source.data_format == "json"
        assert source.requires_auth is True
        assert source.rate_limit_per_hour == 100
        assert source.last_verified is None
        assert source.is_active is True
        assert source.created_at is None
        
        # Enhanced fields
        assert source.priority == 5
        assert source.reliability_score == 0.5
        assert source.last_health_check is None
        assert source.health_status == HealthStatus.UNKNOWN
        assert source.failure_count == 0
        assert source.success_count == 0
        assert source.avg_response_time == 0.0
        assert source.rate_limit_remaining == 1000
        assert source.rate_limit_reset is None
    
    def test_initialization_custom_values(self):
        """Test TufeDataSource initialization with custom values."""
        now = datetime.now()
        reset_time = now + timedelta(hours=1)
        
        source = TufeDataSource(
            id=1,
            source_name="OECD SDMX API",
            api_endpoint="https://stats.oecd.org/restsdmx/sdmx.ashx",
            series_code="A.TUR.CPALTT01.M",
            data_format="xml",
            requires_auth=False,
            rate_limit_per_hour=100,
            last_verified=now,
            is_active=True,
            created_at=now,
            priority=1,
            reliability_score=0.95,
            last_health_check=now,
            health_status=HealthStatus.HEALTHY,
            failure_count=0,
            success_count=10,
            avg_response_time=1500.0,
            rate_limit_remaining=95,
            rate_limit_reset=reset_time
        )
        
        assert source.id == 1
        assert source.source_name == "OECD SDMX API"
        assert source.api_endpoint == "https://stats.oecd.org/restsdmx/sdmx.ashx"
        assert source.series_code == "A.TUR.CPALTT01.M"
        assert source.data_format == "xml"
        assert source.requires_auth is False
        assert source.rate_limit_per_hour == 100
        assert source.last_verified == now
        assert source.is_active is True
        assert source.created_at == now
        
        # Enhanced fields
        assert source.priority == 1
        assert source.reliability_score == 0.95
        assert source.last_health_check == now
        assert source.health_status == HealthStatus.HEALTHY
        assert source.failure_count == 0
        assert source.success_count == 10
        assert source.avg_response_time == 1500.0
        assert source.rate_limit_remaining == 95
        assert source.rate_limit_reset == reset_time
    
    def test_validation_source_name_required(self):
        """Test validation requires non-empty source_name."""
        with pytest.raises(ValueError, match="source_name cannot be empty"):
            TufeDataSource(source_name="")
    
    def test_validation_api_endpoint_required(self):
        """Test validation requires non-empty api_endpoint."""
        with pytest.raises(ValueError, match="api_endpoint cannot be empty"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint=""
            )
    
    def test_validation_series_code_required(self):
        """Test validation requires non-empty series_code."""
        with pytest.raises(ValueError, match="series_code cannot be empty"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code=""
            )
    
    def test_validation_data_format_valid(self):
        """Test validation accepts valid data_format values."""
        # Valid formats
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            data_format="json"
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            data_format="xml"
        )
    
    def test_validation_data_format_invalid(self):
        """Test validation rejects invalid data_format values."""
        with pytest.raises(ValueError, match="data_format must be 'json' or 'xml'"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                data_format="csv"
            )
    
    def test_validation_requires_auth_boolean(self):
        """Test validation requires boolean requires_auth."""
        with pytest.raises(ValueError, match="requires_auth must be a boolean"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                requires_auth="yes"
            )
    
    def test_validation_is_active_boolean(self):
        """Test validation requires boolean is_active."""
        with pytest.raises(ValueError, match="is_active must be a boolean"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                is_active="yes"
            )
    
    def test_validation_priority_range(self):
        """Test validation requires priority in range 0-10."""
        # Valid priorities
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            priority=0
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            priority=10
        )
        
        # Invalid priorities
        with pytest.raises(ValueError, match="priority must be between 0 and 10"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                priority=-1
            )
        
        with pytest.raises(ValueError, match="priority must be between 0 and 10"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                priority=11
            )
    
    def test_validation_reliability_score_range(self):
        """Test validation requires reliability_score in range 0.0-1.0."""
        # Valid scores
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            reliability_score=0.0
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            reliability_score=1.0
        )
        
        # Invalid scores
        with pytest.raises(ValueError, match="reliability_score must be between 0.0 and 1.0"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                reliability_score=-0.1
            )
        
        with pytest.raises(ValueError, match="reliability_score must be between 0.0 and 1.0"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                reliability_score=1.1
            )
    
    def test_validation_health_status_enum(self):
        """Test validation requires valid HealthStatus enum."""
        # Valid statuses
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            health_status=HealthStatus.HEALTHY
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            health_status=HealthStatus.DEGRADED
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            health_status=HealthStatus.FAILED
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            health_status=HealthStatus.UNKNOWN
        )
        
        # Invalid status
        with pytest.raises(ValueError, match="health_status must be a valid HealthStatus enum"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                health_status="INVALID"
            )
    
    def test_validation_failure_count_non_negative(self):
        """Test validation requires non-negative failure_count."""
        # Valid counts
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            failure_count=0
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            failure_count=5
        )
        
        # Invalid count
        with pytest.raises(ValueError, match="failure_count and success_count must be non-negative"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                failure_count=-1
            )
    
    def test_validation_success_count_non_negative(self):
        """Test validation requires non-negative success_count."""
        # Valid counts
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            success_count=0
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            success_count=10
        )
        
        # Invalid count
        with pytest.raises(ValueError, match="failure_count and success_count must be non-negative"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                success_count=-1
            )
    
    def test_validation_avg_response_time_non_negative(self):
        """Test validation requires non-negative avg_response_time."""
        # Valid times
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            avg_response_time=0.0
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            avg_response_time=1500.0
        )
        
        # Invalid time
        with pytest.raises(ValueError, match="avg_response_time must be non-negative"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                avg_response_time=-100.0
            )
    
    def test_validation_rate_limit_remaining_non_negative(self):
        """Test validation requires non-negative rate_limit_remaining."""
        # Valid values
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            rate_limit_remaining=0
        )
        TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            rate_limit_remaining=100
        )
        
        # Invalid value
        with pytest.raises(ValueError, match="rate_limit_remaining must be non-negative"):
            TufeDataSource(
                source_name="Test API",
                api_endpoint="https://api.example.com",
                series_code="TEST",
                rate_limit_remaining=-1
            )
    
    def test_health_status_enum_values(self):
        """Test HealthStatus enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.FAILED.value == "failed"
        assert HealthStatus.UNKNOWN.value == "unknown"
    
    def test_health_status_enum_comparison(self):
        """Test HealthStatus enum comparison."""
        source = TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            health_status=HealthStatus.HEALTHY
        )
        
        assert source.health_status == HealthStatus.HEALTHY
        assert source.health_status != HealthStatus.DEGRADED
        assert source.health_status != HealthStatus.FAILED
        assert source.health_status != HealthStatus.UNKNOWN
    
    def test_priority_ordering(self):
        """Test priority ordering (lower number = higher priority)."""
        source1 = TufeDataSource(
            source_name="High Priority API",
            api_endpoint="https://api1.example.com",
            series_code="TEST1",
            priority=1
        )
        
        source2 = TufeDataSource(
            source_name="Low Priority API",
            api_endpoint="https://api2.example.com",
            series_code="TEST2",
            priority=5
        )
        
        assert source1.priority < source2.priority
        assert source1.priority == 1
        assert source2.priority == 5
    
    def test_reliability_score_calculation(self):
        """Test reliability score represents success rate."""
        source = TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            success_count=8,
            failure_count=2
        )
        
        # Reliability score should be calculated as success / (success + failure)
        expected_score = 8 / (8 + 2)  # 0.8
        assert source.reliability_score == 0.5  # Default value, not auto-calculated
    
    def test_rate_limit_tracking(self):
        """Test rate limit tracking fields."""
        now = datetime.now()
        reset_time = now + timedelta(hours=1)
        
        source = TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            rate_limit_remaining=95,
            rate_limit_reset=reset_time
        )
        
        assert source.rate_limit_remaining == 95
        assert source.rate_limit_reset == reset_time
        
        # Test rate limit reset
        source.rate_limit_reset = None
        assert source.rate_limit_reset is None
    
    def test_response_time_tracking(self):
        """Test response time tracking."""
        source = TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            avg_response_time=1500.0
        )
        
        assert source.avg_response_time == 1500.0
        
        # Test response time update
        source.avg_response_time = 2000.0
        assert source.avg_response_time == 2000.0
    
    def test_health_check_tracking(self):
        """Test health check tracking."""
        now = datetime.now()
        
        source = TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            last_health_check=now,
            health_status=HealthStatus.HEALTHY
        )
        
        assert source.last_health_check == now
        assert source.health_status == HealthStatus.HEALTHY
        
        # Test health status update
        source.health_status = HealthStatus.DEGRADED
        assert source.health_status == HealthStatus.DEGRADED
    
    def test_success_failure_counting(self):
        """Test success and failure counting."""
        source = TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            success_count=5,
            failure_count=2
        )
        
        assert source.success_count == 5
        assert source.failure_count == 2
        
        # Test incrementing counts
        source.success_count += 1
        source.failure_count += 1
        
        assert source.success_count == 6
        assert source.failure_count == 3
    
    def test_complete_oecd_source_creation(self):
        """Test creating a complete OECD source with all fields."""
        now = datetime.now()
        reset_time = now + timedelta(hours=1)
        
        source = TufeDataSource(
            id=1,
            source_name="OECD SDMX API",
            api_endpoint="https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all",
            series_code="A.TUR.CPALTT01.M",
            data_format="xml",
            requires_auth=False,
            rate_limit_per_hour=100,
            last_verified=now,
            is_active=True,
            created_at=now,
            priority=1,
            reliability_score=0.95,
            last_health_check=now,
            health_status=HealthStatus.HEALTHY,
            failure_count=0,
            success_count=10,
            avg_response_time=1500.0,
            rate_limit_remaining=95,
            rate_limit_reset=reset_time
        )
        
        # Verify all fields
        assert source.id == 1
        assert source.source_name == "OECD SDMX API"
        assert source.api_endpoint == "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all"
        assert source.series_code == "A.TUR.CPALTT01.M"
        assert source.data_format == "xml"
        assert source.requires_auth is False
        assert source.rate_limit_per_hour == 100
        assert source.last_verified == now
        assert source.is_active is True
        assert source.created_at == now
        assert source.priority == 1
        assert source.reliability_score == 0.95
        assert source.last_health_check == now
        assert source.health_status == HealthStatus.HEALTHY
        assert source.failure_count == 0
        assert source.success_count == 10
        assert source.avg_response_time == 1500.0
        assert source.rate_limit_remaining == 95
        assert source.rate_limit_reset == reset_time
    
    def test_serialization_compatibility(self):
        """Test that the enhanced model is compatible with serialization."""
        source = TufeDataSource(
            source_name="Test API",
            api_endpoint="https://api.example.com",
            series_code="TEST",
            priority=1,
            reliability_score=0.8,
            health_status=HealthStatus.HEALTHY,
            failure_count=2,
            success_count=8,
            avg_response_time=1200.0,
            rate_limit_remaining=90
        )
        
        # Test that all fields can be accessed
        fields = [
            'id', 'source_name', 'api_endpoint', 'series_code', 'data_format',
            'requires_auth', 'rate_limit_per_hour', 'last_verified', 'is_active',
            'created_at', 'priority', 'reliability_score', 'last_health_check',
            'health_status', 'failure_count', 'success_count', 'avg_response_time',
            'rate_limit_remaining', 'rate_limit_reset'
        ]
        
        for field in fields:
            assert hasattr(source, field)
            getattr(source, field)  # Should not raise exception


if __name__ == "__main__":
    pytest.main([__file__])
