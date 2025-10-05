"""
LegalRule model for storing legal rent increase rules.
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class LegalRule:
    """
    Immutable model for legal rent increase rules.
    
    Attributes:
        rule_type: Type of rule ("25%_cap" or "cpi_based")
        effective_start: When the rule becomes effective
        effective_end: When the rule expires (None for current rules)
        rate: Fixed rate for 25% cap, None for CPI-based
        label: Human-readable description
    """
    
    rule_type: str
    effective_start: date
    effective_end: Optional[date]
    rate: Optional[Decimal]
    label: str
    
    def __post_init__(self):
        """Validate the legal rule after initialization."""
        if self.rule_type not in ["25%_cap", "cpi_based"]:
            raise ValueError(f"Invalid rule type: {self.rule_type}. Must be '25%_cap' or 'cpi_based'.")
        
        if not isinstance(self.effective_start, date):
            raise ValueError("effective_start must be a date object")
        
        if self.effective_end is not None and not isinstance(self.effective_end, date):
            raise ValueError("effective_end must be a date object or None")
        
        if self.effective_end is not None and self.effective_start > self.effective_end:
            raise ValueError("effective_start must be before effective_end")
        
        if self.rate is not None and self.rate <= 0:
            raise ValueError("rate must be positive if provided")
        
        if not isinstance(self.label, str) or len(self.label.strip()) == 0:
            raise ValueError("label must be a non-empty string")
    
    def is_applicable_for_date(self, check_date: date) -> bool:
        """
        Check if this rule applies to the given date.
        
        Args:
            check_date: Date to check
            
        Returns:
            True if the rule applies to the given date
        """
        if not isinstance(check_date, date):
            raise ValueError("check_date must be a date object")
        
        if check_date < self.effective_start:
            return False
        
        if self.effective_end is None:
            return True
        
        return check_date <= self.effective_end
    
    def get_display_label(self) -> str:
        """
        Get formatted label for UI display.
        
        Returns:
            Formatted label string
        """
        return self.label
    
    def is_25_percent_cap(self) -> bool:
        """Check if this is a 25% cap rule."""
        return self.rule_type == "25%_cap"
    
    def is_cpi_based(self) -> bool:
        """Check if this is a CPI-based rule."""
        return self.rule_type == "cpi_based"
    
    def get_rate(self) -> Optional[Decimal]:
        """
        Get the rate for this rule.
        
        Returns:
            Rate as Decimal for 25% cap rules, None for CPI-based rules
        """
        return self.rate
    
    @classmethod
    def create_25_percent_cap(cls, effective_start: date, effective_end: date) -> "LegalRule":
        """
        Create a 25% cap rule.
        
        Args:
            effective_start: When the rule becomes effective
            effective_end: When the rule expires
            
        Returns:
            LegalRule instance for 25% cap
        """
        return cls(
            rule_type="25%_cap",
            effective_start=effective_start,
            effective_end=effective_end,
            rate=Decimal("25.00"),
            label="+25% (limit until July 2024)"
        )
    
    @classmethod
    def create_cpi_based(cls, effective_start: date) -> "LegalRule":
        """
        Create a CPI-based rule.
        
        Args:
            effective_start: When the rule becomes effective
            
        Returns:
            LegalRule instance for CPI-based rule
        """
        return cls(
            rule_type="cpi_based",
            effective_start=effective_start,
            effective_end=None,
            rate=None,
            label="+CPI (Yearly TÜFE)"
        )
