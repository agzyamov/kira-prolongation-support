"""
InflationData model for storing official Turkish inflation data.
Used to calculate legal maximum rent increases.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class InflationData:
    """
    Represents official Turkish inflation data for a specific month/year.
    Source: TUIK (Turkish Statistical Institute).
    
    Attributes:
        month: Month (1-12)
        year: Year (e.g., 2024)
        inflation_rate_percent: Annual inflation rate as percentage (e.g., 67.5)
        source: Data source (e.g., "TUIK", "Manual Entry")
        id: Database primary key (None for new records)
        notes: Optional notes or metadata
        created_at: Timestamp when record was created
    """
    month: int
    year: int
    inflation_rate_percent: Decimal
    source: str
    id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate inflation data after initialization"""
        # Validate month range
        if not (1 <= self.month <= 12):
            raise ValueError(f"month must be between 1-12, got {self.month}")
        
        # Validate year range
        if self.year < 2000 or self.year > 2100:
            raise ValueError(f"year must be between 2000-2100, got {self.year}")
        
        # Validate inflation rate is non-negative (can be 0 or positive)
        if self.inflation_rate_percent < 0:
            raise ValueError(
                f"inflation_rate_percent cannot be negative, got {self.inflation_rate_percent}"
            )
        
        # Validate source is provided
        if not self.source or not self.source.strip():
            raise ValueError("source must be a non-empty string")
    
    def period_key(self) -> str:
        """Return a sortable period key like '2024-11'"""
        return f"{self.year}-{self.month:02d}"
    
    def legal_max_increase_multiplier(self) -> Decimal:
        """
        Calculate the legal maximum rent increase multiplier.
        
        Example: If inflation is 67.5%, multiplier is 1.675
        (old_rent * 1.675 = new_rent)
        """
        return Decimal("1") + (self.inflation_rate_percent / Decimal("100"))
    
    def get_yearly_tufe(self, year: int) -> Optional[Decimal]:
        """
        Get yearly TÜFE rate for given year.
        
        Args:
            year: Year to get TÜFE for
            
        Returns:
            TÜFE rate as Decimal or None if not available
        """
        if not isinstance(year, int):
            raise ValueError("year must be an integer")
        
        if year < 2000 or year > 2100:
            raise ValueError("year must be between 2000-2100")
        
        # For now, return None as this would typically query a database
        # In a real implementation, this would search for TÜFE data for the given year
        return None
    
    def is_tufe_available(self, year: int) -> bool:
        """
        Check if TÜFE data is available for given year.
        
        Args:
            year: Year to check
            
        Returns:
            True if TÜFE data is available
        """
        if not isinstance(year, int):
            raise ValueError("year must be an integer")
        
        if year < 2000 or year > 2100:
            return False
        
        # For now, return False as this would typically query a database
        # In a real implementation, this would check if TÜFE data exists for the given year
        return False
    
    def is_from_tcmb_api(self) -> bool:
        """Check if this data was fetched from TCMB API."""
        return "TCMB" in self.source.upper() or "EVDS" in self.source.upper()
    
    def get_source_attribution(self) -> str:
        """Get formatted source attribution string."""
        if self.is_from_tcmb_api():
            return "Data source: TCMB EVDS API"
        elif "Manual" in self.source:
            return "Data source: Manual Entry"
        else:
            return f"Data source: {self.source}"
    
    def __repr__(self) -> str:
        return (
            f"InflationData({self.year}-{self.month:02d}, "
            f"{self.inflation_rate_percent}%, "
            f"source={self.source})"
        )

