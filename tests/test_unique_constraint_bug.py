"""
Test for unique constraint bug when saving multiple rates from same screenshot.

Bug: User reported that saving Rate 1 works, but saving Rate 2 fails with:
"UNIQUE constraint failed: market_rates.screenshot_filename"

Root cause: Database schema has unique constraint on screenshot_filename,
but multiple rates from the same screenshot all have the same filename.

Fix: Remove unique constraint or make it composite (filename + amount).
"""
from decimal import Decimal
from datetime import date
import tempfile
import os

from src.storage import DataStore
from src.models import MarketRate


def test_multiple_rates_from_same_screenshot_save_successfully():
    """Test that multiple rates from the same screenshot can be saved"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # Initialize DataStore with temp database
        data_store = DataStore(db_path=db_path)
        
        # Create multiple rates from the same screenshot
        rate1 = MarketRate(
            amount_tl=Decimal("30000"),
            location="Konyaaltı",
            screenshot_filename="screenshot.png",  # Same filename
            date_captured=date.today(),
            confidence=Decimal("0.85"),
            raw_ocr_text="30 bin TL Konyaaltı"
        )
        
        rate2 = MarketRate(
            amount_tl=Decimal("45000"),
            location="Konyaaltı", 
            screenshot_filename="screenshot.png",  # Same filename
            date_captured=date.today(),
            confidence=Decimal("0.90"),
            raw_ocr_text="45 bin TL Konyaaltı"
        )
        
        # Both should save successfully
        rate1_id = data_store.save_market_rate(rate1)
        rate2_id = data_store.save_market_rate(rate2)
        
        assert rate1_id > 0, "Rate 1 should be saved with valid ID"
        assert rate2_id > 0, "Rate 2 should be saved with valid ID"
        assert rate1_id != rate2_id, "Rates should have different IDs"
        
        # Verify both are retrievable
        retrieved_rates = data_store.get_market_rates()
        assert len(retrieved_rates) == 2, "Should retrieve both saved rates"
        
        # Verify amounts are different
        amounts = [r.amount_tl for r in retrieved_rates]
        assert Decimal("30000") in amounts, "Rate 1 amount should be found"
        assert Decimal("45000") in amounts, "Rate 2 amount should be found"
        
    finally:
        # Clean up temp database
        if os.path.exists(db_path):
            os.remove(db_path)


def test_database_schema_allows_duplicate_filenames():
    """Test that database schema doesn't have unique constraint on screenshot_filename"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Check the schema by examining the table creation
        with data_store._get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(market_rates)")
            columns = cursor.fetchall()
            
            # Find screenshot_filename column
            filename_col = None
            for col in columns:
                if col[1] == 'screenshot_filename':  # col[1] is column name
                    filename_col = col
                    break
            
            assert filename_col is not None, "screenshot_filename column should exist"
            
            # Check if it has unique constraint (col[5] is the constraint info)
            is_unique = filename_col[5]  # 1 if unique, 0 if not
            assert is_unique == 0, f"screenshot_filename should not be unique (got {is_unique})"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
