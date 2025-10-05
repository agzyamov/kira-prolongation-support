"""
Test for November chart spikes bug.

Bug: User reports "something strange happens to the chart each November" - 
there are "V" shaped spikes in the USD equivalent line every November.

Root cause: The _is_in_date_range method uses the current date (October 2025) 
to determine if we're in the conditional period, but it should use the 
payment date for each specific month being calculated.

This causes:
- Nov 2024: Should use base amount (31,000 TL) but incorrectly applies conditional rules
- Dec 2024: Should use conditional rules but may be calculated incorrectly
- The spikes happen because the calculation is inconsistent with the actual agreement terms

Fix: Update the calculation logic to use the payment date instead of current date
when determining which rules apply for each month.
"""
import pytest
import tempfile
import os
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.storage import DataStore
from src.models import RentalAgreement, ExchangeRate, PaymentRecord
from src.services import CalculationService


def test_november_2024_uses_base_amount():
    """Test that November 2024 uses base amount, not conditional rules"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        calculation_service = CalculationService()
        
        # Create agreement with conditional rules starting Dec 2024
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
        
        # Test November 2024 - should use base amount regardless of current date
        # Even if we're currently in October 2025, Nov 2024 should use 31,000 TL
        nov_2024_amount = calculation_service.apply_conditional_rules_for_date(
            agreement, 
            Decimal('35.0'),  # USD rate
            date(2024, 11, 1)  # Payment date
        )
        assert nov_2024_amount == Decimal('31000'), f"Nov 2024 should be 31,000 TL, got {nov_2024_amount}"
        
        # Test December 2024 - should use conditional rules
        dec_2024_amount = calculation_service.apply_conditional_rules_for_date(
            agreement,
            Decimal('35.0'),  # USD rate < 40
            date(2024, 12, 1)  # Payment date
        )
        assert dec_2024_amount == Decimal('35000'), f"Dec 2024 should be 35,000 TL, got {dec_2024_amount}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_payment_calculation_uses_correct_date():
    """Test that payment calculation uses the payment date, not current date"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        calculation_service = CalculationService()
        
        # Create agreement
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
        
        # Test different months with same USD rate
        test_cases = [
            # (payment_date, expected_amount, description)
            (date(2024, 11, 1), Decimal('31000'), "Nov 2024 - base amount"),
            (date(2024, 12, 1), Decimal('35000'), "Dec 2024 - conditional (USD < 40)"),
            (date(2025, 1, 1), Decimal('35000'), "Jan 2025 - conditional (USD < 40)"),
            (date(2025, 11, 1), Decimal('35000'), "Nov 2025 - conditional (USD < 40)"),
        ]
        
        for payment_date, expected_amount, description in test_cases:
            amount = calculation_service.apply_conditional_rules_for_date(
                agreement,
                Decimal('35.0'),  # USD rate < 40
                payment_date
            )
            assert amount == expected_amount, f"{description}: Expected {expected_amount}, got {amount}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_no_november_spikes_in_chart():
    """Test that chart generation doesn't create November spikes"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create agreement
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
        
        data_store.save_rental_agreement(agreement)
        
        # Add exchange rates
        exchange_rates = [
            ExchangeRate(month=11, year=2024, rate_tl_per_usd=Decimal('34.0'), source='TCMB'),
            ExchangeRate(month=12, year=2024, rate_tl_per_usd=Decimal('35.0'), source='TCMB'),
            ExchangeRate(month=1, year=2025, rate_tl_per_usd=Decimal('36.0'), source='TCMB'),
        ]
        
        for rate in exchange_rates:
            data_store.save_exchange_rate(rate)
        
        # Generate payment records
        calculation_service = CalculationService()
        
        # Simulate the payment calculation logic that should be used
        payments = []
        current_date = agreement.start_date
        end_date = min(agreement.end_date or date.today(), date.today())
        
        while current_date <= end_date:
            # Get exchange rate for this month
            rate = data_store.get_exchange_rate(current_date.month, current_date.year)
            if rate:
                # Calculate amount using the payment date, not current date
                amount_tl = calculation_service.apply_conditional_rules_for_date(
                    agreement,
                    rate.rate_tl_per_usd,
                    current_date  # Use payment date
                )
                
                # Calculate USD equivalent
                amount_usd = calculation_service.calculate_usd_equivalent(
                    amount_tl,
                    rate.rate_tl_per_usd
                )
                
                payments.append({
                    'date': current_date,
                    'amount_tl': amount_tl,
                    'amount_usd': amount_usd,
                    'exchange_rate': rate.rate_tl_per_usd
                })
            
            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        # Verify no spikes in November
        assert len(payments) >= 3, "Should have at least 3 payments"
        
        # Nov 2024 should be base amount
        nov_2024 = next(p for p in payments if p['date'] == date(2024, 11, 1))
        assert nov_2024['amount_tl'] == Decimal('31000'), f"Nov 2024 should be 31,000 TL, got {nov_2024['amount_tl']}"
        
        # Dec 2024 should be conditional amount
        dec_2024 = next(p for p in payments if p['date'] == date(2024, 12, 1))
        assert dec_2024['amount_tl'] == Decimal('35000'), f"Dec 2024 should be 35,000 TL, got {dec_2024['amount_tl']}"
        
        # No sudden spikes - amounts should change smoothly
        for i in range(1, len(payments)):
            prev_amount = payments[i-1]['amount_tl']
            curr_amount = payments[i]['amount_tl']
            
            # Allow for expected changes (Nov->Dec transition)
            if prev_amount == Decimal('31000') and curr_amount == Decimal('35000'):
                continue  # This is expected
            
            # No other sudden changes should occur
            assert abs(curr_amount - prev_amount) <= Decimal('1000'), \
                f"Sudden spike detected: {prev_amount} -> {curr_amount} at {payments[i]['date']}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
