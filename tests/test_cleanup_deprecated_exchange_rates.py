"""
Test for cleaning up deprecated exchange rate sources.

Bug: User reports seeing exchange rates from deprecated sources in the database.
These were added before switching to TCMB-only policy.

Root cause: Old exchange rates from non-TCMB sources are still in the database.

Fix: Create migration to remove exchange rates from non-TCMB sources.
"""
from decimal import Decimal
from datetime import date
import tempfile
import os
import sqlite3

from src.storage import DataStore
from src.models import ExchangeRate


def test_cleanup_deprecated_exchange_rates():
    """Test that migration removes exchange rates from non-TCMB sources"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # Create database with old exchange rates from various sources
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE exchange_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    rate_tl_per_usd DECIMAL(10, 4) NOT NULL,
                    source VARCHAR(255),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(month, year)
                )
            """)
            
            # Insert exchange rates from various sources (old and new)
            conn.execute("""
                INSERT INTO exchange_rates (month, year, rate_tl_per_usd, source, notes)
                VALUES 
                (1, 2023, 18.85, 'TCMB', 'Official Central Bank rate'),
                (2, 2023, 19.12, 'TCMB', 'Official Central Bank rate'),
                (3, 2023, 19.45, 'Yahoo Finance', 'Deprecated source'),
                (4, 2023, 19.78, 'Fixer.io', 'Deprecated source'),
                (5, 2023, 20.15, 'TCMB', 'Official Central Bank rate'),
                (6, 2023, 20.45, 'Alpha Vantage', 'Deprecated source')
            """)
            conn.commit()
        
        # Initialize DataStore (should trigger cleanup migration)
        data_store = DataStore(db_path=db_path)
        
        # Verify only TCMB rates remain
        remaining_rates = data_store.get_exchange_rates()
        
        # Should have only 3 TCMB rates
        assert len(remaining_rates) == 3, f"Expected 3 TCMB rates, got {len(remaining_rates)}"
        
        # All remaining rates should be from TCMB
        for rate in remaining_rates:
            assert rate.source == 'TCMB', f"Found non-TCMB rate: {rate.source}"
        
        # Verify specific months are correct
        months = [rate.month for rate in remaining_rates]
        assert 1 in months, "January 2023 TCMB rate should remain"
        assert 2 in months, "February 2023 TCMB rate should remain"
        assert 5 in months, "May 2023 TCMB rate should remain"
        
        # Verify deprecated sources are gone
        sources = [rate.source for rate in remaining_rates]
        assert 'Yahoo Finance' not in sources, "Yahoo Finance rates should be removed"
        assert 'Fixer.io' not in sources, "Fixer.io rates should be removed"
        assert 'Alpha Vantage' not in sources, "Alpha Vantage rates should be removed"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_cleanup_preserves_tcmb_rates():
    """Test that migration preserves all TCMB rates"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # Create database with only TCMB rates
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE exchange_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    rate_tl_per_usd DECIMAL(10, 4) NOT NULL,
                    source VARCHAR(255),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(month, year)
                )
            """)
            
            # Insert only TCMB rates
            conn.execute("""
                INSERT INTO exchange_rates (month, year, rate_tl_per_usd, source, notes)
                VALUES 
                (1, 2023, 18.85, 'TCMB', 'Official Central Bank rate'),
                (2, 2023, 19.12, 'TCMB', 'Official Central Bank rate'),
                (3, 2023, 19.45, 'TCMB', 'Official Central Bank rate')
            """)
            conn.commit()
        
        # Initialize DataStore (should not remove any rates)
        data_store = DataStore(db_path=db_path)
        
        # Verify all TCMB rates are preserved
        remaining_rates = data_store.get_exchange_rates()
        assert len(remaining_rates) == 3, "All TCMB rates should be preserved"
        
        for rate in remaining_rates:
            assert rate.source == 'TCMB', "All rates should be TCMB"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_cleanup_handles_empty_database():
    """Test that migration handles empty exchange_rates table gracefully"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # Create empty database
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE exchange_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    rate_tl_per_usd DECIMAL(10, 4) NOT NULL,
                    source VARCHAR(255),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(month, year)
                )
            """)
            conn.commit()
        
        # Initialize DataStore (should not crash)
        data_store = DataStore(db_path=db_path)
        
        # Verify empty table remains empty
        remaining_rates = data_store.get_exchange_rates()
        assert len(remaining_rates) == 0, "Empty table should remain empty"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
