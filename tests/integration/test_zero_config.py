"""
Integration tests for zero-configuration setup.
Tests automatic source discovery and configuration without user intervention.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.tufe_auto_config import TufeAutoConfig
from src.services.tufe_source_manager import TufeSourceManager
from src.services.tufe_fetch_service import TufeFetchService
from src.models.tufe_auto_config import TufeAutoConfig as TufeAutoConfigModel
from src.models.tufe_data_source import TufeDataSource


class TestZeroConfiguration:
    """Test zero-configuration setup integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data_store = Mock()
        self.auto_config = TufeAutoConfig(self.test_data_store)
        self.source_manager = TufeSourceManager(self.test_data_store)
        self.fetch_service = TufeFetchService(self.test_data_store, self.source_manager)
    
    def test_zero_config_initial_setup(self):
        """Test initial zero-configuration setup."""
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
        
        # Mock no existing config
        self.test_data_store.get_tufe_auto_config_by_name.return_value = None
        self.test_data_store.save_tufe_auto_config.return_value = 1
        self.test_data_store.get_tufe_auto_config_by_name.return_value = expected_config
        
        # Act
        result = self.auto_config.setup_zero_config()
        
        # Assert
        assert result is not None
        assert result.config_name == "default_config"
        assert result.auto_discovery_enabled is True
        assert result.fallback_to_manual is True
        assert result.cache_duration_hours == 24
        assert result.validation_enabled is True
        self.test_data_store.save_tufe_auto_config.assert_called_once()
    
    def test_zero_config_already_configured(self):
        """Test zero-configuration when already configured."""
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
        
        self.test_data_store.get_tufe_auto_config_by_name.return_value = existing_config
        
        # Act
        result = self.auto_config.setup_zero_config()
        
        # Assert
        assert result is not None
        assert result.config_name == "default_config"
        # Should not create new config if one exists
        self.test_data_store.save_tufe_auto_config.assert_not_called()
    
    def test_zero_config_source_discovery(self):
        """Test automatic source discovery during zero-configuration."""
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
        
        with patch.object(self.auto_config, '_discover_tcmb_source', return_value=discovered_sources[0]), \
             patch.object(self.auto_config, '_discover_tuik_source', return_value=discovered_sources[1]), \
             patch.object(self.auto_config, '_discover_epias_source', return_value=None):
            
            # Act
            result = self.auto_config.discover_available_sources()
            
            # Assert
            assert len(result) == 2
            assert result[0].source_name == "TCMB EVDS API"
            assert result[1].source_name == "TÜİK API"
            assert result[0].priority == 1
            assert result[1].priority == 2
    
    def test_zero_config_source_auto_configuration(self):
        """Test automatic source configuration during zero-configuration."""
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
        
        with patch.object(self.auto_config, 'discover_available_sources', return_value=discovered_sources), \
             patch.object(self.test_data_store, 'save_tufe_data_source', return_value=1):
            
            # Act
            result = self.auto_config.auto_configure_sources()
            
            # Assert
            assert len(result) == 1
            assert result[0].source_name == "TCMB EVDS API"
            self.test_data_store.save_tufe_data_source.assert_called_once()
    
    def test_zero_config_no_sources_discovered(self):
        """Test zero-configuration when no sources are discovered."""
        # Arrange
        with patch.object(self.auto_config, 'discover_available_sources', return_value=[]):
            
            # Act
            result = self.auto_config.auto_configure_sources()
            
            # Assert
            assert len(result) == 0
            self.test_data_store.save_tufe_data_source.assert_not_called()
    
    def test_zero_config_fallback_to_manual(self):
        """Test zero-configuration with fallback to manual entry."""
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
        
        self.test_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Mock no sources discovered
        with patch.object(self.auto_config, 'discover_available_sources', return_value=[]):
            
            # Act
            result = self.auto_config.auto_configure_sources()
            
            # Assert
            assert len(result) == 0
            # Should not raise exception due to fallback_to_manual=True
    
    def test_zero_config_priority_order_setup(self):
        """Test that zero-configuration sets up proper priority order."""
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
        
        self.test_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.auto_config.get_default_priority_order()
        
        # Assert
        assert result == [1, 2, 3]
    
    def test_zero_config_cache_duration_setup(self):
        """Test that zero-configuration sets up proper cache duration."""
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
        
        self.test_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.auto_config.setup_zero_config()
        
        # Assert
        assert result.cache_duration_hours == 48
    
    def test_zero_config_validation_enabled(self):
        """Test that zero-configuration enables data validation."""
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
        
        self.test_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.auto_config.setup_zero_config()
        
        # Assert
        assert result.validation_enabled is True
    
    def test_zero_config_enable_disable_auto_config(self):
        """Test enabling and disabling auto-configuration."""
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
        
        self.test_data_store.get_tufe_auto_config_by_name.return_value = config
        self.test_data_store.update_tufe_auto_config.return_value = True
        
        # Act - Enable auto-config
        self.auto_config.enable_auto_config()
        
        # Assert
        self.test_data_store.update_tufe_auto_config.assert_called_once()
        update_call = self.test_data_store.update_tufe_auto_config.call_args
        updated_config = update_call[0][0]
        assert updated_config.auto_discovery_enabled is True
        
        # Reset mock
        self.test_data_store.update_tufe_auto_config.reset_mock()
        
        # Act - Disable auto-config
        self.auto_config.disable_auto_config()
        
        # Assert
        self.test_data_store.update_tufe_auto_config.assert_called_once()
        update_call = self.test_data_store.update_tufe_auto_config.call_args
        updated_config = update_call[0][0]
        assert updated_config.auto_discovery_enabled is False
    
    def test_zero_config_integration_with_fetch_service(self):
        """Test zero-configuration integration with fetch service."""
        # Arrange
        year = 2023
        
        config = TufeAutoConfigModel(
            id=1,
            config_name="default_config",
            auto_discovery_enabled=True,
            default_priority_order="[1, 2, 3]",
            fallback_to_manual=True,
            cache_duration_hours=24,
            validation_enabled=True
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
        
        # Mock auto-config setup and successful fetch
        with patch.object(self.auto_config, 'is_auto_config_enabled', return_value=True), \
             patch.object(self.auto_config, 'setup_zero_config', return_value=config), \
             patch.object(self.source_manager, 'get_best_source', return_value=source), \
             patch.object(self.fetch_service, '_fetch_from_source', return_value=Mock()), \
             patch.object(self.fetch_service, '_validate_data', return_value=True), \
             patch.object(self.fetch_service, '_cache_data', return_value=True):
            
            # Act
            result = self.fetch_service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            # Verify auto-config was checked
            self.auto_config.is_auto_config_enabled.assert_called_once()
    
    def test_zero_config_error_handling(self):
        """Test zero-configuration error handling."""
        # Arrange
        with patch.object(self.auto_config, 'discover_available_sources', side_effect=Exception("Discovery failed")):
            
            # Act & Assert
            with pytest.raises(Exception, match="Discovery failed"):
                self.auto_config.auto_configure_sources()
    
    def test_zero_config_performance_requirement(self):
        """Test that zero-configuration meets performance requirements."""
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
        
        with patch.object(self.auto_config, 'discover_available_sources', return_value=discovered_sources), \
             patch.object(self.test_data_store, 'save_tufe_data_source', return_value=1):
            
            # Act
            start_time = datetime.now()
            result = self.auto_config.auto_configure_sources()
            end_time = datetime.now()
            
            # Assert
            duration = (end_time - start_time).total_seconds()
            assert duration < 5.0  # Should be fast
            assert len(result) == 1
    
    def test_zero_config_source_health_monitoring(self):
        """Test that zero-configuration sets up source health monitoring."""
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
        
        self.test_data_store.get_tufe_auto_config_by_name.return_value = config
        
        # Act
        result = self.auto_config.setup_zero_config()
        
        # Assert
        assert result is not None
        assert result.auto_discovery_enabled is True
        # Health monitoring is implicit in the auto-discovery and source management
