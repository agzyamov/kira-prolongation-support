"""
TufeDataSource model for managing TÜFE data sources.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class TufeDataSource:
    """Model for TÜFE data sources."""
    
    id: Optional[int] = None
    source_name: str = ""
    api_endpoint: str = ""
    series_code: str = ""
    data_format: str = "json"
    requires_auth: bool = True
    rate_limit_per_hour: int = 100
    last_verified: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the data source after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate the data source fields."""
        if not self.source_name or not self.source_name.strip():
            raise ValueError("source_name must be a non-empty string")
        
        if not self.api_endpoint or not self.api_endpoint.strip():
            raise ValueError("api_endpoint must be a non-empty string")
        
        if not self.api_endpoint.startswith(('http://', 'https://')):
            raise ValueError("api_endpoint must be a valid URL starting with http:// or https://")
        
        if not self.series_code or not self.series_code.strip():
            raise ValueError("series_code must be a non-empty string")
        
        if self.data_format not in ['json', 'xml']:
            raise ValueError("data_format must be 'json' or 'xml'")
        
        if self.rate_limit_per_hour <= 0:
            raise ValueError("rate_limit_per_hour must be a positive integer")
        
        if not isinstance(self.requires_auth, bool):
            raise ValueError("requires_auth must be a boolean")
        
        if not isinstance(self.is_active, bool):
            raise ValueError("is_active must be a boolean")
    
    def to_dict(self) -> dict:
        """Convert the data source to a dictionary."""
        return {
            'id': self.id,
            'source_name': self.source_name,
            'api_endpoint': self.api_endpoint,
            'series_code': self.series_code,
            'data_format': self.data_format,
            'requires_auth': self.requires_auth,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'last_verified': self.last_verified.isoformat() if self.last_verified else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeDataSource':
        """Create a TufeDataSource from a dictionary."""
        # Parse datetime fields
        last_verified = None
        if data.get('last_verified'):
            last_verified = datetime.fromisoformat(data['last_verified'])
        
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            id=data.get('id'),
            source_name=data['source_name'],
            api_endpoint=data['api_endpoint'],
            series_code=data['series_code'],
            data_format=data.get('data_format', 'json'),
            requires_auth=data.get('requires_auth', True),
            rate_limit_per_hour=data.get('rate_limit_per_hour', 100),
            last_verified=last_verified,
            is_active=data.get('is_active', True),
            created_at=created_at
        )
    
    def update_verification(self, verified_at: datetime = None):
        """Update the last verification timestamp."""
        if verified_at is None:
            verified_at = datetime.now()
        self.last_verified = verified_at
    
    def activate(self):
        """Activate the data source."""
        self.is_active = True
    
    def deactivate(self):
        """Deactivate the data source."""
        self.is_active = False
    
    def is_verified(self) -> bool:
        """Check if the data source has been verified."""
        return self.last_verified is not None
    
    def get_verification_age_days(self) -> Optional[int]:
        """Get the age of the last verification in days."""
        if self.last_verified is None:
            return None
        
        delta = datetime.now() - self.last_verified
        return delta.days
    
    def needs_verification(self, max_age_days: int = 30) -> bool:
        """Check if the data source needs verification."""
        if not self.is_verified():
            return True
        
        age_days = self.get_verification_age_days()
        return age_days is not None and age_days > max_age_days
    
    def __str__(self) -> str:
        """String representation of the data source."""
        status = "Active" if self.is_active else "Inactive"
        verified = "Verified" if self.is_verified() else "Not Verified"
        return f"TufeDataSource({self.source_name}, {status}, {verified})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the data source."""
        return (f"TufeDataSource(id={self.id}, source_name='{self.source_name}', "
                f"api_endpoint='{self.api_endpoint}', series_code='{self.series_code}', "
                f"data_format='{self.data_format}', requires_auth={self.requires_auth}, "
                f"rate_limit_per_hour={self.rate_limit_per_hour}, "
                f"last_verified={self.last_verified}, is_active={self.is_active}, "
                f"created_at={self.created_at})")
