"""
ExchangeRate model for storing historical USD/TRY exchange rate data.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ExchangeRate:
    """
    Represents a USD/TRY exchange rate for a specific month/year.
    Uses monthly average rates for calculations.
    
    Attributes:
        month: Month (1-12)
        year: Year (e.g., 2024)
        rate_tl_per_usd: How many TL for 1 USD (e.g., 18.65 means 1 USD = 18.65 TL)
        source: Data source (e.g., "TCMB", "ExchangeRate-API")
        id: Database primary key (None for new records)
        notes: Optional metadata or notes
        created_at: Timestamp when record was created
    """
    month: int
    year: int
    rate_tl_per_usd: Decimal
    source: str
    id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate exchange rate data after initialization"""
        # Validate month range
        if not (1 <= self.month <= 12):
            raise ValueError(f"month must be between 1-12, got {self.month}")
        
        # Validate year range (reasonable years)
        if self.year < 2000 or self.year > 2100:
            raise ValueError(f"year must be between 2000-2100, got {self.year}")
        
        # Validate rate is positive
        if self.rate_tl_per_usd <= 0:
            raise ValueError(
                f"rate_tl_per_usd must be positive, got {self.rate_tl_per_usd}"
            )
        
        # Validate source is provided
        if not self.source or not self.source.strip():
            raise ValueError("source must be a non-empty string")
    
    def period_key(self) -> str:
        """Return a sortable period key like '2024-11'"""
        return f"{self.year}-{self.month:02d}"
    
    def __repr__(self) -> str:
        return (
            f"ExchangeRate({self.year}-{self.month:02d}, "
            f"1 USD = {self.rate_tl_per_usd} TL, "
            f"source={self.source})"
        )

