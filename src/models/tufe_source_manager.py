"""
TufeSourceManager model for managing source selection and health monitoring.
"""

import json
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class TufeSourceManager:
    """Model for managing TÜFE data source selection and health monitoring."""
    
    id: Optional[int] = None
    name: str = ""
    active_sources: List[int] = None
    health_check_interval: int = 300  # seconds between health checks
    failure_threshold: int = 3  # failures before marking source as failed
    success_threshold: int = 2  # successes before marking source as healthy
    max_retry_attempts: int = 3  # maximum retry attempts per source
    retry_delay: int = 5  # seconds between retry attempts
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize and validate the source manager."""
        if self.active_sources is None:
            self.active_sources = []
        
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        self._validate()
    
    def _validate(self):
        """Validate the source manager fields."""
        if not self.name or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        
        if not (60 <= self.health_check_interval <= 3600):
            raise ValueError("health_check_interval must be between 60 and 3600 seconds")
        
        if not (1 <= self.failure_threshold <= 10):
            raise ValueError("failure_threshold must be between 1 and 10")
        
        if not (1 <= self.success_threshold <= 10):
            raise ValueError("success_threshold must be between 1 and 10")
        
        if not (1 <= self.max_retry_attempts <= 5):
            raise ValueError("max_retry_attempts must be between 1 and 5")
        
        if not (1 <= self.retry_delay <= 60):
            raise ValueError("retry_delay must be between 1 and 60 seconds")
        
        if not isinstance(self.active_sources, list):
            raise ValueError("active_sources must be a list")
        
        # Validate that all active sources are positive integers
        for source_id in self.active_sources:
            if not isinstance(source_id, int) or source_id <= 0:
                raise ValueError("All active_sources must be positive integers")
    
    def to_dict(self) -> dict:
        """Convert the source manager to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'active_sources': json.dumps(self.active_sources),
            'health_check_interval': self.health_check_interval,
            'failure_threshold': self.failure_threshold,
            'success_threshold': self.success_threshold,
            'max_retry_attempts': self.max_retry_attempts,
            'retry_delay': self.retry_delay,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeSourceManager':
        """Create a TufeSourceManager from a dictionary."""
        # Parse datetime fields
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        updated_at = None
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
        
        # Parse active sources
        active_sources = []
        if data.get('active_sources'):
            try:
                active_sources = json.loads(data['active_sources'])
            except (json.JSONDecodeError, TypeError):
                active_sources = []
        
        return cls(
            id=data.get('id'),
            name=data['name'],
            active_sources=active_sources,
            health_check_interval=data.get('health_check_interval', 300),
            failure_threshold=data.get('failure_threshold', 3),
            success_threshold=data.get('success_threshold', 2),
            max_retry_attempts=data.get('max_retry_attempts', 3),
            retry_delay=data.get('retry_delay', 5),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def add_active_source(self, source_id: int):
        """Add a source to the active sources list."""
        if not isinstance(source_id, int) or source_id <= 0:
            raise ValueError("source_id must be a positive integer")
        
        if source_id not in self.active_sources:
            self.active_sources.append(source_id)
            self.updated_at = datetime.now()
    
    def remove_active_source(self, source_id: int):
        """Remove a source from the active sources list."""
        if source_id in self.active_sources:
            self.active_sources.remove(source_id)
            self.updated_at = datetime.now()
    
    def is_source_active(self, source_id: int) -> bool:
        """Check if a source is in the active sources list."""
        return source_id in self.active_sources
    
    def get_active_sources_count(self) -> int:
        """Get the number of active sources."""
        return len(self.active_sources)
    
    def clear_active_sources(self):
        """Clear all active sources."""
        self.active_sources.clear()
        self.updated_at = datetime.now()
    
    def update_health_check_interval(self, interval: int):
        """Update the health check interval."""
        if not (60 <= interval <= 3600):
            raise ValueError("health_check_interval must be between 60 and 3600 seconds")
        
        self.health_check_interval = interval
        self.updated_at = datetime.now()
    
    def update_failure_threshold(self, threshold: int):
        """Update the failure threshold."""
        if not (1 <= threshold <= 10):
            raise ValueError("failure_threshold must be between 1 and 10")
        
        self.failure_threshold = threshold
        self.updated_at = datetime.now()
    
    def update_success_threshold(self, threshold: int):
        """Update the success threshold."""
        if not (1 <= threshold <= 10):
            raise ValueError("success_threshold must be between 1 and 10")
        
        self.success_threshold = threshold
        self.updated_at = datetime.now()
    
    def update_max_retry_attempts(self, attempts: int):
        """Update the maximum retry attempts."""
        if not (1 <= attempts <= 5):
            raise ValueError("max_retry_attempts must be between 1 and 5")
        
        self.max_retry_attempts = attempts
        self.updated_at = datetime.now()
    
    def update_retry_delay(self, delay: int):
        """Update the retry delay."""
        if not (1 <= delay <= 60):
            raise ValueError("retry_delay must be between 1 and 60 seconds")
        
        self.retry_delay = delay
        self.updated_at = datetime.now()
    
    def get_health_check_interval_minutes(self) -> float:
        """Get the health check interval in minutes."""
        return self.health_check_interval / 60.0
    
    def get_retry_delay_minutes(self) -> float:
        """Get the retry delay in minutes."""
        return self.retry_delay / 60.0
    
    def is_configured(self) -> bool:
        """Check if the source manager is properly configured."""
        return (
            bool(self.name.strip()) and
            len(self.active_sources) > 0 and
            self.health_check_interval > 0 and
            self.failure_threshold > 0 and
            self.success_threshold > 0 and
            self.max_retry_attempts > 0 and
            self.retry_delay > 0
        )
    
    def get_configuration_summary(self) -> dict:
        """Get a summary of the configuration."""
        return {
            'name': self.name,
            'active_sources_count': len(self.active_sources),
            'health_check_interval_minutes': self.get_health_check_interval_minutes(),
            'failure_threshold': self.failure_threshold,
            'success_threshold': self.success_threshold,
            'max_retry_attempts': self.max_retry_attempts,
            'retry_delay_seconds': self.retry_delay,
            'is_configured': self.is_configured()
        }
    
    def __str__(self) -> str:
        """String representation of the source manager."""
        sources_count = len(self.active_sources)
        return f"TufeSourceManager({self.name}, {sources_count} sources)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the source manager."""
        return (f"TufeSourceManager(id={self.id}, name='{self.name}', "
                f"active_sources={self.active_sources}, "
                f"health_check_interval={self.health_check_interval}, "
                f"failure_threshold={self.failure_threshold}, "
                f"success_threshold={self.success_threshold}, "
                f"max_retry_attempts={self.max_retry_attempts}, "
                f"retry_delay={self.retry_delay})")
