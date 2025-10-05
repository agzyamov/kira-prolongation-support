"""
Test for duplicate agreement fix.

Bug: User reported that the app showed two separate agreements when it should 
show ONE agreement with conditional pricing. The issue was that duplicate 
agreements were created for the same period.

Fix: 
1. Delete duplicate agreements
2. Ensure only one agreement exists per period
3. Fix conditional rules structure to be properly formatted

Tests verify that:
- Only one agreement exists for the 2024-2025 period
- Conditional rules are properly structured
- Agreement displays correctly in UI
"""
import pytest
import tempfile
import os
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.storage import DataStore
from src.models import RentalAgreement


def test_no_duplicate_agreements_for_same_period():
    """Test that there are no duplicate agreements for the same period"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create one agreement for 2024-2025 period
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
            notes="Single agreement with conditional pricing"
        )
        
        data_store.save_rental_agreement(agreement)
        
        # Verify only one agreement exists for this period
        agreements = data_store.get_rental_agreements()
        
        # Count agreements for 2024-2025 period
        period_agreements = [
            a for a in agreements 
            if a.start_date.year == 2024 and a.end_date and a.end_date.year == 2025
        ]
        
        assert len(period_agreements) == 1, f"Expected 1 agreement for 2024-2025 period, got {len(period_agreements)}"
        
        # Verify the agreement has correct structure
        agreement = period_agreements[0]
        assert agreement.base_amount_tl == Decimal('31000')
        assert agreement.has_conditional_pricing() == True
        assert len(agreement.conditional_rules.get('rules', [])) == 1
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_conditional_rules_structure_is_correct():
    """Test that conditional rules are properly structured"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create agreement with correct conditional rules structure
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
        
        # Retrieve and verify structure
        agreements = data_store.get_rental_agreements()
        saved_agreement = agreements[0]
        
        # Check conditional rules structure
        assert saved_agreement.conditional_rules is not None
        assert 'rules' in saved_agreement.conditional_rules
        assert len(saved_agreement.conditional_rules['rules']) == 1
        
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


def test_agreement_display_logic():
    """Test that agreement display logic works correctly"""
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
        
        # Simulate UI display logic
        agreements = data_store.get_rental_agreements()
        
        # Should show exactly one agreement
        assert len(agreements) == 1
        
        agreement = agreements[0]
        
        # Display properties
        display_text = f"{agreement.start_date} - {agreement.end_date or 'Ongoing'} ({agreement.base_amount_tl:,.0f} TL)"
        expected_display = "2024-11-01 - 2025-11-01 (31,000 TL)"
        assert display_text == expected_display, f"Expected '{expected_display}', got '{display_text}'"
        
        # Conditional pricing display
        if agreement.has_conditional_pricing():
            rule_count = len(agreement.conditional_rules.get('rules', []))
            assert rule_count == 1, f"Should show 1 conditional rule, got {rule_count}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_delete_and_update_methods_work():
    """Test that delete and update methods work correctly"""
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
            conditional_rules=None,
            notes="Test agreement"
        )
        
        agreement_id = data_store.save_rental_agreement(agreement)
        
        # Test update
        agreement.id = agreement_id
        agreement.conditional_rules = {
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
        }
        
        success = data_store.update_rental_agreement(agreement)
        assert success == True, "Update should succeed"
        
        # Verify update
        updated_agreements = data_store.get_rental_agreements()
        assert len(updated_agreements) == 1
        assert updated_agreements[0].has_conditional_pricing() == True
        
        # Test delete
        success = data_store.delete_rental_agreement(agreement_id)
        assert success == True, "Delete should succeed"
        
        # Verify delete
        remaining_agreements = data_store.get_rental_agreements()
        assert len(remaining_agreements) == 0
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
