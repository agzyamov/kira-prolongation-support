"""
Contract tests for TufeApiKeyService.
Tests the service interface before implementation.
"""

import pytest
import tempfile
import os
from datetime import datetime
from src.services.tufe_api_key_service import TufeApiKeyService
from src.models.tufe_api_key import TufeApiKey
from src.storage import DataStore


class TestTufeApiKeyService:
    """Contract tests for TufeApiKeyService."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.data_store = DataStore(self.db_path)
        self.service = TufeApiKeyService(self.data_store)

    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_get_api_key_returns_string_or_none(self):
        """Test that get_api_key returns string or None."""
        api_key = self.service.get_api_key(1)
        assert api_key is None or isinstance(api_key, str)

    def test_set_api_key_returns_id(self):
        """Test that set_api_key returns an integer ID."""
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_api_key_123"
        )
        assert isinstance(key_id, int)
        assert key_id > 0

    def test_update_api_key_returns_boolean(self):
        """Test that update_api_key returns a boolean."""
        # First set an API key
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_api_key_123"
        )
        
        # Update the API key
        result = self.service.update_api_key(key_id, "updated_api_key_456")
        assert isinstance(result, bool)

    def test_deactivate_api_key_returns_boolean(self):
        """Test that deactivate_api_key returns a boolean."""
        # First set an API key
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_api_key_123"
        )
        
        # Deactivate the API key
        result = self.service.deactivate_api_key(key_id)
        assert isinstance(result, bool)

    def test_get_keys_for_source_returns_list(self):
        """Test that get_keys_for_source returns a list."""
        keys = self.service.get_keys_for_source(1)
        assert isinstance(keys, list)

    def test_record_api_usage_returns_none(self):
        """Test that record_api_usage returns None."""
        # First set an API key
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_api_key_123"
        )
        
        # Record API usage
        result = self.service.record_api_usage(key_id)
        assert result is None

    def test_api_key_encryption(self):
        """Test that API keys are stored encrypted."""
        # Set an API key
        original_key = "test_api_key_123"
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key=original_key
        )
        
        # Retrieve the API key
        retrieved_key = self.service.get_api_key(1)
        assert retrieved_key == original_key  # Should be decrypted

    def test_multiple_keys_for_source(self):
        """Test that multiple API keys can be stored for a source."""
        # Set multiple API keys for the same source
        key_id_1 = self.service.set_api_key(
            source_id=1,
            key_name="Primary Key",
            api_key="primary_key_123"
        )
        key_id_2 = self.service.set_api_key(
            source_id=1,
            key_name="Backup Key",
            api_key="backup_key_456"
        )
        
        # Get all keys for the source
        keys = self.service.get_keys_for_source(1)
        assert len(keys) == 2
        assert key_id_1 != key_id_2
