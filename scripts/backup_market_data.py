#!/usr/bin/env python3
"""
Backup script for market data before removal.
This script creates a backup of existing market rate data before removing the market comparison feature.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def backup_market_data():
    """Create a backup of market rate data before removal."""
    
    # Database path
    db_path = "rental_negotiation.db"
    
    if not os.path.exists(db_path):
        print("No database found. Nothing to backup.")
        return
    
    # Create backup directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"market_data_backup_{timestamp}.json"
    
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
            print("No market_rates table found. Nothing to backup.")
            conn.close()
            return
        
        # Get all market rate data
        cursor.execute("SELECT * FROM market_rates")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(market_rates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Convert to list of dictionaries
        market_data = []
        for row in rows:
            market_data.append(dict(zip(columns, row)))
        
        # Save backup
        with open(backup_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'table_name': 'market_rates',
                'columns': columns,
                'data': market_data,
                'count': len(market_data)
            }, f, indent=2, default=str)
        
        print(f"✅ Market data backup created: {backup_file}")
        print(f"   - {len(market_data)} records backed up")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    backup_market_data()
