#!/usr/bin/env python3
"""
Database migration script to add new functional requirements tables.
Adds negotiation_settings and legal_rules tables to support new features.
"""

import sqlite3
import json
from datetime import datetime

def migrate_add_new_functional():
    """Add new tables for functional requirements."""
    db_path = "rental_negotiation.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create negotiation_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS negotiation_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode VARCHAR(20) NOT NULL CHECK (mode IN ('calm', 'assertive')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create legal_rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS legal_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_type VARCHAR(20) NOT NULL CHECK (rule_type IN ('25%_cap', 'cpi_based')),
                effective_start DATE NOT NULL,
                effective_end DATE,
                rate DECIMAL(6, 2),
                label VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Insert default legal rules
        cursor.execute("""
            INSERT OR IGNORE INTO legal_rules (rule_type, effective_start, effective_end, rate, label) VALUES
            ('25%_cap', '2020-01-01', '2024-06-30', 25.00, '+25% (limit until July 2024)'),
            ('cpi_based', '2024-07-01', NULL, NULL, '+CPI (Yearly TÜFE)');
        """)

        # Insert default negotiation settings
        cursor.execute("""
            INSERT OR IGNORE INTO negotiation_settings (mode) VALUES ('calm');
        """)

        conn.commit()
        print("✅ Successfully added new functional requirements tables:")
        print("  - negotiation_settings")
        print("  - legal_rules")
        print("  - Default legal rules inserted")
        print("  - Default negotiation settings inserted")

        # Verification
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('negotiation_settings', 'legal_rules');")
        tables = cursor.fetchall()
        if len(tables) == 2:
            print("✅ Verification: Both tables created successfully.")
        else:
            print("❌ Verification failed: Not all tables created.")

    except sqlite3.Error as e:
        print(f"Database error during migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_add_new_functional()
