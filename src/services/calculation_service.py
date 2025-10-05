"""
Calculation service for rent and exchange rate calculations.
"""
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import date

from src.models import RentalAgreement, ExchangeRate, PaymentRecord, MarketRate
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
        
        rules = agreement.conditional_rules.get("rules", [])
        
        for rule in rules:
            condition_type = rule.get("condition", "")
            
            # Handle new date_range format
            if condition_type == "date_range":
                # Check if we're in the date range period
                if self._is_in_date_range(rule):
                    # Use USD threshold to determine amount
                    if exchange_rate < Decimal(str(rule["usd_threshold"])):
                        return Decimal(str(rule["rent_low"]))
                    else:
                        return Decimal(str(rule["rent_high"]))
                # If not in date range, continue to next rule (or return base amount)
            
            # Handle old format (backward compatibility)
            elif condition_type in ["<", ">", "<=", ">=", "==", "="] or any(condition_type.startswith(op) for op in ["<", ">", "="]):
                if self._evaluate_condition(condition_type, exchange_rate):
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
    
    def _evaluate_date_range_condition(self, rule: dict, exchange_rate: Decimal) -> bool:
        """
        Evaluate a date_range condition.
        
        Args:
            rule: Rule dictionary with date_range condition
            exchange_rate: Current exchange rate
            
        Returns:
            True if the date range condition is applicable
        """
        # For date_range conditions, we always return True if we're in the date range
        # The actual amount calculation is handled by the USD threshold
        return True
    
    def _is_in_date_range(self, rule: dict) -> bool:
        """
        Check if current date is within the specified date range.
        
        Args:
            rule: Rule dictionary with start_date and end_date
            
        Returns:
            True if current date is within the range
        """
        from datetime import date
        
        current_date = date.today()
        start_date = date.fromisoformat(rule["start_date"])
        end_date = date.fromisoformat(rule["end_date"])
        
        return start_date <= current_date <= end_date
    
    def calculate_market_comparison(
        self, 
        user_rent: Decimal, 
        market_rates: List[MarketRate]
    ) -> Dict:
        """
        Compare user's rent with market rates.
        
        Args:
            user_rent: User's current/proposed rent in TL
            market_rates: List of market rental rates
            
        Returns:
            Dictionary with comparison statistics
        """
        if not market_rates:
            return {
                "market_count": 0,
                "market_avg": None,
                "market_min": None,
                "market_max": None,
                "user_vs_avg_percent": None,
                "position": "no_data"
            }
        
        amounts = [rate.amount_tl for rate in market_rates]
        market_avg = sum(amounts) / len(amounts)
        market_min = min(amounts)
        market_max = max(amounts)
        
        user_vs_avg_percent = self.calculate_percentage_increase(market_avg, user_rent)
        
        # Determine position
        if user_rent < market_avg:
            position = "below_average"
        elif user_rent > market_avg:
            position = "above_average"
        else:
            position = "at_average"
        
        return {
            "market_count": len(market_rates),
            "market_avg": market_avg.quantize(Decimal("0.01")),
            "market_min": market_min.quantize(Decimal("0.01")),
            "market_max": market_max.quantize(Decimal("0.01")),
            "user_vs_avg_percent": user_vs_avg_percent,
            "position": position
        }
    
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
            "total_tl": total_tl.quantize(Decimal("0.01")),
            "total_usd": total_usd.quantize(Decimal("0.01")),
            "avg_tl": (total_tl / count).quantize(Decimal("0.01")),
            "avg_usd": (total_usd / count).quantize(Decimal("0.01")),
            "min_tl": min(p.amount_tl for p in payments),
            "max_tl": max(p.amount_tl for p in payments),
            "min_usd": min(p.amount_usd for p in payments),
            "max_usd": max(p.amount_usd for p in payments)
        }

