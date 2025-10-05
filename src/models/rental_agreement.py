"""
RentalAgreement model for storing rental agreement data.
Represents a time period with associated rental terms.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict


@dataclass
class RentalAgreement:
    """
    Represents a rental agreement period with pricing terms.
    
    Attributes:
        id: Database primary key (None for new records)
        start_date: Agreement start date (month/year precision)
        end_date: Agreement end date (None for ongoing agreements)
        base_amount_tl: Base monthly rent in Turkish Lira
        conditional_rules: Optional JSON rules for conditional pricing
        notes: Optional user notes about this agreement
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    start_date: date
    base_amount_tl: Decimal
    id: Optional[int] = None
    end_date: Optional[date] = None
    conditional_rules: Optional[Dict] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate rental agreement data after initialization"""
        # Validate base_amount_tl > 0
        if self.base_amount_tl <= 0:
            raise ValueError(f"base_amount_tl must be positive, got {self.base_amount_tl}")
        
        # Validate start_date < end_date (if end_date provided)
        if self.end_date is not None and self.start_date > self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) must be before end_date ({self.end_date})"
            )
    
    def is_ongoing(self) -> bool:
        """Check if this agreement is currently ongoing (no end date)"""
        return self.end_date is None
    
    def has_conditional_pricing(self) -> bool:
        """Check if this agreement has conditional pricing rules"""
        return self.conditional_rules is not None and len(self.conditional_rules) > 0
    
    def __repr__(self) -> str:
        end_str = self.end_date.strftime("%Y-%m") if self.end_date else "ongoing"
        return (
            f"RentalAgreement(id={self.id}, "
            f"{self.start_date.strftime('%Y-%m')} to {end_str}, "
            f"{self.base_amount_tl} TL)"
        )

