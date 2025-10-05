"""
Validation utilities for Kira Prolongation Support.
Provides input validation functions used across the application.
"""
from datetime import date
from decimal import Decimal
from typing import Optional


class ValidationError(Exception):
    """Raised when data validation fails"""
    pass


def validate_date_range(start_date: date, end_date: Optional[date]) -> bool:
    """
    Validate that start_date is before end_date.
    
    Args:
        start_date: Agreement start date
        end_date: Agreement end date (None for ongoing)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If start_date >= end_date
    """
    if end_date is not None and start_date > end_date:
        raise ValidationError(
            f"start_date ({start_date}) must be before end_date ({end_date})"
        )
    return True


def validate_amount(amount: Decimal) -> bool:
    """
    Validate that monetary amount is positive.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If amount <= 0
    """
    if amount <= 0:
        raise ValidationError(f"amount must be positive, got {amount}")
    return True


def validate_exchange_rate(rate: Decimal) -> bool:
    """
    Validate that exchange rate is positive.
    
    Args:
        rate: Exchange rate to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If rate <= 0
    """
    if rate <= 0:
        raise ValidationError(f"exchange rate must be positive, got {rate}")
    return True


def validate_month(month: int) -> bool:
    """
    Validate that month is in range 1-12.
    
    Args:
        month: Month to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If month not in 1-12
    """
    if not (1 <= month <= 12):
        raise ValidationError(f"month must be between 1-12, got {month}")
    return True


def validate_year(year: int) -> bool:
    """
    Validate that year is in reasonable range.
    
    Args:
        year: Year to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If year < 2000 (too old for Turkish Lira data)
    """
    if year < 2000:
        raise ValidationError(f"year must be >= 2000, got {year}")
    return True


def validate_confidence(confidence: float) -> bool:
    """
    Validate that OCR confidence score is in range 0.0-1.0.
    
    Args:
        confidence: Confidence score to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If confidence not in 0.0-1.0
    """
    if not (0.0 <= confidence <= 1.0):
        raise ValidationError(
            f"confidence must be between 0.0-1.0, got {confidence}"
        )
    return True

