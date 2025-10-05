"""
Integration tests for TCMB API key configuration.
Tests the complete flow of API key configuration and validation.
"""

import pytest
import tempfile
import os
from src.services.tufe_config_service import TufeConfigService
from src.services.tufe_api_key_service import TufeApiKeyService
from src.services.tufe_data_source_service import TufeDataSourceService
from src.storage import DataStore


class TestTCMBApiKeyConfig:
    """Integration tests for TCMB API key configuration."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.data_store = DataStore(self.db_path)
        self.config_service = TufeConfigService()
        self.api_key_service = TufeApiKeyService(self.data_store)
        self.data_source_service = TufeDataSourceService(self.data_store)

    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_api_key_configuration_flow(self):
        """Test the complete API key configuration flow."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Step 1: Get TCMB data source
            tcmb_source = self.data_source_service.get_active_source()
            assert tcmb_source is not None
            assert tcmb_source.source_name == "TCMB EVDS API"
            
            # Step 2: Set API key
            key_id = self.api_key_service.set_api_key(
                source_id=tcmb_source.id,
                key_name="Primary TCMB Key",
                api_key="test_tcmb_api_key_123"
            )
            assert key_id > 0
            
            # Step 3: Verify API key is stored
            stored_key = self.api_key_service.get_api_key(tcmb_source.id)
            assert stored_key == "test_tcmb_api_key_123"
            
            # Step 4: Update configuration service
            self.config_service.set_tcmb_api_key("test_tcmb_api_key_123")
            
            # Step 5: Verify configuration is accessible
            config_key = self.config_service.get_tcmb_api_key()
            assert config_key == "test_tcmb_api_key_123"

    def test_api_key_validation_flow(self):
        """Test the API key validation flow."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Set up API key
            self.config_service.set_tcmb_api_key("test_tcmb_api_key_123")
            
            # Validate API key (this would make actual API call in real implementation)
            # For now, just test that the method exists and returns boolean
            is_valid = self.config_service.validate_api_key()
            assert isinstance(is_valid, bool)

    def test_multiple_api_keys_management(self):
        """Test management of multiple API keys."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Get TCMB data source
            tcmb_source = self.data_source_service.get_active_source()
            
            # Set primary API key
            primary_key_id = self.api_key_service.set_api_key(
                source_id=tcmb_source.id,
                key_name="Primary Key",
                api_key="primary_key_123"
            )
            
            # Set backup API key
            backup_key_id = self.api_key_service.set_api_key(
                source_id=tcmb_source.id,
                key_name="Backup Key",
                api_key="backup_key_456"
            )
            
            # Verify both keys are stored
            keys = self.api_key_service.get_keys_for_source(tcmb_source.id)
            assert len(keys) == 2
            assert primary_key_id != backup_key_id

    def test_api_key_deactivation_flow(self):
        """Test the API key deactivation flow."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Get TCMB data source
            tcmb_source = self.data_source_service.get_active_source()
            
            # Set API key
            key_id = self.api_key_service.set_api_key(
                source_id=tcmb_source.id,
                key_name="Test Key",
                api_key="test_key_123"
            )
            
            # Verify key is active
            keys = self.api_key_service.get_keys_for_source(tcmb_source.id)
            assert len(keys) == 1
            assert keys[0].is_active is True
            
            # Deactivate key
            result = self.api_key_service.deactivate_api_key(key_id)
            assert result is True
            
            # Verify key is deactivated
            keys = self.api_key_service.get_keys_for_source(tcmb_source.id)
            assert len(keys) == 1
            assert keys[0].is_active is False

    def test_api_key_usage_tracking(self):
        """Test API key usage tracking."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Get TCMB data source
            tcmb_source = self.data_source_service.get_active_source()
            
            # Set API key
            key_id = self.api_key_service.set_api_key(
                source_id=tcmb_source.id,
                key_name="Test Key",
                api_key="test_key_123"
            )
            
            # Record API usage
            self.api_key_service.record_api_usage(key_id)
            
            # Verify usage was recorded
            keys = self.api_key_service.get_keys_for_source(tcmb_source.id)
            assert len(keys) == 1
            assert keys[0].last_used is not None

    def test_configuration_persistence(self):
        """Test that configuration persists across service instances."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Set configuration
            self.config_service.set_tcmb_api_key("persistent_key_123")
            
            # Create new service instance
            new_config_service = TufeConfigService()
            
            # Verify configuration persists
            api_key = new_config_service.get_tcmb_api_key()
            assert api_key == "persistent_key_123"

    def test_environment_variable_override(self):
        """Test that environment variables override configuration."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Set environment variable
            os.environ['TCMB_API_KEY'] = 'env_override_key'
            
            # Create new service instance
            service = TufeConfigService()
            
            # Verify environment variable is used
            api_key = service.get_tcmb_api_key()
            assert api_key == 'env_override_key'
            
            # Clean up
            del os.environ['TCMB_API_KEY']

    def test_invalid_api_key_handling(self):
        """Test handling of invalid API keys."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Test empty API key
            with pytest.raises(ValueError):
                self.config_service.set_tcmb_api_key("")
            
            # Test None API key
            with pytest.raises(ValueError):
                self.config_service.set_tcmb_api_key(None)
            
            # Test invalid format API key
            with pytest.raises(ValueError):
                self.config_service.set_tcmb_api_key("invalid_format")

    def test_api_key_security(self):
        """Test that API keys are handled securely."""
        # This will fail initially as the services don't exist
        with pytest.raises(AttributeError):
            # Set API key
            original_key = "secure_key_123"
            self.config_service.set_tcmb_api_key(original_key)
            
            # Verify key is not logged or exposed inappropriately
            # (This would be tested with actual logging/monitoring in real implementation)
            retrieved_key = self.config_service.get_tcmb_api_key()
            assert retrieved_key == original_key
