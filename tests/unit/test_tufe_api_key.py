"""
Unit tests for TufeApiKey model.
"""

import pytest
from datetime import datetime
from src.models.tufe_api_key import TufeApiKey


class TestTufeApiKey:
    """Unit tests for TufeApiKey model."""

    def test_valid_tufe_api_key_creation(self):
        """Test creating a valid TufeApiKey."""
        api_key = TufeApiKey(
            key_name="Primary TCMB Key",
            api_key="test_api_key_123",
            source_id=1,
            is_active=True
        )
        
        assert api_key.key_name == "Primary TCMB Key"
        assert api_key.api_key == "test_api_key_123"
        assert api_key.source_id == 1
        assert api_key.is_active is True

    def test_invalid_key_name_raises_error(self):
        """Test that invalid key name raises ValueError."""
        with pytest.raises(ValueError, match="key_name must be a non-empty string"):
            TufeApiKey(
                key_name="",
                api_key="test_key",
                source_id=1
            )

    def test_invalid_api_key_raises_error(self):
        """Test that invalid API key raises ValueError."""
        with pytest.raises(ValueError, match="api_key must be a non-empty string"):
            TufeApiKey(
                key_name="Test Key",
                api_key="",
                source_id=1
            )

    def test_invalid_source_id_raises_error(self):
        """Test that invalid source ID raises ValueError."""
        with pytest.raises(ValueError, match="source_id must be a positive integer"):
            TufeApiKey(
                key_name="Test Key",
                api_key="test_key",
                source_id=0
            )

    def test_to_dict_conversion(self):
        """Test converting TufeApiKey to dictionary."""
        api_key = TufeApiKey(
            id=1,
            key_name="Test Key",
            api_key="test_api_key_123",
            source_id=1,
            is_active=True
        )
        
        data_dict = api_key.to_dict()
        
        assert data_dict['id'] == 1
        assert data_dict['key_name'] == "Test Key"
        assert data_dict['source_id'] == 1
        assert data_dict['is_active'] is True
        # API key should be encrypted in the dictionary
        assert data_dict['api_key'] != "test_api_key_123"

    def test_from_dict_creation(self):
        """Test creating TufeApiKey from dictionary."""
        # Create a key first to get encrypted version
        original_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_api_key_123",
            source_id=1
        )
        encrypted_dict = original_key.to_dict()
        
        # Now create from the encrypted dictionary
        api_key = TufeApiKey.from_dict(encrypted_dict)
        
        assert api_key.key_name == "Test Key"
        assert api_key.api_key == "test_api_key_123"  # Should be decrypted
        assert api_key.source_id == 1
        assert api_key.is_active is True

    def test_api_key_encryption_decryption(self):
        """Test that API key encryption and decryption work correctly."""
        original_key = "test_api_key_123"
        
        # Test encryption
        encrypted = TufeApiKey._encrypt_key(original_key)
        assert encrypted != original_key
        assert len(encrypted) > 0
        
        # Test decryption
        decrypted = TufeApiKey._decrypt_key(encrypted)
        assert decrypted == original_key

    def test_record_usage(self):
        """Test recording API key usage."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_key",
            source_id=1
        )
        
        assert api_key.last_used is None
        
        usage_time = datetime(2024, 1, 1, 12, 0, 0)
        api_key.record_usage(usage_time)
        
        assert api_key.last_used == usage_time

    def test_activate_deactivate(self):
        """Test activating and deactivating API key."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_key",
            source_id=1,
            is_active=False
        )
        
        assert api_key.is_active is False
        
        api_key.activate()
        assert api_key.is_active is True
        
        api_key.deactivate()
        assert api_key.is_active is False

    def test_is_recently_used(self):
        """Test checking if API key was used recently."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_key",
            source_id=1
        )
        
        # Not used yet
        assert api_key.is_recently_used() is False
        
        # Used recently
        api_key.record_usage()
        assert api_key.is_recently_used() is True
        
        # Used long ago
        from datetime import timedelta
        old_usage = datetime.now() - timedelta(hours=25)
        api_key.record_usage(old_usage)
        assert api_key.is_recently_used() is False

    def test_get_usage_age_hours(self):
        """Test getting usage age in hours."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_key",
            source_id=1
        )
        
        assert api_key.get_usage_age_hours() is None
        
        # Set usage to 2 hours ago
        from datetime import timedelta
        old_usage = datetime.now() - timedelta(hours=2)
        api_key.record_usage(old_usage)
        
        age_hours = api_key.get_usage_age_hours()
        assert age_hours is not None
        assert 1.9 <= age_hours <= 2.1  # Allow some tolerance

    def test_get_creation_age_days(self):
        """Test getting creation age in days."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_key",
            source_id=1
        )
        
        assert api_key.get_creation_age_days() is None
        
        # Set creation to 5 days ago
        from datetime import timedelta
        old_creation = datetime.now() - timedelta(days=5)
        api_key.created_at = old_creation
        
        age_days = api_key.get_creation_age_days()
        assert age_days is not None
        assert 4 <= age_days <= 6  # Allow some tolerance

    def test_is_old(self):
        """Test checking if API key is old."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_key",
            source_id=1
        )
        
        # No creation date
        assert api_key.is_old() is False
        
        # Recently created
        api_key.created_at = datetime.now()
        assert api_key.is_old() is False
        
        # Old creation
        from datetime import timedelta
        old_creation = datetime.now() - timedelta(days=400)
        api_key.created_at = old_creation
        assert api_key.is_old() is True

    def test_mask_key(self):
        """Test masking API key for display."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_api_key_123456789",
            source_id=1
        )
        
        masked = api_key.mask_key()
        assert masked != api_key.api_key
        assert "test" in masked
        assert "789" in masked
        assert "*" in masked

    def test_mask_short_key(self):
        """Test masking short API key."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="short",
            source_id=1
        )
        
        masked = api_key.mask_key()
        assert masked == "*****"  # All asterisks for short keys

    def test_string_representation(self):
        """Test string representation of TufeApiKey."""
        api_key = TufeApiKey(
            key_name="Test Key",
            api_key="test_api_key_123",
            source_id=1,
            is_active=True
        )
        
        str_repr = str(api_key)
        assert "TufeApiKey" in str_repr
        assert "Test Key" in str_repr
        assert "Active" in str_repr
        assert "test" in str_repr  # Masked key should contain part of original

    def test_repr_representation(self):
        """Test detailed string representation of TufeApiKey."""
        api_key = TufeApiKey(
            id=1,
            key_name="Test Key",
            api_key="test_api_key_123",
            source_id=1,
            is_active=True
        )
        
        repr_str = repr(api_key)
        assert "TufeApiKey" in repr_str
        assert "id=1" in repr_str
        assert "key_name='Test Key'" in repr_str
        assert "source_id=1" in repr_str
        assert "is_active=True" in repr_str
        # API key should be masked in repr
        assert "test_api_key_123" not in repr_str
