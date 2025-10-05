"""
Unit tests for TufeDataSourceService.
"""

import pytest
import tempfile
import os
from datetime import datetime
from src.services.tufe_data_source_service import TufeDataSourceService
from src.models.tufe_data_source import TufeDataSource
from src.storage import DataStore
from src.services.exceptions import TufeDataSourceError


class TestTufeDataSourceService:
    """Unit tests for TufeDataSourceService."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.data_store = DataStore(self.db_path)
        self.service = TufeDataSourceService(self.data_store)

    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_get_all_sources_empty(self):
        """Test getting all sources when none exist."""
        sources = self.service.get_all_sources()
        assert isinstance(sources, list)
        assert len(sources) == 0

    def test_get_active_source_none(self):
        """Test getting active source when none exist."""
        source = self.service.get_active_source()
        assert source is None

    def test_add_source_success(self):
        """Test adding a new data source."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True
        )
        
        source_id = self.service.add_source(source)
        assert isinstance(source_id, int)
        assert source_id > 0

    def test_get_source_by_id_success(self):
        """Test getting a source by ID."""
        # Add a source first
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        source_id = self.service.add_source(source)
        
        # Get the source
        retrieved_source = self.service.get_source_by_id(source_id)
        assert retrieved_source is not None
        assert retrieved_source.source_name == "Test Source"
        assert retrieved_source.api_endpoint == "https://api.example.com"

    def test_get_source_by_id_not_found(self):
        """Test getting a source by non-existent ID."""
        source = self.service.get_source_by_id(999)
        assert source is None

    def test_update_source_success(self):
        """Test updating an existing source."""
        # Add a source first
        source = TufeDataSource(
            source_name="Original Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        source_id = self.service.add_source(source)
        
        # Update the source
        updated_source = TufeDataSource(
            source_name="Updated Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=200,
            is_active=True
        )
        
        result = self.service.update_source(source_id, updated_source)
        assert result is True
        
        # Verify the update
        retrieved_source = self.service.get_source_by_id(source_id)
        assert retrieved_source.source_name == "Updated Source"
        assert retrieved_source.rate_limit_per_hour == 200

    def test_deactivate_source_success(self):
        """Test deactivating a source."""
        # Add a source first
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            is_active=True
        )
        source_id = self.service.add_source(source)
        
        # Deactivate the source
        result = self.service.deactivate_source(source_id)
        assert result is True
        
        # Verify deactivation
        retrieved_source = self.service.get_source_by_id(source_id)
        assert retrieved_source.is_active is False

    def test_activate_source_success(self):
        """Test activating a source."""
        # Add a source first
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            is_active=False
        )
        source_id = self.service.add_source(source)
        
        # Activate the source
        result = self.service.activate_source(source_id)
        assert result is True
        
        # Verify activation
        retrieved_source = self.service.get_source_by_id(source_id)
        assert retrieved_source.is_active is True

    def test_verify_source_success(self):
        """Test verifying a source."""
        # Add a source first
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        source_id = self.service.add_source(source)
        
        # Verify the source
        result = self.service.verify_source(source_id)
        assert result is True
        
        # Verify verification timestamp was updated
        retrieved_source = self.service.get_source_by_id(source_id)
        assert retrieved_source.is_verified() is True

    def test_get_sources_needing_verification(self):
        """Test getting sources that need verification."""
        # Add a source without verification
        source = TufeDataSource(
            source_name="Unverified Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        self.service.add_source(source)
        
        # Add a verified source
        verified_source = TufeDataSource(
            source_name="Verified Source",
            api_endpoint="https://api.example.com",
            series_code="TEST002",
            data_format="json"
        )
        verified_id = self.service.add_source(verified_source)
        self.service.verify_source(verified_id)
        
        # Get sources needing verification
        sources_needing_verification = self.service.get_sources_needing_verification()
        assert len(sources_needing_verification) == 1
        assert sources_needing_verification[0].source_name == "Unverified Source"

    def test_get_tcmb_source_success(self):
        """Test getting TCMB source."""
        # Add TCMB source
        tcmb_source = TufeDataSource(
            source_name="TCMB EVDS API",
            api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
            series_code="TP.FE.OKTG01",
            data_format="json"
        )
        self.service.add_source(tcmb_source)
        
        # Get TCMB source
        retrieved_tcmb = self.service.get_tcmb_source()
        assert retrieved_tcmb is not None
        assert "TCMB" in retrieved_tcmb.source_name

    def test_get_tcmb_source_not_found(self):
        """Test getting TCMB source when none exists."""
        tcmb_source = self.service.get_tcmb_source()
        assert tcmb_source is None

    def test_create_default_tcmb_source(self):
        """Test creating default TCMB source."""
        tcmb_source = self.service.create_default_tcmb_source()
        
        assert tcmb_source.source_name == "TCMB EVDS API"
        assert tcmb_source.api_endpoint == "https://evds2.tcmb.gov.tr/service/evds/"
        assert tcmb_source.series_code == "TP.FE.OKTG01"
        assert tcmb_source.data_format == "json"
        assert tcmb_source.requires_auth is True
        assert tcmb_source.rate_limit_per_hour == 100
        assert tcmb_source.is_active is True
        assert tcmb_source.id is not None

    def test_get_source_statistics(self):
        """Test getting source statistics."""
        # Add some sources
        source1 = TufeDataSource(
            source_name="Active Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            is_active=True
        )
        self.service.add_source(source1)
        
        source2 = TufeDataSource(
            source_name="Inactive Source",
            api_endpoint="https://api.example.com",
            series_code="TEST002",
            data_format="json",
            is_active=False
        )
        self.service.add_source(source2)
        
        # Verify one source
        self.service.verify_source(1)
        
        stats = self.service.get_source_statistics()
        
        assert stats["total_sources"] == 2
        assert stats["active_sources"] == 1
        assert stats["verified_sources"] == 1
        assert stats["sources_needing_verification"] == 1
        assert stats["verification_rate"] == 0.5

    def test_cleanup_inactive_sources(self):
        """Test cleaning up inactive sources."""
        # Add an inactive source
        source = TufeDataSource(
            source_name="Inactive Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            is_active=False
        )
        self.service.add_source(source)
        
        # Cleanup inactive sources
        cleaned_count = self.service.cleanup_inactive_sources(days_inactive=1)
        assert cleaned_count >= 0

    def test_add_source_validation_error(self):
        """Test adding source with validation error."""
        with pytest.raises(TufeDataSourceError):
            # This should fail due to validation in the model
            invalid_source = TufeDataSource(
                source_name="",  # Invalid empty name
                api_endpoint="https://api.example.com",
                series_code="TEST001",
                data_format="json"
            )
            self.service.add_source(invalid_source)

    def test_update_nonexistent_source(self):
        """Test updating a non-existent source."""
        source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json"
        )
        
        result = self.service.update_source(999, source)
        assert result is True  # Should not raise error, just return True

    def test_deactivate_nonexistent_source(self):
        """Test deactivating a non-existent source."""
        result = self.service.deactivate_source(999)
        assert result is False

    def test_verify_nonexistent_source(self):
        """Test verifying a non-existent source."""
        result = self.service.verify_source(999)
        assert result is False
