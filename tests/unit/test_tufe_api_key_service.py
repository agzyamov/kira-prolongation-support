"""
Unit tests for TufeApiKeyService.
"""

import pytest
import tempfile
import os
from datetime import datetime
from src.services.tufe_api_key_service import TufeApiKeyService
from src.models.tufe_api_key import TufeApiKey
from src.storage import DataStore
from src.services.exceptions import TufeApiKeyError


class TestTufeApiKeyService:
    """Unit tests for TufeApiKeyService."""

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

    def test_get_api_key_none(self):
        """Test getting API key when none exists."""
        api_key = self.service.get_api_key(1)
        assert api_key is None

    def test_set_api_key_success(self):
        """Test setting an API key."""
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_api_key_123"
        )
        
        assert isinstance(key_id, int)
        assert key_id > 0

    def test_get_api_key_success(self):
        """Test getting an API key."""
        # Set an API key first
        self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_api_key_123"
        )
        
        # Get the API key
        api_key = self.service.get_api_key(1)
        assert api_key == "test_api_key_123"

    def test_update_api_key_success(self):
        """Test updating an API key."""
        # Set an API key first
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="original_key"
        )
        
        # Update the API key
        result = self.service.update_api_key(key_id, "updated_key")
        assert result is True
        
        # Verify the update
        api_key = self.service.get_api_key(1)
        assert api_key == "updated_key"

    def test_deactivate_api_key_success(self):
        """Test deactivating an API key."""
        # Set an API key first
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_key"
        )
        
        # Deactivate the API key
        result = self.service.deactivate_api_key(key_id)
        assert result is True

    def test_activate_api_key_success(self):
        """Test activating an API key."""
        # Set an API key first
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_key"
        )
        
        # Deactivate it first
        self.service.deactivate_api_key(key_id)
        
        # Activate it again
        result = self.service.activate_api_key(key_id)
        assert result is True

    def test_get_keys_for_source(self):
        """Test getting all keys for a source."""
        # Set multiple keys for the same source
        self.service.set_api_key(
            source_id=1,
            key_name="Primary Key",
            api_key="primary_key"
        )
        
        self.service.set_api_key(
            source_id=1,
            key_name="Backup Key",
            api_key="backup_key"
        )
        
        # Get all keys for the source
        keys = self.service.get_keys_for_source(1)
        assert len(keys) == 2
        assert keys[0].key_name in ["Primary Key", "Backup Key"]
        assert keys[1].key_name in ["Primary Key", "Backup Key"]

    def test_get_active_keys_for_source(self):
        """Test getting active keys for a source."""
        # Set multiple keys
        key_id_1 = self.service.set_api_key(
            source_id=1,
            key_name="Active Key",
            api_key="active_key"
        )
        
        key_id_2 = self.service.set_api_key(
            source_id=1,
            key_name="Inactive Key",
            api_key="inactive_key"
        )
        
        # Deactivate one key
        self.service.deactivate_api_key(key_id_2)
        
        # Get active keys
        active_keys = self.service.get_active_keys_for_source(1)
        assert len(active_keys) == 1
        assert active_keys[0].key_name == "Active Key"

    def test_record_api_usage(self):
        """Test recording API usage."""
        # Set an API key first
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_key"
        )
        
        # Record usage
        self.service.record_api_usage(key_id)
        
        # Verify usage was recorded
        keys = self.service.get_keys_for_source(1)
        assert keys[0].last_used is not None

    def test_get_api_key_by_id(self):
        """Test getting API key by ID."""
        # Set an API key first
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_key"
        )
        
        # Get by ID
        api_key = self.service.get_api_key_by_id(key_id)
        assert api_key is not None
        assert api_key.key_name == "Test Key"
        assert api_key.api_key == "test_key"

    def test_get_api_key_statistics(self):
        """Test getting API key statistics."""
        # Set some keys
        key_id_1 = self.service.set_api_key(
            source_id=1,
            key_name="Active Key",
            api_key="active_key"
        )
        
        key_id_2 = self.service.set_api_key(
            source_id=1,
            key_name="Inactive Key",
            api_key="inactive_key"
        )
        
        # Record usage for one key
        self.service.record_api_usage(key_id_1)
        
        # Deactivate one key
        self.service.deactivate_api_key(key_id_2)
        
        stats = self.service.get_api_key_statistics(1)
        
        assert stats["total_keys"] == 2
        assert stats["active_keys"] == 1
        assert stats["recently_used_keys"] == 1
        assert stats["old_keys"] == 0
        assert stats["usage_rate"] == 0.5

    def test_cleanup_old_keys(self):
        """Test cleaning up old API keys."""
        # Set a key
        self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_key"
        )
        
        # Cleanup old keys
        cleaned_count = self.service.cleanup_old_keys(max_age_days=1)
        assert cleaned_count >= 0

    def test_validate_api_key_format_valid(self):
        """Test validating valid API key format."""
        valid_keys = [
            "valid_api_key_123",
            "another_valid_key_456",
            "test_key_with_numbers_789"
        ]
        
        for key in valid_keys:
            assert self.service.validate_api_key_format(key) is True

    def test_validate_api_key_format_invalid(self):
        """Test validating invalid API key format."""
        invalid_keys = [
            "",  # Empty
            "short",  # Too short
            "test",  # Contains "test"
            "demo_key",  # Contains "demo"
            "sample_key",  # Contains "sample"
            "invalid_key"  # Contains "invalid"
        ]
        
        for key in invalid_keys:
            assert self.service.validate_api_key_format(key) is False

    def test_rotate_api_key(self):
        """Test rotating an API key."""
        # Set an original key
        old_key_id = self.service.set_api_key(
            source_id=1,
            key_name="Original Key",
            api_key="old_key"
        )
        
        # Rotate the key
        new_key_id = self.service.rotate_api_key(
            source_id=1,
            old_key_id=old_key_id,
            new_key="new_key",
            key_name="Rotated Key"
        )
        
        assert new_key_id != old_key_id
        assert new_key_id > 0
        
        # Verify old key is deactivated and new key is active
        old_key = self.service.get_api_key_by_id(old_key_id)
        new_key = self.service.get_api_key_by_id(new_key_id)
        
        assert old_key.is_active is False
        assert new_key.is_active is True
        assert new_key.api_key == "new_key"

    def test_set_api_key_validation_error(self):
        """Test setting API key with validation error."""
        with pytest.raises(TufeApiKeyError):
            self.service.set_api_key(
                source_id=1,
                key_name="",  # Invalid empty name
                api_key="test_key"
            )

    def test_update_api_key_validation_error(self):
        """Test updating API key with validation error."""
        # Set a key first
        key_id = self.service.set_api_key(
            source_id=1,
            key_name="Test Key",
            api_key="test_key"
        )
        
        with pytest.raises(TufeApiKeyError):
            self.service.update_api_key(key_id, "")  # Invalid empty key

    def test_get_api_key_by_id_not_found(self):
        """Test getting API key by non-existent ID."""
        api_key = self.service.get_api_key_by_id(999)
        assert api_key is None

    def test_update_nonexistent_api_key(self):
        """Test updating non-existent API key."""
        result = self.service.update_api_key(999, "new_key")
        assert result is False

    def test_deactivate_nonexistent_api_key(self):
        """Test deactivating non-existent API key."""
        result = self.service.deactivate_api_key(999)
        assert result is False

    def test_activate_nonexistent_api_key(self):
        """Test activating non-existent API key."""
        result = self.service.activate_api_key(999)
        assert result is False

    def test_record_usage_nonexistent_api_key(self):
        """Test recording usage for non-existent API key."""
        # Should not raise error
        self.service.record_api_usage(999)
