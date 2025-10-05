"""
Contract tests for TufeDataSourceService.
Tests the service interface before implementation.
"""

import pytest
import tempfile
import os
from datetime import datetime
from src.services.tufe_data_source_service import TufeDataSourceService
from src.models.tufe_data_source import TufeDataSource
from src.storage import DataStore


class TestTufeDataSourceService:
    """Contract tests for TufeDataSourceService."""

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

    def test_get_all_sources_returns_list(self):
        """Test that get_all_sources returns a list."""
        sources = self.service.get_all_sources()
        assert isinstance(sources, list)

    def test_get_active_source_returns_source_or_none(self):
        """Test that get_active_source returns TufeDataSource or None."""
        source = self.service.get_active_source()
        assert source is None or isinstance(source, TufeDataSource)

    def test_add_source_returns_id(self):
        """Test that add_source returns an integer ID."""
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

    def test_update_source_returns_boolean(self):
        """Test that update_source returns a boolean."""
        # First add a source
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
        assert isinstance(result, bool)

    def test_deactivate_source_returns_boolean(self):
        """Test that deactivate_source returns a boolean."""
        # First add a source
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
        
        # Deactivate the source
        result = self.service.deactivate_source(source_id)
        assert isinstance(result, bool)

    def test_verify_source_returns_boolean(self):
        """Test that verify_source returns a boolean."""
        # First add a source
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
        
        # Verify the source
        result = self.service.verify_source(source_id)
        assert isinstance(result, bool)

    def test_get_source_by_id_returns_source_or_none(self):
        """Test that get_source_by_id returns TufeDataSource or None."""
        # Test with non-existent ID
        source = self.service.get_source_by_id(999)
        assert source is None
        
        # Test with existing ID
        test_source = TufeDataSource(
            source_name="Test Source",
            api_endpoint="https://api.example.com",
            series_code="TEST001",
            data_format="json",
            requires_auth=True,
            rate_limit_per_hour=100,
            is_active=True
        )
        source_id = self.service.add_source(test_source)
        retrieved_source = self.service.get_source_by_id(source_id)
        assert isinstance(retrieved_source, TufeDataSource)
        assert retrieved_source.source_name == "Test Source"
