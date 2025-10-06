"""
TufeAutoConfig model for managing zero-configuration setup.
"""

import json
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class TufeAutoConfig:
    """Model for managing zero-configuration TÜFE data fetching setup."""
    
    id: Optional[int] = None
    config_name: str = ""
    auto_discovery_enabled: bool = True
    default_priority_order: List[int] = None
    fallback_to_manual: bool = True
    cache_duration_hours: int = 24
    validation_enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize and validate the auto config."""
        if self.default_priority_order is None:
            self.default_priority_order = []
        
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        self._validate()
    
    def _validate(self):
        """Validate the auto config fields."""
        if not self.config_name or not self.config_name.strip():
            raise ValueError("config_name must be a non-empty string")
        
        if not (1 <= self.cache_duration_hours <= 168):  # 1 hour to 1 week
            raise ValueError("cache_duration_hours must be between 1 and 168 hours")
        
        if not isinstance(self.auto_discovery_enabled, bool):
            raise ValueError("auto_discovery_enabled must be a boolean")
        
        if not isinstance(self.fallback_to_manual, bool):
            raise ValueError("fallback_to_manual must be a boolean")
        
        if not isinstance(self.validation_enabled, bool):
            raise ValueError("validation_enabled must be a boolean")
        
        if not isinstance(self.default_priority_order, list):
            raise ValueError("default_priority_order must be a list")
        
        # Validate that all priority order items are positive integers
        for source_id in self.default_priority_order:
            if not isinstance(source_id, int) or source_id <= 0:
                raise ValueError("All default_priority_order items must be positive integers")
    
    def to_dict(self) -> dict:
        """Convert the auto config to a dictionary."""
        return {
            'id': self.id,
            'config_name': self.config_name,
            'auto_discovery_enabled': self.auto_discovery_enabled,
            'default_priority_order': json.dumps(self.default_priority_order),
            'fallback_to_manual': self.fallback_to_manual,
            'cache_duration_hours': self.cache_duration_hours,
            'validation_enabled': self.validation_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeAutoConfig':
        """Create a TufeAutoConfig from a dictionary."""
        # Parse datetime fields
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        updated_at = None
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
        
        # Parse default priority order
        default_priority_order = []
        if data.get('default_priority_order'):
            try:
                default_priority_order = json.loads(data['default_priority_order'])
            except (json.JSONDecodeError, TypeError):
                default_priority_order = []
        
        return cls(
            id=data.get('id'),
            config_name=data['config_name'],
            auto_discovery_enabled=data.get('auto_discovery_enabled', True),
            default_priority_order=default_priority_order,
            fallback_to_manual=data.get('fallback_to_manual', True),
            cache_duration_hours=data.get('cache_duration_hours', 24),
            validation_enabled=data.get('validation_enabled', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def enable_auto_discovery(self):
        """Enable automatic source discovery."""
        self.auto_discovery_enabled = True
        self.updated_at = datetime.now()
    
    def disable_auto_discovery(self):
        """Disable automatic source discovery."""
        self.auto_discovery_enabled = False
        self.updated_at = datetime.now()
    
    def enable_fallback_to_manual(self):
        """Enable fallback to manual data entry."""
        self.fallback_to_manual = True
        self.updated_at = datetime.now()
    
    def disable_fallback_to_manual(self):
        """Disable fallback to manual data entry."""
        self.fallback_to_manual = False
        self.updated_at = datetime.now()
    
    def enable_validation(self):
        """Enable data validation."""
        self.validation_enabled = True
        self.updated_at = datetime.now()
    
    def disable_validation(self):
        """Disable data validation."""
        self.validation_enabled = False
        self.updated_at = datetime.now()
    
    def set_cache_duration(self, hours: int):
        """Set the cache duration in hours."""
        if not (1 <= hours <= 168):
            raise ValueError("cache_duration_hours must be between 1 and 168 hours")
        
        self.cache_duration_hours = hours
        self.updated_at = datetime.now()
    
    def add_priority_source(self, source_id: int):
        """Add a source to the priority order."""
        if not isinstance(source_id, int) or source_id <= 0:
            raise ValueError("source_id must be a positive integer")
        
        if source_id not in self.default_priority_order:
            self.default_priority_order.append(source_id)
            self.updated_at = datetime.now()
    
    def remove_priority_source(self, source_id: int):
        """Remove a source from the priority order."""
        if source_id in self.default_priority_order:
            self.default_priority_order.remove(source_id)
            self.updated_at = datetime.now()
    
    def set_priority_order(self, priority_order: List[int]):
        """Set the complete priority order."""
        if not isinstance(priority_order, list):
            raise ValueError("priority_order must be a list")
        
        # Validate all items are positive integers
        for source_id in priority_order:
            if not isinstance(source_id, int) or source_id <= 0:
                raise ValueError("All priority_order items must be positive integers")
        
        self.default_priority_order = priority_order.copy()
        self.updated_at = datetime.now()
    
    def get_cache_duration_minutes(self) -> int:
        """Get the cache duration in minutes."""
        return self.cache_duration_hours * 60
    
    def get_cache_duration_seconds(self) -> int:
        """Get the cache duration in seconds."""
        return self.cache_duration_hours * 3600
    
    def is_auto_discovery_enabled(self) -> bool:
        """Check if auto discovery is enabled."""
        return self.auto_discovery_enabled
    
    def is_fallback_to_manual_enabled(self) -> bool:
        """Check if fallback to manual entry is enabled."""
        return self.fallback_to_manual
    
    def is_validation_enabled(self) -> bool:
        """Check if validation is enabled."""
        return self.validation_enabled
    
    def get_priority_source_count(self) -> int:
        """Get the number of sources in the priority order."""
        return len(self.default_priority_order)
    
    def is_configured(self) -> bool:
        """Check if the auto config is properly configured."""
        return (
            bool(self.config_name.strip()) and
            self.cache_duration_hours > 0 and
            isinstance(self.auto_discovery_enabled, bool) and
            isinstance(self.fallback_to_manual, bool) and
            isinstance(self.validation_enabled, bool)
        )
    
    def get_configuration_summary(self) -> dict:
        """Get a summary of the configuration."""
        return {
            'config_name': self.config_name,
            'auto_discovery_enabled': self.auto_discovery_enabled,
            'fallback_to_manual': self.fallback_to_manual,
            'validation_enabled': self.validation_enabled,
            'cache_duration_hours': self.cache_duration_hours,
            'priority_sources_count': len(self.default_priority_order),
            'is_configured': self.is_configured()
        }
    
    def reset_to_defaults(self):
        """Reset the configuration to default values."""
        self.auto_discovery_enabled = True
        self.default_priority_order = []
        self.fallback_to_manual = True
        self.cache_duration_hours = 24
        self.validation_enabled = True
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation of the auto config."""
        auto_discovery = "Enabled" if self.auto_discovery_enabled else "Disabled"
        return f"TufeAutoConfig({self.config_name}, AutoDiscovery: {auto_discovery})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the auto config."""
        return (f"TufeAutoConfig(id={self.id}, config_name='{self.config_name}', "
                f"auto_discovery_enabled={self.auto_discovery_enabled}, "
                f"default_priority_order={self.default_priority_order}, "
                f"fallback_to_manual={self.fallback_to_manual}, "
                f"cache_duration_hours={self.cache_duration_hours}, "
                f"validation_enabled={self.validation_enabled})")
