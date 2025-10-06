"""
TufeData model for representing TÜFE inflation data.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class TufeData:
    """Model for TÜFE (Consumer Price Index) data."""
    
    year: int
    month: int
    inflation_rate_percent: float
    source: str
    fetched_at: datetime
    is_validated: bool = False
    
    def __post_init__(self):
        """Validate the TÜFE data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate the TÜFE data fields."""
        if not (2000 <= self.year <= 2030):
            raise ValueError("year must be between 2000 and 2030")
        
        if not (1 <= self.month <= 12):
            raise ValueError("month must be between 1 and 12")
        
        if self.inflation_rate_percent < 0:
            raise ValueError("inflation_rate_percent cannot be negative")
        
        if not self.source or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        
        if not isinstance(self.is_validated, bool):
            raise ValueError("is_validated must be a boolean")
    
    def to_dict(self) -> dict:
        """Convert the TÜFE data to a dictionary."""
        return {
            'year': self.year,
            'month': self.month,
            'inflation_rate_percent': self.inflation_rate_percent,
            'source': self.source,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'is_validated': self.is_validated
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeData':
        """Create TufeData from a dictionary."""
        fetched_at = None
        if data.get('fetched_at'):
            fetched_at = datetime.fromisoformat(data['fetched_at'])
        
        return cls(
            year=data['year'],
            month=data['month'],
            inflation_rate_percent=data['inflation_rate_percent'],
            source=data['source'],
            fetched_at=fetched_at,
            is_validated=data.get('is_validated', False)
        )
    
    def validate(self):
        """Mark the data as validated."""
        self.is_validated = True
    
    def invalidate(self):
        """Mark the data as not validated."""
        self.is_validated = False
    
    def is_from_tcmb_api(self) -> bool:
        """Check if data is from TCMB API."""
        return 'TCMB' in self.source.upper() or 'EVDS' in self.source.upper()
    
    def get_source_attribution(self) -> str:
        """Get human-readable source attribution."""
        if 'TCMB' in self.source.upper() or 'EVDS' in self.source.upper():
            return "TCMB EVDS API"
        elif 'TUIK' in self.source.upper() or 'TÜİK' in self.source.upper():
            return "TÜİK API"
        elif 'MANUAL' in self.source.upper():
            return "Manual Entry"
        else:
            return self.source
    
    def __str__(self) -> str:
        """String representation of the TÜFE data."""
        return f"TufeData({self.year}-{self.month:02d}, {self.inflation_rate_percent:.2f}%, {self.source})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the TÜFE data."""
        return (f"TufeData(year={self.year}, month={self.month}, "
                f"inflation_rate_percent={self.inflation_rate_percent}, "
                f"source='{self.source}', fetched_at={self.fetched_at}, "
                f"is_validated={self.is_validated})")
