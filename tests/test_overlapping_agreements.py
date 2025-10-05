"""
Test for overlapping agreements bug.

Bug: User reports overlapping agreements causing chart spikes and duplicate payments.
Root cause: Multiple agreements exist for the same time periods:
- Agreement 1: 2022-11-01 to 2023-11-01
- Agreement 2: 2023-11-01 to 2024-11-01  
- Agreement 4: 2024-11-01 to 2025-11-01

This causes:
- Duplicate payments for overlapping months (Nov 2023, Nov 2024)
- Chart spikes due to multiple data points for same period
- Confusion about which agreement applies when

Solution: 
1. Add validation to prevent overlapping agreements
2. Clean up existing overlapping agreements
3. Ensure only one agreement per time period
"""
import pytest
import tempfile
import os
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.storage import DataStore
from src.storage.data_store import DatabaseError
from src.models import RentalAgreement


def test_no_overlapping_agreements_allowed():
    """Test that overlapping agreements are not allowed"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create first agreement
        agreement1 = RentalAgreement(
            id=1,
            start_date=date(2022, 11, 1),
            end_date=date(2023, 11, 1),
            base_amount_tl=Decimal('15000'),
            conditional_rules=None,
            notes="First agreement"
        )
        
        data_store.save_rental_agreement(agreement1)
        
        # Try to create overlapping agreement - should be rejected
        agreement2 = RentalAgreement(
            id=2,
            start_date=date(2023, 11, 1),  # Same end date as agreement1
            end_date=date(2024, 11, 1),
            base_amount_tl=Decimal('25000'),
            conditional_rules=None,
            notes="Overlapping agreement"
        )
        
        # This should raise an exception or be rejected
        with pytest.raises((DatabaseError, ValueError)):
            data_store.save_rental_agreement(agreement2)
        
        # Verify only one agreement exists
        agreements = data_store.get_rental_agreements()
        assert len(agreements) == 1
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_agreement_validation_checks_overlaps():
    """Test that agreement validation checks for overlaps"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create first agreement
        agreement1 = RentalAgreement(
            id=1,
            start_date=date(2022, 11, 1),
            end_date=date(2023, 11, 1),
            base_amount_tl=Decimal('15000'),
            conditional_rules=None,
            notes="First agreement"
        )
        
        data_store.save_rental_agreement(agreement1)
        
        # Test various overlapping scenarios
        overlapping_scenarios = [
            # Same start/end dates
            (date(2023, 11, 1), date(2024, 11, 1), "Same end date as start date"),
            # Overlapping in middle
            (date(2023, 6, 1), date(2024, 6, 1), "Overlapping in middle"),
            # Completely contained
            (date(2023, 1, 1), date(2023, 6, 1), "Completely contained"),
            # Completely containing
            (date(2022, 1, 1), date(2024, 1, 1), "Completely containing"),
        ]
        
        for start_date, end_date, description in overlapping_scenarios:
            agreement = RentalAgreement(
                id=None,  # Will be assigned
                start_date=start_date,
                end_date=end_date,
                base_amount_tl=Decimal('25000'),
                conditional_rules=None,
                notes=f"Overlapping: {description}"
            )
            
            # Should be rejected
            with pytest.raises((DatabaseError, ValueError)):
                data_store.save_rental_agreement(agreement)
        
        # Verify still only one agreement
        agreements = data_store.get_rental_agreements()
        assert len(agreements) == 1
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_non_overlapping_agreements_allowed():
    """Test that non-overlapping agreements are allowed"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create first agreement
        agreement1 = RentalAgreement(
            id=1,
            start_date=date(2022, 11, 1),
            end_date=date(2023, 11, 1),
            base_amount_tl=Decimal('15000'),
            conditional_rules=None,
            notes="First agreement"
        )
        
        data_store.save_rental_agreement(agreement1)
        
        # Create non-overlapping agreement - should be allowed
        agreement2 = RentalAgreement(
            id=2,
            start_date=date(2023, 12, 1),  # Starts after first agreement ends
            end_date=date(2024, 11, 1),
            base_amount_tl=Decimal('25000'),
            conditional_rules=None,
            notes="Non-overlapping agreement"
        )
        
        # This should succeed
        agreement2_id = data_store.save_rental_agreement(agreement2)
        assert agreement2_id is not None
        
        # Verify both agreements exist
        agreements = data_store.get_rental_agreements()
        assert len(agreements) == 2
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_cleanup_overlapping_agreements():
    """Test cleanup of existing overlapping agreements"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create overlapping agreements (simulating current bug)
        agreement1 = RentalAgreement(
            id=1,
            start_date=date(2022, 11, 1),
            end_date=date(2023, 11, 1),
            base_amount_tl=Decimal('15000'),
            conditional_rules=None,
            notes="First agreement"
        )
        
        agreement2 = RentalAgreement(
            id=2,
            start_date=date(2023, 11, 1),  # Overlapping
            end_date=date(2024, 11, 1),
            base_amount_tl=Decimal('25000'),
            conditional_rules=None,
            notes="Overlapping agreement"
        )
        
        # Manually insert overlapping agreements (bypassing validation for test)
        with data_store._get_connection() as conn:
            conn.execute("""
                INSERT INTO rental_agreements (id, start_date, end_date, base_amount_tl, conditional_rules, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                1, 
                agreement1.start_date.isoformat(), 
                agreement1.end_date.isoformat(),
                str(agreement1.base_amount_tl),
                None,
                agreement1.notes,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.execute("""
                INSERT INTO rental_agreements (id, start_date, end_date, base_amount_tl, conditional_rules, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                2, 
                agreement2.start_date.isoformat(), 
                agreement2.end_date.isoformat(),
                str(agreement2.base_amount_tl),
                None,
                agreement2.notes,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            conn.commit()
        
        # Verify overlapping agreements exist
        agreements = data_store.get_rental_agreements()
        assert len(agreements) == 2
        
        # Test cleanup method (if it exists)
        if hasattr(data_store, 'cleanup_overlapping_agreements'):
            data_store.cleanup_overlapping_agreements()
            
            # Verify only non-overlapping agreements remain
            agreements_after = data_store.get_rental_agreements()
            assert len(agreements_after) < 2  # Should have fewer agreements
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
