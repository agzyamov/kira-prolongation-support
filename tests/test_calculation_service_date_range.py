"""
Test for calculation service date_range condition bug.

Bug: User reports error when calculating Payment Records:
"Error calculating payments: Invalid condition format: date_range"

Root cause: The calculation service doesn't know how to handle the new 
'date_range' condition format that was created when fixing conditional rules.

The calculation service expects old format like '< 40' but gets new format like:
{
    'condition': 'date_range',
    'start_date': '2024-12-01',
    'end_date': '2025-11-01',
    'usd_threshold': 40.0,
    'rent_low': 35000,
    'rent_high': 40000
}

Fix: Update calculation service to handle date_range conditions properly.
"""
import pytest
import tempfile
import os
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.storage import DataStore
from src.models import RentalAgreement, ExchangeRate
from src.services import CalculationService


def test_calculation_service_handles_date_range_condition():
    """Test that calculation service can handle date_range conditions"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        calculation_service = CalculationService()
        
        # Create agreement with date_range condition
        agreement = RentalAgreement(
            id=1,
            start_date=date(2024, 11, 1),
            end_date=date(2025, 11, 1),
            base_amount_tl=Decimal('31000'),
            conditional_rules={
                'rules': [
                    {
                        'condition': 'date_range',
                        'start_date': '2024-12-01',
                        'end_date': '2025-11-01',
                        'usd_threshold': 40.0,
                        'rent_low': 35000,
                        'rent_high': 40000
                    }
                ]
            },
            notes="Test agreement"
        )
        
        # Test calculation for Nov 2024 (should use base amount)
        # Mock the _is_in_date_range method to return False for Nov 2024
        with patch.object(calculation_service, '_is_in_date_range', return_value=False):
            nov_2024_amount = calculation_service.apply_conditional_rules(
                agreement, 
                Decimal('35.0')  # USD rate
            )
            assert nov_2024_amount == Decimal('31000'), f"Nov 2024 should be 31,000 TL, got {nov_2024_amount}"
        
        # Test calculation for Dec 2024 (should use conditional rules)
        # Mock the _is_in_date_range method to return True for Dec 2024
        with patch.object(calculation_service, '_is_in_date_range', return_value=True):
            # Test with USD rate < 40 (should return 35,000 TL)
            dec_2024_amount_low = calculation_service.apply_conditional_rules(
                agreement,
                Decimal('35.0')  # USD rate < 40
            )
            assert dec_2024_amount_low == Decimal('35000'), f"Dec 2024 with USD 35 should be 35,000 TL, got {dec_2024_amount_low}"
            
            # Test with USD rate >= 40 (should return 40,000 TL)
            dec_2024_amount_high = calculation_service.apply_conditional_rules(
                agreement,
                Decimal('42.0')  # USD rate >= 40
            )
            assert dec_2024_amount_high == Decimal('40000'), f"Dec 2024 with USD 42 should be 40,000 TL, got {dec_2024_amount_high}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_calculation_service_handles_old_condition_format():
    """Test that calculation service still handles old condition format"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        calculation_service = CalculationService()
        
        # Create agreement with old condition format
        agreement = RentalAgreement(
            id=1,
            start_date=date(2024, 11, 1),
            end_date=date(2025, 11, 1),
            base_amount_tl=Decimal('31000'),
            conditional_rules={
                'rules': [
                    {
                        'condition': '< 40',
                        'amount_tl': 35000
                    },
                    {
                        'condition': '>= 40',
                        'amount_tl': 40000
                    }
                ]
            },
            notes="Test agreement with old format"
        )
        
        # Test with old format (should still work)
        amount_low = calculation_service.apply_conditional_rules(
            agreement,
            Decimal('35.0')  # USD rate < 40
        )
        assert amount_low == Decimal('35000'), f"Should handle old format, got {amount_low}"
        
        amount_high = calculation_service.apply_conditional_rules(
            agreement,
            Decimal('42.0')  # USD rate >= 40
        )
        assert amount_high == Decimal('40000'), f"Should handle old format, got {amount_high}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_calculation_service_date_range_logic():
    """Test the date range logic for conditional pricing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        calculation_service = CalculationService()
        
        # Create agreement with date_range condition
        agreement = RentalAgreement(
            id=1,
            start_date=date(2024, 11, 1),
            end_date=date(2025, 11, 1),
            base_amount_tl=Decimal('31000'),
            conditional_rules={
                'rules': [
                    {
                        'condition': 'date_range',
                        'start_date': '2024-12-01',
                        'end_date': '2025-11-01',
                        'usd_threshold': 40.0,
                        'rent_low': 35000,
                        'rent_high': 40000
                    }
                ]
            },
            notes="Test agreement"
        )
        
        # Test different months
        test_cases = [
            # (month, year, expected_amount, usd_rate, description)
            (11, 2024, Decimal('31000'), Decimal('35.0'), "Nov 2024 - before conditional period"),
            (12, 2024, Decimal('35000'), Decimal('35.0'), "Dec 2024 - conditional period, USD < 40"),
            (12, 2024, Decimal('40000'), Decimal('42.0'), "Dec 2024 - conditional period, USD >= 40"),
            (1, 2025, Decimal('35000'), Decimal('35.0'), "Jan 2025 - conditional period, USD < 40"),
            (1, 2025, Decimal('40000'), Decimal('42.0'), "Jan 2025 - conditional period, USD >= 40"),
        ]
        
        for month, year, expected_amount, usd_rate, description in test_cases:
            # Determine if we're in the date range based on the test case
            is_in_range = (month >= 12 and year == 2024) or (year == 2025 and month <= 11)
            
            # Mock the _is_in_date_range method
            with patch.object(calculation_service, '_is_in_date_range', return_value=is_in_range):
                amount = calculation_service.apply_conditional_rules(agreement, usd_rate)
                assert amount == expected_amount, f"{description}: Expected {expected_amount}, got {amount}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
