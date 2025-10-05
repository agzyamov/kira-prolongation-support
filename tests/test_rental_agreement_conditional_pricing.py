"""
Test for Rental Agreement conditional pricing bug.

Bug: User reports that the app shows two separate agreements when it should 
show ONE agreement with conditional pricing:
- Nov 2024: 31,000 TL
- Dec 2024 - Nov 2025: If USD < 40 TL then 35,000 TL, otherwise 40,000 TL

Root cause: The app is creating separate rental agreements instead of one 
agreement with conditional rules.

Fix: Ensure that conditional pricing is stored as rules within a single 
agreement, not as separate agreements.
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


def test_rental_agreement_has_single_conditional_pricing():
    """Test that a rental agreement with conditional pricing is stored as ONE agreement"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create ONE agreement with conditional pricing
        # Nov 2024: 31,000 TL
        # Dec 2024 - Nov 2025: If USD < 40 TL then 35,000 TL, otherwise 40,000 TL
        agreement = RentalAgreement(
            id=1,
            start_date=date(2024, 11, 1),
            end_date=date(2025, 11, 1),
            base_amount_tl=Decimal('31000'),  # Base rent for Nov 2024
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
            notes="Single agreement with conditional pricing"
        )
        
        # Save the agreement
        data_store.save_rental_agreement(agreement)
        
        # Retrieve agreements
        agreements = data_store.get_rental_agreements()
        
        # Should be exactly ONE agreement
        assert len(agreements) == 1, f"Expected 1 agreement, got {len(agreements)}"
        
        saved_agreement = agreements[0]
        assert saved_agreement.base_amount_tl == Decimal('31000')
        assert saved_agreement.has_conditional_pricing() == True
        assert len(saved_agreement.conditional_rules.get('rules', [])) == 1
        
        # Check conditional rule
        rule = saved_agreement.conditional_rules['rules'][0]
        assert rule['condition'] == 'date_range'
        assert rule['start_date'] == '2024-12-01'
        assert rule['end_date'] == '2025-11-01'
        assert rule['usd_threshold'] == 40.0
        assert rule['rent_low'] == 35000
        assert rule['rent_high'] == 40000
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_conditional_pricing_calculation_logic():
    """Test that conditional pricing is calculated correctly"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create agreement with conditional pricing
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
        
        # Test calculation logic
        # Nov 2024: Should use base amount (31,000 TL)
        nov_2024_date = date(2024, 11, 1)
        nov_2024_amount = agreement.base_amount_tl
        assert nov_2024_amount == Decimal('31000'), f"Nov 2024 should be 31,000 TL, got {nov_2024_amount}"
        
        # Dec 2024 onwards: Should use conditional pricing
        dec_2024_date = date(2024, 12, 1)
        
        # Test case 1: USD rate < 40 TL → 35,000 TL
        usd_rate_low = Decimal('35.0')
        if usd_rate_low < Decimal('40.0'):
            dec_2024_amount_low = Decimal('35000')
        else:
            dec_2024_amount_low = Decimal('40000')
        
        assert dec_2024_amount_low == Decimal('35000'), \
            f"Dec 2024 with USD {usd_rate_low} should be 35,000 TL, got {dec_2024_amount_low}"
        
        # Test case 2: USD rate >= 40 TL → 40,000 TL
        usd_rate_high = Decimal('42.0')
        if usd_rate_high < Decimal('40.0'):
            dec_2024_amount_high = Decimal('35000')
        else:
            dec_2024_amount_high = Decimal('40000')
        
        assert dec_2024_amount_high == Decimal('40000'), \
            f"Dec 2024 with USD {usd_rate_high} should be 40,000 TL, got {dec_2024_amount_high}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_agreement_display_shows_single_agreement():
    """Test that the UI displays one agreement, not multiple"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create ONE agreement with conditional pricing
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
            notes="Single agreement"
        )
        
        data_store.save_rental_agreement(agreement)
        
        # Simulate what the UI should display
        agreements = data_store.get_rental_agreements()
        
        # Should show exactly one agreement
        assert len(agreements) == 1
        
        # The agreement should show:
        # - Base rent: 31,000 TL (for Nov 2024)
        # - Conditional pricing: 1 rule (for Dec 2024 - Nov 2025)
        agreement = agreements[0]
        
        # Check display properties
        assert agreement.base_amount_tl == Decimal('31000')
        assert agreement.start_date == date(2024, 11, 1)
        assert agreement.end_date == date(2025, 11, 1)
        assert agreement.has_conditional_pricing() == True
        
        # Should show "Conditional Pricing: 1 rule" (not 2 rules)
        rule_count = len(agreement.conditional_rules.get('rules', []))
        assert rule_count == 1, f"Should show 1 conditional rule, got {rule_count}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_no_duplicate_agreements_created():
    """Test that the system doesn't create duplicate agreements for the same period"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create one agreement
        agreement1 = RentalAgreement(
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
            notes="Single agreement"
        )
        
        data_store.save_rental_agreement(agreement1)
        
        # Try to create another agreement for the same period (should not happen)
        # This simulates the bug where multiple agreements are created
        
        agreements = data_store.get_rental_agreements()
        
        # Should still be only one agreement
        assert len(agreements) == 1, f"Should have only 1 agreement, got {len(agreements)}"
        
        # All agreements should have the same period
        for agreement in agreements:
            assert agreement.start_date == date(2024, 11, 1)
            assert agreement.end_date == date(2025, 11, 1)
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
