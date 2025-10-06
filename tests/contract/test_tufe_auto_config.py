"""
Contract tests for TufeAutoConfig.
Tests the service interface and expected behavior for zero-configuration setup.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.tufe_auto_config import TufeAutoConfig
from src.services.exceptions import AutoConfigError
from src.models.tufe_auto_config import TufeAutoConfig as TufeAutoConfigModel
from src.models.tufe_data_source import TufeDataSource


class TestTufeAutoConfig:
    """Test TufeAutoConfig contract and interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_data_store = Mock()
        self.service = TufeAutoConfig(self.mock_data_store)
    
    def test_setup_zero_config_success(self):
        """Test setting up zero-configuration successfully."""
        # Arrange
        expected_config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.save_tufe_auto_config.return_value = 1
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = expected_config
        
        # Act
        result = self.service.setup_zero_config()
        
        # Assert
        assert result is not None
        assert result.config_name == "default_config"
        assert result.auto_discovery_enabled is True
        assert result.fallback_to_manual is True
        assert result.cache_duration_hours == 24
        assert result.validation_enabled is True
        self.mock_data_store.save_tufe_auto_config.assert_called_once()
    
    def test_setup_zero_config_already_exists(self):
        """Test setting up zero-config when config already exists."""
        # Arrange
        existing_config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = existing_config
        
        # Act
        result = self.service.setup_zero_config()
        
        # Assert
        assert result is not None
        assert result.config_name == "default_config"
        # Should not create new config if one exists
        self.mock_data_store.save_tufe_auto_config.assert_not_called()
    
    def test_discover_available_sources_success(self):
        """Test discovering available TÜFE data sources."""
        # Arrange
        discovered_sources = [
            TufeDataSource(
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
            ),
            TufeDataSource(
                id=2,
                source_name="TÜİK API",
                api_endpoint="https://data.tuik.gov.tr/api/",
                series_code="TUF01",
                data_format="json",
                requires_auth=True,
                rate_limit_per_hour=200,
                is_active=True,
                priority=2,
                reliability_score=0.90,
                health_status="healthy"
            )
        ]
        
        with patch.object(self.service, '_discover_tcmb_source') as mock_tcmb, \
             patch.object(self.service, '_discover_tuik_source') as mock_tuik, \
             patch.object(self.service, '_discover_epias_source') as mock_epias:
            
            mock_tcmb.return_value = discovered_sources[0]
            mock_tuik.return_value = discovered_sources[1]
            mock_epias.return_value = None  # Not available
            
            # Act
            result = self.service.discover_available_sources()
            
            # Assert
            assert len(result) == 2
            assert result[0].source_name == "TCMB EVDS API"
            assert result[1].source_name == "TÜİK API"
            mock_tcmb.assert_called_once()
            mock_tuik.assert_called_once()
            mock_epias.assert_called_once()
    
    def test_discover_available_sources_no_sources_found(self):
        """Test discovering sources when none are available."""
        # Arrange
        with patch.object(self.service, '_discover_tcmb_source') as mock_tcmb, \
             patch.object(self.service, '_discover_tuik_source') as mock_tuik, \
             patch.object(self.service, '_discover_epias_source') as mock_epias:
            
            mock_tcmb.return_value = None
            mock_tuik.return_value = None
            mock_epias.return_value = None
            
            # Act
            result = self.service.discover_available_sources()
            
            # Assert
            assert len(result) == 0
            mock_tcmb.assert_called_once()
            mock_tuik.assert_called_once()
            mock_epias.assert_called_once()
    
    def test_auto_configure_sources_success(self):
        """Test auto-configuring discovered sources."""
        # Arrange
        discovered_sources = [
            TufeDataSource(
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
        ]
        
        with patch.object(self.service, 'discover_available_sources') as mock_discover:
            mock_discover.return_value = discovered_sources
            self.mock_data_store.save_tufe_data_source.return_value = 1
            
            # Act
            result = self.service.auto_configure_sources()
            
            # Assert
            assert len(result) == 1
            assert result[0].source_name == "TCMB EVDS API"
            self.mock_data_store.save_tufe_data_source.assert_called_once()
            mock_discover.assert_called_once()
    
    def test_auto_configure_sources_discovery_fails(self):
        """Test auto-configuring when source discovery fails."""
        # Arrange
        with patch.object(self.service, 'discover_available_sources') as mock_discover:
            mock_discover.side_effect = AutoConfigError("Discovery failed")
            
            # Act & Assert
            with pytest.raises(AutoConfigError, match="Discovery failed"):
                self.service.auto_configure_sources()
    
    def test_get_default_priority_order_success(self):
        """Test getting default priority order."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.service.get_default_priority_order()
        
        # Assert
        assert result == [1, 2, 3]
        self.mock_data_store.get_tufe_auto_config_by_name.assert_called_once_with("default_config")
    
    def test_get_default_priority_order_no_config(self):
        """Test getting priority order when no config exists."""
        # Arrange
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = None
        
        # Act
        result = self.service.get_default_priority_order()
        
        # Assert
        assert result == []  # Empty list as fallback
        self.mock_data_store.get_tufe_auto_config_by_name.assert_called_once_with("default_config")
    
    def test_is_auto_config_enabled_true(self):
        """Test checking if auto-config is enabled (true)."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.service.is_auto_config_enabled()
        
        # Assert
        assert result is True
        self.mock_data_store.get_tufe_auto_config_by_name.assert_called_once_with("default_config")
    
    def test_is_auto_config_enabled_false(self):
        """Test checking if auto-config is enabled (false)."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=False,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.service.is_auto_config_enabled()
        
        # Assert
        assert result is False
        self.mock_data_store.get_tufe_auto_config_by_name.assert_called_once_with("default_config")
    
    def test_is_auto_config_enabled_no_config(self):
        """Test checking if auto-config is enabled when no config exists."""
        # Arrange
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = None
        
        # Act
        result = self.service.is_auto_config_enabled()
        
        # Assert
        assert result is False  # Default to disabled
        self.mock_data_store.get_tufe_auto_config_by_name.assert_called_once_with("default_config")
    
    def test_enable_auto_config_success(self):
        """Test enabling auto-configuration."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=False,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        self.mock_data_store.update_tufe_auto_config.return_value = True
        
        # Act
        self.service.enable_auto_config()
        
        # Assert
        self.mock_data_store.get_tufe_auto_config_by_name.assert_called_once_with("default_config")
        self.mock_data_store.update_tufe_auto_config.assert_called_once()
        
        # Verify the config was updated to enabled
        update_call = self.mock_data_store.update_tufe_auto_config.call_args
        updated_config = update_call[0][0]
        assert updated_config.auto_discovery_enabled is True
    
    def test_disable_auto_config_success(self):
        """Test disabling auto-configuration."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        self.mock_data_store.update_tufe_auto_config.return_value = True
        
        # Act
        self.service.disable_auto_config()
        
        # Assert
        self.mock_data_store.get_tufe_auto_config_by_name.assert_called_once_with("default_config")
        self.mock_data_store.update_tufe_auto_config.assert_called_once()
        
        # Verify the config was updated to disabled
        update_call = self.mock_data_store.update_tufe_auto_config.call_args
        updated_config = update_call[0][0]
        assert updated_config.auto_discovery_enabled is False
    
    def test_auto_config_with_fallback_to_manual(self):
        """Test auto-config with fallback to manual entry enabled."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.service.setup_zero_config()
        
        # Assert
        assert result.fallback_to_manual is True
    
    def test_auto_config_cache_duration_configuration(self):
        """Test auto-config cache duration configuration."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=48,  # 48 hours cache
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.service.setup_zero_config()
        
        # Assert
        assert result.cache_duration_hours == 48
    
    def test_auto_config_validation_enabled(self):
        """Test auto-config with validation enabled."""
        # Arrange
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
        )
        
        self.mock_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.service.setup_zero_config()
        
        # Assert
        assert result.validation_enabled is True
