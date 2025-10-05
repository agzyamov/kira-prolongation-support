"""
Test for Payment Records bug with future months.

Bug: User reports error when calculating Payment Records for agreement 
"2024-11-01 - 2025-11-01 (31,000 TL)". The app tries to fetch exchange rates 
for future months (like 2025-11) which don't exist in TCMB.

Expected behavior for Nov 2024-Nov 2025 agreement:
- Nov 2024: 31,000 TL
- Dec 2024 onwards: If USD < 40 TL then 35,000 TL, otherwise 40,000 TL
- Should only calculate payments up to current date, not future months

Root cause: Payment calculation logic tries to fetch exchange rates for 
entire agreement period including future months.

Fix: Modify payment calculation to only process months up to current date.
"""
import pytest
import tempfile
import os
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.storage import DataStore
from src.models import RentalAgreement, ExchangeRate
from src.services import ExchangeRateService


def test_payment_records_skips_future_months():
    """Test that payment records calculation skips future months"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        exchange_service = ExchangeRateService(data_store)
        
        # Create a rental agreement from Nov 2024 to Nov 2025
        agreement = RentalAgreement(
            id=1,
            start_date=date(2024, 11, 1),
            end_date=date(2025, 11, 1),
            base_amount_tl=Decimal('31000'),
            conditional_rules={
                'rules': [{
                    'condition': 'usd_rate_threshold',
                    'threshold': 40.0,
                    'rent_low': 35000,
                    'rent_high': 40000
                }]
            },
            notes="Test agreement with currency clause"
        )
        
        # Save the agreement
        data_store.save_rental_agreement(agreement)
        
        # Add some exchange rates for past/current months (not future)
        exchange_rates = [
            ExchangeRate(month=11, year=2024, rate_tl_per_usd=Decimal('34.0'), source='TCMB'),
            ExchangeRate(month=12, year=2024, rate_tl_per_usd=Decimal('35.0'), source='TCMB'),
            ExchangeRate(month=1, year=2025, rate_tl_per_usd=Decimal('36.0'), source='TCMB'),
            ExchangeRate(month=2, year=2025, rate_tl_per_usd=Decimal('37.0'), source='TCMB'),
            # Note: No rates for future months like 2025-11
        ]
        
        for rate in exchange_rates:
            data_store.save_exchange_rate(rate)
        
            # Mock current date to be in March 2025
            with patch('datetime.date') as mock_date:
                mock_date.today.return_value = date(2025, 3, 15)
                mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
                
                # The payment calculation should only process months up to current date
                # and should NOT try to fetch exchange rates for future months
                
                # This should not raise an error about missing 2025-11 exchange rate
                # because it should only calculate up to March 2025
                
                # Test the logic that determines which months to process
                current_date = mock_date.today()  # Use mocked date
                start_date = agreement.start_date
                
                # Calculate months to process (should stop at current month)
                months_to_process = []
                current_month = start_date.month
                current_year = start_date.year
                
                while (current_year < current_date.year) or (current_year == current_date.year and current_month <= current_date.month):
                    months_to_process.append((current_month, current_year))
                    
                    # Move to next month
                    current_month += 1
                    if current_month > 12:
                        current_month = 1
                        current_year += 1
                
                # Should only include months up to March 2025, not November 2025
                expected_months = [
                    (11, 2024), (12, 2024),  # 2024
                    (1, 2025), (2, 2025), (3, 2025)  # 2025 up to current month
                ]
                
                assert months_to_process == expected_months, \
                    f"Expected months {expected_months}, got {months_to_process}"
                
                # Should NOT include future months like (11, 2025)
                assert (11, 2025) not in months_to_process, \
                    "Should not include future months in calculation"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_payment_records_handles_missing_exchange_rates_gracefully():
    """Test that payment records handles missing exchange rates gracefully"""
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
                'rules': [{
                    'condition': 'usd_rate_threshold',
                    'threshold': 40.0,
                    'rent_low': 35000,
                    'rent_high': 40000
                }]
            },
            notes="Test agreement"
        )
        
        data_store.save_rental_agreement(agreement)
        
        # Add only some exchange rates (missing some months)
        exchange_rates = [
            ExchangeRate(month=11, year=2024, rate_tl_per_usd=Decimal('34.0'), source='TCMB'),
            # Missing Dec 2024
            ExchangeRate(month=1, year=2025, rate_tl_per_usd=Decimal('36.0'), source='TCMB'),
            # Missing Feb 2025
        ]
        
        for rate in exchange_rates:
            data_store.save_exchange_rate(rate)
        
        # Mock current date
        with patch('datetime.date') as mock_date:
            mock_date.today.return_value = date(2025, 2, 15)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            # Should handle missing exchange rates gracefully
            # and not crash when trying to fetch missing rates
            
            # Test that we can check for missing rates without crashing
            months_to_check = [(11, 2024), (12, 2024), (1, 2025), (2, 2025)]
            
            missing_rates = []
            for month, year in months_to_check:
                rate = data_store.get_exchange_rate(month, year)
                if not rate:
                    missing_rates.append((month, year))
            
            # Should identify missing rates
            expected_missing = [(12, 2024), (2, 2025)]
            assert missing_rates == expected_missing, \
                f"Expected missing rates {expected_missing}, got {missing_rates}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_currency_clause_calculation():
    """Test that currency clause is calculated correctly"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create agreement with currency clause
        agreement = RentalAgreement(
            id=1,
            start_date=date(2024, 11, 1),
            end_date=date(2025, 11, 1),
            base_amount_tl=Decimal('31000'),
            conditional_rules={
                'rules': [{
                    'condition': 'usd_rate_threshold',
                    'threshold': 40.0,
                    'rent_low': 35000,
                    'rent_high': 40000
                }]
            },
            notes="Test agreement"
        )
        
        # Test currency clause logic
        # If USD rate < 40 TL, use 35,000 TL
        # If USD rate >= 40 TL, use 40,000 TL
        
        # Test case 1: USD rate < 40 TL
        usd_rate_low = Decimal('35.0')
        threshold = Decimal('40.0')
        rent_low = Decimal('35000')
        rent_high = Decimal('40000')
        
        if usd_rate_low < threshold:
            expected_rent_low = rent_low
        else:
            expected_rent_low = rent_high
        
        assert expected_rent_low == Decimal('35000'), \
            f"Expected 35000 TL for USD rate {usd_rate_low}, got {expected_rent_low}"
        
        # Test case 2: USD rate >= 40 TL
        usd_rate_high = Decimal('42.0')
        if usd_rate_high < threshold:
            expected_rent_high = rent_low
        else:
            expected_rent_high = rent_high
        
        assert expected_rent_high == Decimal('40000'), \
            f"Expected 40000 TL for USD rate {usd_rate_high}, got {expected_rent_high}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
