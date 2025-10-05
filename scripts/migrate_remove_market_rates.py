#!/usr/bin/env python3
"""
Database migration script to remove market_rates table.
This script safely removes the market_rates table and all associated data.
"""

import sqlite3
import os
from pathlib import Path

def migrate_remove_market_rates():
    """Remove market_rates table from the database."""
    
    # Database path
    db_path = "rental_negotiation.db"
    
    if not os.path.exists(db_path):
        print("No database found. Nothing to migrate.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if market_rates table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='market_rates'
        """)
        
        if not cursor.fetchone():
            print("No market_rates table found. Nothing to migrate.")
            conn.close()
            return
        
        # Get count of records before deletion
        cursor.execute("SELECT COUNT(*) FROM market_rates")
        count = cursor.fetchone()[0]
        print(f"Found {count} market rate records to remove.")
        
        # Drop the market_rates table
        cursor.execute("DROP TABLE IF EXISTS market_rates")
        
        # Commit changes
        conn.commit()
        
        print(f"✅ Successfully removed market_rates table and {count} records.")
        
        # Verify removal
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='market_rates'
        """)
        
        if not cursor.fetchone():
            print("✅ Verification: market_rates table successfully removed.")
        else:
            print("❌ Verification failed: market_rates table still exists.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_remove_market_rates()
