"""
Integration test for negotiation mode persistence.
Tests that negotiation mode preferences persist across sessions.
"""

import pytest
from src.services.negotiation_settings_service import NegotiationSettingsService


class TestNegotiationModePersistence:
    """Integration tests for negotiation mode persistence."""

    def test_mode_persistence_within_session(self):
        """Test that mode persists within a single session."""
        service = NegotiationSettingsService()
        
        # Set initial mode
        service.set_mode("calm")
        assert service.get_current_mode() == "calm"
        
        # Change mode
        service.set_mode("assertive")
        assert service.get_current_mode() == "assertive"
        
        # Verify persistence
        assert service.get_current_mode() == "assertive"

    def test_mode_persistence_across_service_calls(self):
        """Test that mode persists across multiple service calls."""
        service = NegotiationSettingsService()
        
        # Set mode
        service.set_mode("calm")
        
        # Make multiple calls
        for _ in range(5):
            mode = service.get_current_mode()
            assert mode == "calm"
        
        # Change mode
        service.set_mode("assertive")
        
        # Verify change persists
        for _ in range(5):
            mode = service.get_current_mode()
            assert mode == "assertive"

    def test_session_state_integration(self):
        """Test integration with session state."""
        service = NegotiationSettingsService()
        
        # Save to session state
        service.save_to_session_state("calm")
        
        # Load from session state
        mode = service.load_from_session_state()
        assert mode == "calm"
        
        # Change and save again
        service.save_to_session_state("assertive")
        mode = service.load_from_session_state()
        assert mode == "assertive"

    def test_mode_validation_persistence(self):
        """Test that mode validation works with persistence."""
        service = NegotiationSettingsService()
        
        # Valid modes should persist
        service.set_mode("calm")
        assert service.get_current_mode() == "calm"
        
        service.set_mode("assertive")
        assert service.get_current_mode() == "assertive"
        
        # Invalid modes should not change current mode
        current_mode = service.get_current_mode()
        
        with pytest.raises(ValueError):
            service.set_mode("invalid")
        
        # Mode should remain unchanged
        assert service.get_current_mode() == current_mode

    def test_default_mode_behavior(self):
        """Test default mode behavior."""
        service = NegotiationSettingsService()
        
        # Should have a default mode
        default_mode = service.get_current_mode()
        assert default_mode in ["calm", "assertive"]
        
        # Should be able to load default from session state
        session_mode = service.load_from_session_state()
        assert session_mode in ["calm", "assertive"]

    def test_mode_switching_consistency(self):
        """Test that mode switching is consistent."""
        service = NegotiationSettingsService()
        
        # Test multiple switches
        modes = ["calm", "assertive", "calm", "assertive"]
        
        for expected_mode in modes:
            service.set_mode(expected_mode)
            assert service.get_current_mode() == expected_mode
            
            # Verify session state is also updated
            session_mode = service.load_from_session_state()
            assert session_mode == expected_mode

    def test_concurrent_mode_access(self):
        """Test that mode access is consistent under concurrent-like access."""
        service = NegotiationSettingsService()
        
        # Set mode
        service.set_mode("calm")
        
        # Simulate concurrent access by making rapid calls
        modes = []
        for _ in range(10):
            mode = service.get_current_mode()
            modes.append(mode)
        
        # All should be the same
        assert all(mode == "calm" for mode in modes)
        
        # Change mode
        service.set_mode("assertive")
        
        # Verify change is consistent
        modes = []
        for _ in range(10):
            mode = service.get_current_mode()
            modes.append(mode)
        
        assert all(mode == "assertive" for mode in modes)
