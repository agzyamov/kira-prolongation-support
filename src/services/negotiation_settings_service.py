"""
NegotiationSettingsService for managing user negotiation preferences.
"""

import streamlit as st
from datetime import datetime
from typing import Optional
from src.models.negotiation_settings import NegotiationSettings
from src.services.exceptions import ServiceError


class NegotiationModeError(ServiceError):
    """Raised when invalid negotiation mode is provided."""
    pass


class NegotiationSettingsService:
    """Service for managing negotiation settings."""
    
    SESSION_STATE_KEY = "negotiation_mode"
    
    def __init__(self):
        """Initialize the negotiation settings service."""
        pass
    
    def get_current_mode(self) -> str:
        """
        Get current negotiation mode.
        
        Returns:
            Current negotiation mode ("calm" or "assertive")
        """
        try:
            # Try to get from session state first
            mode = self.load_from_session_state()
            return mode
        except Exception:
            # Fall back to default
            return "calm"
    
    def set_mode(self, mode: str) -> None:
        """
        Set negotiation mode.
        
        Args:
            mode: Negotiation mode ("calm" or "assertive")
            
        Raises:
            NegotiationModeError: If mode is invalid
        """
        if mode not in ["calm", "assertive"]:
            raise NegotiationModeError(f"Invalid negotiation mode: {mode}. Must be 'calm' or 'assertive'.")
        
        # Save to session state
        self.save_to_session_state(mode)
    
    def save_to_session_state(self, mode: str) -> None:
        """
        Save mode to Streamlit session state.
        
        Args:
            mode: Mode to save
            
        Raises:
            NegotiationModeError: If mode is invalid
        """
        if mode not in ["calm", "assertive"]:
            raise NegotiationModeError(f"Invalid negotiation mode: {mode}. Must be 'calm' or 'assertive'.")
        
        try:
            st.session_state[self.SESSION_STATE_KEY] = mode
        except Exception as e:
            # If session state is not available, that's okay
            # The mode will be handled by the calling code
            pass
    
    def load_from_session_state(self) -> str:
        """
        Load mode from Streamlit session state.
        
        Returns:
            Current mode or default "calm"
        """
        try:
            mode = st.session_state.get(self.SESSION_STATE_KEY, "calm")
            if mode not in ["calm", "assertive"]:
                return "calm"
            return mode
        except Exception:
            # If session state is not available, return default
            return "calm"
    
    def get_negotiation_settings(self) -> NegotiationSettings:
        """
        Get current negotiation settings.
        
        Returns:
            NegotiationSettings object with current preferences
        """
        mode = self.get_current_mode()
        now = datetime.now()
        
        return NegotiationSettings(
            mode=mode,
            created_at=now,
            updated_at=now
        )
    
    def is_calm_mode(self) -> bool:
        """
        Check if current mode is calm.
        
        Returns:
            True if current mode is calm
        """
        return self.get_current_mode() == "calm"
    
    def is_assertive_mode(self) -> bool:
        """
        Check if current mode is assertive.
        
        Returns:
            True if current mode is assertive
        """
        return self.get_current_mode() == "assertive"
    
    def toggle_mode(self) -> str:
        """
        Toggle between calm and assertive modes.
        
        Returns:
            New mode after toggle
        """
        current_mode = self.get_current_mode()
        new_mode = "assertive" if current_mode == "calm" else "calm"
        self.set_mode(new_mode)
        return new_mode
