"""
NegotiationSettings model for storing user negotiation preferences.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class NegotiationSettings:
    """
    Immutable model for negotiation settings.
    
    Attributes:
        mode: Negotiation mode ("calm" or "assertive")
        created_at: When the setting was created
        updated_at: When the setting was last updated
    """
    
    mode: str
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        """Validate the negotiation settings after initialization."""
        if self.mode not in ["calm", "assertive"]:
            raise ValueError(f"Invalid negotiation mode: {self.mode}. Must be 'calm' or 'assertive'.")
        
        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime object")
        
        if not isinstance(self.updated_at, datetime):
            raise ValueError("updated_at must be a datetime object")
    
    def is_calm_mode(self) -> bool:
        """Check if the negotiation mode is calm."""
        return self.mode == "calm"
    
    def is_assertive_mode(self) -> bool:
        """Check if the negotiation mode is assertive."""
        return self.mode == "assertive"
    
    def with_mode(self, new_mode: str) -> "NegotiationSettings":
        """
        Create a new NegotiationSettings instance with updated mode.
        
        Args:
            new_mode: New negotiation mode
            
        Returns:
            New NegotiationSettings instance with updated mode and timestamp
        """
        if new_mode not in ["calm", "assertive"]:
            raise ValueError(f"Invalid negotiation mode: {new_mode}. Must be 'calm' or 'assertive'.")
        
        return NegotiationSettings(
            mode=new_mode,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
    
    @classmethod
    def default(cls) -> "NegotiationSettings":
        """
        Create default negotiation settings.
        
        Returns:
            Default NegotiationSettings with calm mode
        """
        now = datetime.now()
        return cls(
            mode="calm",
            created_at=now,
            updated_at=now
        )
