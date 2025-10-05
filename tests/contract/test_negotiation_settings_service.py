"""
Contract tests for NegotiationSettingsService.
Tests the service interface before implementation.
"""

import pytest
from datetime import datetime
from src.services.negotiation_settings_service import NegotiationSettingsService


class TestNegotiationSettingsService:
    """Contract tests for NegotiationSettingsService."""

    def test_get_current_mode_returns_string(self):
        """Test that get_current_mode returns a string."""
        service = NegotiationSettingsService()
        mode = service.get_current_mode()
        assert isinstance(mode, str)
        assert mode in ["calm", "assertive"]

    def test_set_mode_accepts_valid_modes(self):
        """Test that set_mode accepts valid mode values."""
        service = NegotiationSettingsService()
        
        # Should not raise exception
        service.set_mode("calm")
        service.set_mode("assertive")

    def test_set_mode_rejects_invalid_modes(self):
        """Test that set_mode rejects invalid mode values."""
        service = NegotiationSettingsService()
        
        with pytest.raises(Exception):  # NegotiationModeError or ValueError
            service.set_mode("invalid")
        
        with pytest.raises(Exception):  # NegotiationModeError or ValueError
            service.set_mode("")

    def test_save_to_session_state_accepts_valid_mode(self):
        """Test that save_to_session_state accepts valid mode."""
        service = NegotiationSettingsService()
        
        # Should not raise exception
        service.save_to_session_state("calm")
        service.save_to_session_state("assertive")

    def test_load_from_session_state_returns_string(self):
        """Test that load_from_session_state returns a string."""
        service = NegotiationSettingsService()
        mode = service.load_from_session_state()
        assert isinstance(mode, str)
        assert mode in ["calm", "assertive"]

    def test_mode_persistence(self):
        """Test that mode changes persist."""
        service = NegotiationSettingsService()
        
        # Set mode
        service.set_mode("assertive")
        
        # Verify it persists
        assert service.get_current_mode() == "assertive"
        
        # Change mode
        service.set_mode("calm")
        
        # Verify change persists
        assert service.get_current_mode() == "calm"
