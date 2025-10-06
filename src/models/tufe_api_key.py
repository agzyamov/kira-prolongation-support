"""
TufeApiKey model for managing TÜFE API keys.
"""

import base64
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class TufeApiKey:
    """Enhanced model for TÜFE API keys with auto-configuration support."""
    
    id: Optional[int] = None
    key_name: str = ""
    api_key: str = ""
    source_id: int = 0
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True
    
    # Enhanced fields for auto-configuration
    source_priority: int = 5  # Priority for this source (1-10)
    auto_configured: bool = False  # Whether key was auto-discovered
    usage_count: int = 0  # Number of times key was used
    is_valid: bool = True  # Whether key is currently valid
    
    def __post_init__(self):
        """Validate the API key after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate the API key fields."""
        if not self.key_name or not self.key_name.strip():
            raise ValueError("key_name must be a non-empty string")
        
        if not self.api_key or not self.api_key.strip():
            raise ValueError("api_key must be a non-empty string")
        
        if self.source_id <= 0:
            raise ValueError("source_id must be a positive integer")
        
        if not isinstance(self.is_active, bool):
            raise ValueError("is_active must be a boolean")
        
        # Enhanced validation for new fields
        if not (1 <= self.source_priority <= 10):
            raise ValueError("source_priority must be between 1 and 10")
        
        if not isinstance(self.auto_configured, bool):
            raise ValueError("auto_configured must be a boolean")
        
        if self.usage_count < 0:
            raise ValueError("usage_count must be non-negative")
        
        if not isinstance(self.is_valid, bool):
            raise ValueError("is_valid must be a boolean")
    
    def to_dict(self) -> dict:
        """Convert the API key to a dictionary."""
        return {
            'id': self.id,
            'key_name': self.key_name,
            'api_key': self._encrypt_key(self.api_key),  # Store encrypted
            'source_id': self.source_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'is_active': self.is_active,
            # Enhanced fields
            'source_priority': self.source_priority,
            'auto_configured': self.auto_configured,
            'usage_count': self.usage_count,
            'is_valid': self.is_valid
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeApiKey':
        """Create a TufeApiKey from a dictionary."""
        # Parse datetime fields
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        last_used = None
        if data.get('last_used'):
            last_used = datetime.fromisoformat(data['last_used'])
        
        # Decrypt the API key
        encrypted_key = data.get('api_key', '')
        decrypted_key = cls._decrypt_key(encrypted_key) if encrypted_key else ''
        
        return cls(
            id=data.get('id'),
            key_name=data['key_name'],
            api_key=decrypted_key,
            source_id=data['source_id'],
            created_at=created_at,
            last_used=last_used,
            is_active=data.get('is_active', True),
            # Enhanced fields
            source_priority=data.get('source_priority', 5),
            auto_configured=data.get('auto_configured', False),
            usage_count=data.get('usage_count', 0),
            is_valid=data.get('is_valid', True)
        )
    
    @staticmethod
    def _encrypt_key(key: str) -> str:
        """Encrypt the API key for storage."""
        # Simple base64 encoding for now - in production, use proper encryption
        return base64.b64encode(key.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def _decrypt_key(encrypted_key: str) -> str:
        """Decrypt the API key from storage."""
        # Simple base64 decoding for now - in production, use proper decryption
        try:
            return base64.b64decode(encrypted_key.encode('utf-8')).decode('utf-8')
        except Exception:
            return encrypted_key  # Return as-is if decryption fails
    
    def record_usage(self, used_at: datetime = None):
        """Record API key usage."""
        if used_at is None:
            used_at = datetime.now()
        self.last_used = used_at
        self.usage_count += 1
    
    def activate(self):
        """Activate the API key."""
        self.is_active = True
    
    def deactivate(self):
        """Deactivate the API key."""
        self.is_active = False
    
    def is_recently_used(self, hours: int = 24) -> bool:
        """Check if the API key was used recently."""
        if self.last_used is None:
            return False
        
        delta = datetime.now() - self.last_used
        return delta.total_seconds() < (hours * 3600)
    
    def get_usage_age_hours(self) -> Optional[float]:
        """Get the age of the last usage in hours."""
        if self.last_used is None:
            return None
        
        delta = datetime.now() - self.last_used
        return delta.total_seconds() / 3600
    
    def get_creation_age_days(self) -> Optional[int]:
        """Get the age of the API key in days."""
        if self.created_at is None:
            return None
        
        delta = datetime.now() - self.created_at
        return delta.days
    
    def is_old(self, max_age_days: int = 365) -> bool:
        """Check if the API key is old and should be rotated."""
        age_days = self.get_creation_age_days()
        return age_days is not None and age_days > max_age_days
    
    def mask_key(self) -> str:
        """Return a masked version of the API key for display."""
        if len(self.api_key) <= 8:
            return "*" * len(self.api_key)
        
        return self.api_key[:4] + "*" * (len(self.api_key) - 8) + self.api_key[-4:]
    
    # Enhanced methods for auto-configuration
    
    def mark_as_auto_configured(self):
        """Mark the API key as auto-configured."""
        self.auto_configured = True
    
    def mark_as_manually_configured(self):
        """Mark the API key as manually configured."""
        self.auto_configured = False
    
    def update_priority(self, priority: int):
        """Update the source priority."""
        if not (1 <= priority <= 10):
            raise ValueError("source_priority must be between 1 and 10")
        self.source_priority = priority
    
    def mark_as_valid(self):
        """Mark the API key as valid."""
        self.is_valid = True
    
    def mark_as_invalid(self):
        """Mark the API key as invalid."""
        self.is_valid = False
    
    def reset_usage_count(self):
        """Reset the usage count."""
        self.usage_count = 0
    
    def is_frequently_used(self, min_usage: int = 10) -> bool:
        """Check if the API key is frequently used."""
        return self.usage_count >= min_usage
    
    def __str__(self) -> str:
        """String representation of the API key."""
        status = "Active" if self.is_active else "Inactive"
        masked_key = self.mask_key()
        return f"TufeApiKey({self.key_name}, {masked_key}, {status})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the API key."""
        masked_key = self.mask_key()
        return (f"TufeApiKey(id={self.id}, key_name='{self.key_name}', "
                f"api_key='{masked_key}', source_id={self.source_id}, "
                f"created_at={self.created_at}, last_used={self.last_used}, "
                f"is_active={self.is_active})")
