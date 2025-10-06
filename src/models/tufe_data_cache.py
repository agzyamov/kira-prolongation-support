"""
TufeDataCache model for managing TÜFE data cache.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass


@dataclass
class TufeDataCache:
    """Enhanced model for TÜFE data cache with TTL support."""
    
    id: Optional[int] = None
    year: int = 0
    month: int = 1  # Added month field
    tufe_rate: Decimal = Decimal("0.00")
    source_name: str = ""
    fetched_at: datetime = None
    expires_at: datetime = None
    api_response: str = ""
    is_validated: bool = False
    created_at: Optional[datetime] = None
    
    # Enhanced TTL fields
    fetch_duration: Optional[float] = None  # Time taken to fetch data in seconds
    retry_count: int = 0  # Number of retries for this cache entry
    cache_hit_count: int = 0  # Number of times this entry was accessed
    last_accessed: Optional[datetime] = None  # Last time this entry was accessed
    
    def __post_init__(self):
        """Validate the cache entry after initialization."""
        self._validate()
        if self.fetched_at is None:
            self.fetched_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.fetched_at + timedelta(hours=24)
    
    def _validate(self):
        """Validate the cache entry fields."""
        if not (2000 <= self.year <= 2100):
            raise ValueError("year must be between 2000 and 2100")
        
        if not (1 <= self.month <= 12):
            raise ValueError("month must be between 1 and 12")
        
        if self.tufe_rate < 0:
            raise ValueError("tufe_rate must be non-negative")
        
        if not self.source_name or not self.source_name.strip():
            raise ValueError("source_name must be a non-empty string")
        
        if not isinstance(self.is_validated, bool):
            raise ValueError("is_validated must be a boolean")
        
        if self.fetch_duration is not None and self.fetch_duration < 0:
            raise ValueError("fetch_duration must be non-negative")
        
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        
        if self.cache_hit_count < 0:
            raise ValueError("cache_hit_count must be non-negative")
    
    def to_dict(self) -> dict:
        """Convert the cache entry to a dictionary."""
        return {
            'id': self.id,
            'year': self.year,
            'tufe_rate': str(self.tufe_rate),
            'source_name': self.source_name,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'api_response': self.api_response,
            'is_validated': self.is_validated,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeDataCache':
        """Create a TufeDataCache from a dictionary."""
        # Parse datetime fields
        fetched_at = None
        if data.get('fetched_at'):
            fetched_at = datetime.fromisoformat(data['fetched_at'])
        
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'])
        
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            id=data.get('id'),
            year=data['year'],
            tufe_rate=Decimal(data['tufe_rate']),
            source_name=data['source_name'],
            fetched_at=fetched_at,
            expires_at=expires_at,
            api_response=data.get('api_response', ''),
            is_validated=data.get('is_validated', False),
            created_at=created_at
        )
    
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the cache entry is valid (not expired and validated)."""
        return not self.is_expired() and self.is_validated
    
    def get_age_hours(self) -> float:
        """Get the age of the cache entry in hours."""
        if self.fetched_at is None:
            return 0.0
        
        delta = datetime.now() - self.fetched_at
        return delta.total_seconds() / 3600
    
    def get_remaining_hours(self) -> float:
        """Get the remaining hours until expiration."""
        if self.expires_at is None:
            return 0.0
        
        delta = self.expires_at - datetime.now()
        return max(0.0, delta.total_seconds() / 3600)
    
    def extend_expiration(self, hours: int = 24):
        """Extend the expiration time by the specified hours."""
        if self.expires_at is None:
            self.expires_at = datetime.now() + timedelta(hours=hours)
        else:
            self.expires_at += timedelta(hours=hours)
    
    def mark_as_validated(self):
        """Mark the cache entry as validated."""
        self.is_validated = True
    
    def mark_as_invalidated(self):
        """Mark the cache entry as invalidated."""
        self.is_validated = False
    
    def get_source_attribution(self) -> str:
        """Get formatted source attribution string."""
        return f"Data source: {self.source_name}"
    
    def is_ttl_expired(self) -> bool:
        """Check if the TTL has expired."""
        return self.is_expired()
    
    def get_ttl_remaining(self) -> timedelta:
        """Get remaining TTL time."""
        if self.expires_at:
            remaining = self.expires_at - datetime.now()
            return max(timedelta(0), remaining)
        return timedelta(0)
    
    def extend_ttl(self, hours: int) -> None:
        """Extend the TTL by specified hours."""
        self.extend_expiration(hours)
    
    def mark_accessed(self) -> None:
        """Mark this cache entry as accessed."""
        self.cache_hit_count += 1
        self.last_accessed = datetime.now()
    
    def get_cache_efficiency(self) -> float:
        """Get cache efficiency score (hits per hour)."""
        if not self.fetched_at or self.cache_hit_count == 0:
            return 0.0
        
        hours_since_fetch = (datetime.now() - self.fetched_at).total_seconds() / 3600
        if hours_since_fetch == 0:
            return 0.0
        
        return self.cache_hit_count / hours_since_fetch
    
    def get_data_lineage(self) -> str:
        """Get formatted data lineage string."""
        fetched_str = self.fetched_at.strftime("%Y-%m-%d %H:%M") if self.fetched_at else "Unknown"
        return f"TÜFE data for {self.year}: {self.tufe_rate}% from {self.source_name} (fetched: {fetched_str})"
    
    def get_cache_status(self) -> str:
        """Get the cache status string."""
        if self.is_expired():
            return "Expired"
        elif not self.is_validated:
            return "Unvalidated"
        else:
            return "Valid"
    
    def get_remaining_time_str(self) -> str:
        """Get a human-readable string of remaining time."""
        remaining_hours = self.get_remaining_hours()
        if remaining_hours <= 0:
            return "Expired"
        elif remaining_hours < 1:
            minutes = int(remaining_hours * 60)
            return f"{minutes} minutes"
        elif remaining_hours < 24:
            hours = int(remaining_hours)
            return f"{hours} hours"
        else:
            days = int(remaining_hours / 24)
            return f"{days} days"
    
    def __str__(self) -> str:
        """String representation of the cache entry."""
        status = self.get_cache_status()
        return f"TufeDataCache({self.year}: {self.tufe_rate}%, {self.source_name}, {status})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the cache entry."""
        return (f"TufeDataCache(id={self.id}, year={self.year}, "
                f"tufe_rate={self.tufe_rate}, source_name='{self.source_name}', "
                f"fetched_at={self.fetched_at}, expires_at={self.expires_at}, "
                f"api_response='{self.api_response[:50]}...', "
                f"is_validated={self.is_validated}, created_at={self.created_at})")
