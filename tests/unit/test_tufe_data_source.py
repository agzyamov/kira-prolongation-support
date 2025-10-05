"""
Unit tests for TufeDataSource model.
"""

import pytest
from datetime import datetime
from src.models.tufe_data_source import TufeDataSource


class TestTufeDataSource:
    """Unit tests for TufeDataSource model."""

    def test_valid_tufe_data_source_creation(self):
        """Test creating a valid TufeDataSource."""
        source = TufeDataSource(
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True
        )
        
        assert source.source_name == "TCMB EVDS API"
        assert source.api_endpoint == "https://evds2.tcmb.gov.tr/service/evds/"
        assert source.series_code == "TP.FE.OKTG01"
        assert source.data_format == "json"
        assert source.requires_auth is True
        assert source.rate_limit_per_hour == 100
        assert source.is_active is True

    def test_invalid_source_name_raises_error(self):
        """Test that invalid source name raises ValueError."""
        with pytest.raises(ValueError, match="source_name must be a non-empty string"):
            TufeDataSource(
                source_name="",
                api_endpoint="https://api.example.com",
                series_code="TEST001",
                data_format="json"
            )

    def test_invalid_api_endpoint_raises_error(self):
        """Test that invalid API endpoint raises ValueError."""
        with pytest.raises(ValueError, match="api_endpoint must be a valid URL"):
            TufeDataSource(
                source_name="Test Source",
                api_endpoint="invalid-url",
                series_code="TEST001",
                data_format="json"
            )

    def test_invalid_series_code_raises_error(self):
        """Test that invalid series code raises ValueError."""
        with pytest.raises(ValueError, match="series_code must be a non-empty string"):
            TufeDataSource(
                source_name="Test Source",
                api_endpoint="https://api.example.com",
                series_code="",
                data_format="json"
            )

    def test_invalid_data_format_raises_error(self):
        """Test that invalid data format raises ValueError."""
        with pytest.raises(ValueError, match="data_format must be 'json' or 'xml'"):
            TufeDataSource(
                source_name="Test Source",
                api_endpoint="https://api.example.com",
                series_code="TEST001",
                data_format="invalid"
            )

    def test_invalid_rate_limit_raises_error(self):
        """Test that invalid rate limit raises ValueError."""
        with pytest.raises(ValueError, match="rate_limit_per_hour must be a positive integer"):
            TufeDataSource(
                source_name="Test Source",
                api_endpoint="https://api.example.com",
                series_code="TEST001",
                data_format="json",
                rate_limit_per_hour=0
            )

    def test_to_dict_conversion(self):
        """Test converting TufeDataSource to dictionary."""
        source = TufeDataSource(
            id=1,
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True
        )
        
        data_dict = source.to_dict()
        
        assert data_dict['id'] == 1
        assert data_dict['source_name'] == "Test Source"
        assert data_dict['api_endpoint'] == "https://api.example.com"
        assert data_dict['series_code'] == "TEST001"
        assert data_dict['data_format'] == "json"
        assert data_dict['requires_auth'] is True
        assert data_dict['rate_limit_per_hour'] == 100
        assert data_dict['is_active'] is True

    def test_from_dict_creation(self):
        """Test creating TufeDataSource from dictionary."""
        data_dict = {
            'id': 1,
            'source_name': 'Test Source',
            'api_endpoint': 'https://api.example.com',
            'series_code': 'TEST001',
            'data_format': 'json',
            'requires_auth': True,
            'rate_limit_per_hour': 100,
            'is_active': True,
            'last_verified': '2024-01-01T12:00:00',
            'created_at': '2024-01-01T10:00:00'
        }
        
        source = TufeDataSource.from_dict(data_dict)
        
        assert source.id == 1
        assert source.source_name == "Test Source"
        assert source.api_endpoint == "https://api.example.com"
        assert source.series_code == "TEST001"
        assert source.data_format == "json"
        assert source.requires_auth is True
        assert source.rate_limit_per_hour == 100
        assert source.is_active is True
        assert source.last_verified == datetime(2024, 1, 1, 12, 0, 0)
        assert source.created_at == datetime(2024, 1, 1, 10, 0, 0)

    def test_update_verification(self):
        """Test updating verification timestamp."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        
        assert source.last_verified is None
        
        verification_time = datetime(2024, 1, 1, 12, 0, 0)
        source.update_verification(verification_time)
        
        assert source.last_verified == verification_time

    def test_activate_deactivate(self):
        """Test activating and deactivating data source."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            is_active=False
        )
        
        assert source.is_active is False
        
        source.activate()
        assert source.is_active is True
        
        source.deactivate()
        assert source.is_active is False

    def test_is_verified(self):
        """Test checking if data source is verified."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        
        assert source.is_verified() is False
        
        source.update_verification()
        assert source.is_verified() is True

    def test_get_verification_age_days(self):
        """Test getting verification age in days."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        
        assert source.get_verification_age_days() is None
        
        # Set verification to 5 days ago
        from datetime import timedelta
        old_verification = datetime.now() - timedelta(days=5)
        source.update_verification(old_verification)
        
        age_days = source.get_verification_age_days()
        assert age_days is not None
        assert 4 <= age_days <= 6  # Allow some tolerance for test execution time

    def test_needs_verification(self):
        """Test checking if data source needs verification."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        
        # Not verified yet
        assert source.needs_verification() is True
        
        # Recently verified
        source.update_verification()
        assert source.needs_verification() is False
        
        # Old verification
        from datetime import timedelta
        old_verification = datetime.now() - timedelta(days=35)
        source.update_verification(old_verification)
        assert source.needs_verification() is True

    def test_string_representation(self):
        """Test string representation of TufeDataSource."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            is_active=True
        )
        
        source.update_verification()
        
        str_repr = str(source)
        assert "TufeDataSource" in str_repr
        assert "Test Source" in str_repr
        assert "Active" in str_repr
        assert "Verified" in str_repr

    def test_repr_representation(self):
        """Test detailed string representation of TufeDataSource."""
        source = TufeDataSource(
            id=1,
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True
        )
        
        repr_str = repr(source)
        assert "TufeDataSource" in repr_str
        assert "id=1" in repr_str
        assert "source_name='Test Source'" in repr_str
        assert "api_endpoint='https://api.example.com'" in repr_str
        assert "series_code='TEST001'" in repr_str
        assert "data_format='json'" in repr_str
        assert "requires_auth=True" in repr_str
        assert "rate_limit_per_hour=100" in repr_str
        assert "is_active=True" in repr_str
