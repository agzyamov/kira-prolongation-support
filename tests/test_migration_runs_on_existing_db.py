"""
Test for migration not running on existing database.

Bug: User still gets UNIQUE constraint error because migration only runs
when creating new database, not on existing ones.

Root cause: Migration is only called in _create_schema() which only runs
for new databases. Existing databases with the old schema aren't migrated.

Fix: Call migration on every DataStore initialization.
"""
from decimal import Decimal
from datetime import date
import tempfile
import os
import sqlite3

from src.storage import DataStore
from src.models import MarketRate


def test_migration_runs_on_existing_database():
    """Test that migration runs when DataStore is initialized with existing database"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # First, create a database with the OLD schema (with unique constraint)
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE market_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount_tl DECIMAL(10, 2) NOT NULL,
                    location VARCHAR(255),
                    screenshot_filename VARCHAR(255) NOT NULL UNIQUE,  -- OLD: has UNIQUE
                    date_captured DATE NOT NULL,
                    confidence DECIMAL(3, 2),
                    raw_ocr_text TEXT,
                    property_details TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        
        # Now initialize DataStore with existing database
        # This should trigger migration
        data_store = DataStore(db_path=db_path)
        
        # Verify migration worked by checking schema
        with data_store._get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(market_rates)")
            columns = cursor.fetchall()
            
            # Find screenshot_filename column
            filename_col = None
            for col in columns:
                if col[1] == 'screenshot_filename':
                    filename_col = col
                    break
            
            assert filename_col is not None, "screenshot_filename column should exist"
            
            # Check that unique constraint was removed
            is_unique = filename_col[5]  # 1 if unique, 0 if not
            assert is_unique == 0, f"Migration should have removed unique constraint (got {is_unique})"
        
        # Test that multiple rates from same screenshot can be saved
        rate1 = MarketRate(
            amount_tl=Decimal("30000"),
            location="Konyaaltı",
            screenshot_filename="test.png",
            date_captured=date.today(),
            confidence=Decimal("0.85"),
            raw_ocr_text="30 bin TL"
        )
        
        rate2 = MarketRate(
            amount_tl=Decimal("45000"),
            location="Konyaaltı",
            screenshot_filename="test.png",  # Same filename
            date_captured=date.today(),
            confidence=Decimal("0.90"),
            raw_ocr_text="45 bin TL"
        )
        
        # Both should save successfully after migration
        rate1_id = data_store.save_market_rate(rate1)
        rate2_id = data_store.save_market_rate(rate2)
        
        assert rate1_id > 0 and rate2_id > 0, "Both rates should save successfully after migration"
        assert rate1_id != rate2_id, "Rates should have different IDs"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_migration_preserves_existing_data():
    """Test that migration preserves existing data in the database"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # Create database with old schema and some data
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE market_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount_tl DECIMAL(10, 2) NOT NULL,
                    location VARCHAR(255),
                    screenshot_filename VARCHAR(255) NOT NULL UNIQUE,
                    date_captured DATE NOT NULL,
                    confidence DECIMAL(3, 2),
                    raw_ocr_text TEXT,
                    property_details TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert some existing data
            conn.execute("""
                INSERT INTO market_rates 
                (amount_tl, location, screenshot_filename, date_captured, confidence, raw_ocr_text)
                VALUES (25000, 'Test Location', 'existing.png', '2025-01-01', 0.8, 'existing data')
            """)
            conn.commit()
        
        # Initialize DataStore (should trigger migration)
        data_store = DataStore(db_path=db_path)
        
        # Verify existing data is preserved
        existing_rates = data_store.get_market_rates()
        assert len(existing_rates) == 1, "Existing data should be preserved"
        assert existing_rates[0].amount_tl == Decimal("25000"), "Existing amount should be preserved"
        assert existing_rates[0].location == "Test Location", "Existing location should be preserved"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
