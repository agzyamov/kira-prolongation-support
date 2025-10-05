"""
Calculation service for rent and exchange rate calculations.
"""
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import date, datetime

from src.models import RentalAgreement, ExchangeRate, PaymentRecord
from src.services.exceptions import CalculationError


class CalculationService:
    """
    Service for performing rental calculations.
    Handles USD conversions, percentage changes, and conditional pricing.
    """
    
    def calculate_usd_equivalent(
        self, 
        amount_tl: Decimal, 
        exchange_rate: Decimal
    ) -> Decimal:
        """
        Convert TL amount to USD.
        
        Args:
            amount_tl: Amount in Turkish Lira
            exchange_rate: TL per 1 USD (e.g., 18.65)
            
        Returns:
            Amount in USD
        """
        if exchange_rate <= 0:
            raise CalculationError(f"Invalid exchange rate: {exchange_rate}")
        
        return amount_tl / exchange_rate
    
    def calculate_percentage_increase(
        self, 
        old_value: Decimal, 
        new_value: Decimal
    ) -> Decimal:
        """
        Calculate percentage increase from old to new value.
        
        Args:
            old_value: Original value
            new_value: New value
            
        Returns:
            Percentage increase (e.g., 66.67 for 66.67% increase)
        """
        if old_value <= 0:
            raise CalculationError(f"old_value must be positive, got {old_value}")
        
        increase = new_value - old_value
        percentage = (increase / old_value) * Decimal("100")
        return percentage.quantize(Decimal("0.01"))
    
    def apply_conditional_rules(
        self, 
        agreement: RentalAgreement, 
        exchange_rate: Decimal
    ) -> Decimal:
        """
        Apply conditional pricing rules to determine actual rent amount.
        
        Args:
            agreement: Rental agreement with potential conditional rules
            exchange_rate: Current exchange rate (TL per USD)
            
        Returns:
            Actual rent amount in TL
            
        Example conditional_rules format:
        {
            "rules": [
                {"condition": "< 40", "amount_tl": 35000},
                {"condition": ">= 40", "amount_tl": 40000}
            ]
        }
        """
        if not agreement.has_conditional_pricing():
            return agreement.base_amount_tl
        
        if not agreement.conditional_rules:
            return agreement.base_amount_tl
            
        rules = agreement.conditional_rules.get("rules", [])
        
        for rule in rules:
            condition = rule.get("condition", "")
            if self._evaluate_condition(condition, exchange_rate):
                return Decimal(str(rule["amount_tl"]))
        
        # No condition matched, return base amount
        return agreement.base_amount_tl
    
    def _evaluate_condition(self, condition: str, rate: Decimal) -> bool:
        """
        Evaluate a conditional pricing rule.
        
        Args:
            condition: Condition string (e.g., "< 40", ">= 40")
            rate: Exchange rate to evaluate
            
        Returns:
            True if condition is met
        """
        condition = condition.strip()
        
        if condition.startswith(">="):
            threshold = Decimal(condition[2:].strip())
            return rate >= threshold
        elif condition.startswith("<="):
            threshold = Decimal(condition[2:].strip())
            return rate <= threshold
        elif condition.startswith(">"):
            threshold = Decimal(condition[1:].strip())
            return rate > threshold
        elif condition.startswith("<"):
            threshold = Decimal(condition[1:].strip())
            return rate < threshold
        elif condition.startswith("==") or condition.startswith("="):
            threshold = Decimal(condition.lstrip("=").strip())
            return rate == threshold
        else:
            raise CalculationError(f"Invalid condition format: {condition}")
    
    
    def calculate_payment_summary(
        self, 
        payments: List[PaymentRecord]
    ) -> Dict:
        """
        Calculate summary statistics for payment records.
        
        Args:
            payments: List of payment records
            
        Returns:
            Dictionary with summary statistics
        """
        if not payments:
            return {
                "count": 0,
                "total_tl": Decimal("0"),
                "total_usd": Decimal("0"),
                "avg_tl": Decimal("0"),
                "avg_usd": Decimal("0"),
                "min_tl": None,
                "max_tl": None,
                "min_usd": None,
                "max_usd": None
            }
        
        total_tl = sum(p.amount_tl for p in payments)
        total_usd = sum(p.amount_usd for p in payments)
        count = len(payments)
        
        return {
            "count": count,
            "total_tl": Decimal(str(total_tl)).quantize(Decimal("0.01")),
            "total_usd": Decimal(str(total_usd)).quantize(Decimal("0.01")),
            "avg_tl": Decimal(str(total_tl / count)).quantize(Decimal("0.01")),
            "avg_usd": Decimal(str(total_usd / count)).quantize(Decimal("0.01")),
            "min_tl": min(p.amount_tl for p in payments),
            "max_tl": max(p.amount_tl for p in payments),
            "min_usd": min(p.amount_usd for p in payments),
            "max_usd": max(p.amount_usd for p in payments)
        }
    
    def get_legal_rule_for_date(self, check_date: datetime) -> str:
        """
        Determine applicable legal rule for given date.
        
        Args:
            check_date: Date to check legal rule for
            
        Returns:
            "25%_cap" for dates up to June 30, 2024
            "cpi_based" for dates after July 1, 2024
        """
        if not isinstance(check_date, (date, datetime)):
            raise ValueError("check_date must be a date or datetime object")
        
        # Convert datetime to date if needed
        if isinstance(check_date, datetime):
            check_date = check_date.date()
        
        # July 1, 2024 is the cutoff date
        cutoff_date = date(2024, 7, 1)
        
        if check_date < cutoff_date:
            return "25%_cap"
        else:
            return "cpi_based"
    
    def get_legal_rule_label(self, check_date: datetime) -> str:
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
    
    def calculate_legal_max_increase(self, agreement: RentalAgreement, check_date: datetime) -> Decimal:
        """
        Calculate legal maximum rent increase for given date.
        
        Args:
            agreement: Rental agreement to calculate for
            check_date: Date to calculate for
            
        Returns:
            Legal maximum increase amount in TL
        """
        if not isinstance(check_date, (date, datetime)):
            raise ValueError("check_date must be a date or datetime object")
        
        # Convert datetime to date if needed
        if isinstance(check_date, datetime):
            check_date = check_date.date()
        
        rule_type = self.get_legal_rule_for_date(check_date)
        
        if rule_type == "25%_cap":
            # 25% cap rule
            return agreement.base_amount_tl * Decimal("0.25")
        else:
            # CPI-based rule - for now, return a placeholder
            # In a real implementation, this would fetch TÜFE data
            return agreement.base_amount_tl * Decimal("0.10")  # Placeholder 10%

