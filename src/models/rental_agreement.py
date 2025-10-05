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
    
    def get_legal_rule_for_date(self, check_date: date) -> str:
        """
        Get applicable legal rule for given date.
        
        Args:
            check_date: Date to check legal rule for
            
        Returns:
            "25%_cap" for dates up to June 30, 2024
            "cpi_based" for dates after July 1, 2024
        """
        if not isinstance(check_date, date):
            raise ValueError("check_date must be a date object")
        
        # July 1, 2024 is the cutoff date
        cutoff_date = date(2024, 7, 1)
        
        if check_date < cutoff_date:
            return "25%_cap"
        else:
            return "cpi_based"
    
    def get_legal_rule_label(self, check_date: date) -> str:
        """
        Get human-readable label for legal rule applicable to given date.
        
        Args:
            check_date: Date to get label for
            
        Returns:
            "+25% (limit until July 2024)" or "+CPI (Yearly TÜFE)"
        """
        rule_type = self.get_legal_rule_for_date(check_date)
        
        if rule_type == "25%_cap":
            return "+25% (limit until July 2024)"
        else:
            return "+CPI (Yearly TÜFE)"
    
    def __repr__(self) -> str:
        end_str = self.end_date.strftime("%Y-%m") if self.end_date else "ongoing"
        return (
            f"RentalAgreement(id={self.id}, "
            f"{self.start_date.strftime('%Y-%m')} to {end_str}, "
            f"{self.base_amount_tl} TL)"
        )

