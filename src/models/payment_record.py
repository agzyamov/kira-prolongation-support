"""
PaymentRecord model for storing calculated payment data.
Links rental agreements with exchange rates.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


@dataclass
class PaymentRecord:
    """
    Represents a calculated payment for a specific month.
    Derived from rental agreement + exchange rate.
    
    Attributes:
        agreement_id: Foreign key to rental_agreements table
        month: Payment month (1-12)
        year: Payment year (e.g., 2024)
        amount_tl: Rent amount in Turkish Lira
        amount_usd: Rent amount in USD (calculated using monthly avg rate)
        exchange_rate_id: Foreign key to exchange_rates table
        id: Database primary key (None for new records)
        payment_date: Optional specific payment date (for tracking)
        notes: Optional notes about this payment
        created_at: Timestamp when record was created
    """
    agreement_id: int
    month: int
    year: int
    amount_tl: Decimal
    amount_usd: Decimal
    exchange_rate_id: int
    id: Optional[int] = None
    payment_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate payment record data after initialization"""
        # Validate month range
        if not (1 <= self.month <= 12):
            raise ValueError(f"month must be between 1-12, got {self.month}")
        
        # Validate year range
        if self.year < 2000 or self.year > 2100:
            raise ValueError(f"year must be between 2000-2100, got {self.year}")
        
        # Validate amounts are positive
        if self.amount_tl <= 0:
            raise ValueError(f"amount_tl must be positive, got {self.amount_tl}")
        
        if self.amount_usd <= 0:
            raise ValueError(f"amount_usd must be positive, got {self.amount_usd}")
        
        # Validate foreign keys are positive
        if self.agreement_id <= 0:
            raise ValueError(f"agreement_id must be positive, got {self.agreement_id}")
        
        if self.exchange_rate_id <= 0:
            raise ValueError(
                f"exchange_rate_id must be positive, got {self.exchange_rate_id}"
            )
    
    def period_key(self) -> str:
        """Return a sortable period key like '2024-11'"""
        return f"{self.year}-{self.month:02d}"
    
    def tl_to_usd_rate(self) -> Decimal:
        """Calculate the implied TL/USD rate from this payment record"""
        if self.amount_usd == 0:
            raise ValueError("Cannot calculate rate: amount_usd is zero")
        return self.amount_tl / self.amount_usd
    
    def __repr__(self) -> str:
        return (
            f"PaymentRecord({self.year}-{self.month:02d}, "
            f"{self.amount_tl} TL = ${self.amount_usd} USD)"
        )

