#!/usr/bin/env python3
"""
Database migration script for enhanced TÜFE tables.
Adds new fields to existing TÜFE tables and creates new tables for easy TÜFE fetching.

This script enhances the existing TÜFE infrastructure with:
- Enhanced TufeDataSource with reliability tracking
- New TufeFetchSession for operation tracking
- New TufeSourceManager for automatic source selection
- New TufeAutoConfig for zero-configuration setup
- Enhanced TufeApiKey with auto-configuration
- Enhanced TufeDataCache with source tracking
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def run_migration():
    """Run the database migration for enhanced TÜFE tables."""
    
    # Get the database path
    db_path = Path("rental_negotiation.db")
    if not db_path.exists():
        # Try alternative path
        db_path = Path("data/rental_negotiation.db")
        db_path.parent.mkdir(exist_ok=True)
    
    print(f"Running migration on database: {db_path}")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 1. Enhance TufeDataSource table with new fields
        print("1. Enhancing TufeDataSource table...")
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(tufe_data_sources)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        new_columns = [
            ("priority", "INTEGER DEFAULT 5"),
            ("reliability_score", "REAL DEFAULT 0.5"),
            ("last_health_check", "TIMESTAMP"),
            ("health_status", "TEXT DEFAULT 'unknown' CHECK(health_status IN ('healthy', 'degraded', 'failed', 'unknown'))"),
            ("failure_count", "INTEGER DEFAULT 0"),
            ("success_count", "INTEGER DEFAULT 0"),
            ("avg_response_time", "REAL DEFAULT 0.0"),
            ("rate_limit_remaining", "INTEGER DEFAULT 1000"),
            ("rate_limit_reset", "TIMESTAMP")
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE tufe_data_sources ADD COLUMN {column_name} {column_def}")
                    print(f"  ✓ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"  ⚠️ Column {column_name} might already exist: {e}")
        
        # 2. Create TufeFetchSession table
        print("2. Creating TufeFetchSession table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tufe_fetch_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                requested_year INTEGER NOT NULL CHECK(requested_year >= 2000 AND requested_year <= 2030),
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'success', 'failed', 'cancelled')),
                started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                source_attempts TEXT DEFAULT '[]',
                final_source INTEGER,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (final_source) REFERENCES tufe_data_sources(id)
            )
        """)
        print("  ✓ Created TufeFetchSession table")
        
        # 3. Create TufeSourceManager table
        print("3. Creating TufeSourceManager table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tufe_source_managers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                active_sources TEXT DEFAULT '[]',
                health_check_interval INTEGER DEFAULT 300 CHECK(health_check_interval >= 60 AND health_check_interval <= 3600),
                failure_threshold INTEGER DEFAULT 3 CHECK(failure_threshold >= 1 AND failure_threshold <= 10),
                success_threshold INTEGER DEFAULT 2 CHECK(success_threshold >= 1 AND success_threshold <= 10),
                max_retry_attempts INTEGER DEFAULT 3 CHECK(max_retry_attempts >= 1 AND max_retry_attempts <= 5),
                retry_delay INTEGER DEFAULT 5 CHECK(retry_delay >= 1 AND retry_delay <= 60),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ Created TufeSourceManager table")
        
        # 4. Create TufeAutoConfig table
        print("4. Creating TufeAutoConfig table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tufe_auto_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name TEXT UNIQUE NOT NULL,
                auto_discovery_enabled BOOLEAN DEFAULT 1,
                default_priority_order TEXT DEFAULT '[]',
                fallback_to_manual BOOLEAN DEFAULT 1,
                cache_duration_hours INTEGER DEFAULT 24 CHECK(cache_duration_hours >= 1 AND cache_duration_hours <= 168),
                validation_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ Created TufeAutoConfig table")
        
        # 5. Enhance TufeApiKey table with new fields
        print("5. Enhancing TufeApiKey table...")
        cursor.execute("PRAGMA table_info(tufe_api_keys)")
        existing_api_key_columns = [row[1] for row in cursor.fetchall()]
        
        new_api_key_columns = [
            ("source_priority", "INTEGER DEFAULT 5"),
            ("auto_configured", "BOOLEAN DEFAULT 0"),
            ("last_used", "TIMESTAMP"),
            ("usage_count", "INTEGER DEFAULT 0"),
            ("is_valid", "BOOLEAN DEFAULT 1")
        ]
        
        for column_name, column_def in new_api_key_columns:
            if column_name not in existing_api_key_columns:
                try:
                    cursor.execute(f"ALTER TABLE tufe_api_keys ADD COLUMN {column_name} {column_def}")
                    print(f"  ✓ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"  ⚠️ Column {column_name} might already exist: {e}")
        
        # 6. Enhance TufeDataCache table with new fields
        print("6. Enhancing TufeDataCache table...")
        cursor.execute("PRAGMA table_info(tufe_data_cache)")
        existing_cache_columns = [row[1] for row in cursor.fetchall()]
        
        new_cache_columns = [
            ("source_attempts", "TEXT DEFAULT '[]'"),
            ("fetch_duration", "REAL DEFAULT 0.0"),
            ("validation_status", "TEXT DEFAULT 'valid' CHECK(validation_status IN ('valid', 'invalid', 'warning'))"),
            ("data_quality_score", "REAL DEFAULT 1.0 CHECK(data_quality_score >= 0.0 AND data_quality_score <= 1.0)")
        ]
        
        for column_name, column_def in new_cache_columns:
            if column_name not in existing_cache_columns:
                try:
                    cursor.execute(f"ALTER TABLE tufe_data_cache ADD COLUMN {column_name} {column_def}")
                    print(f"  ✓ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"  ⚠️ Column {column_name} might already exist: {e}")
        
        # 7. Create indexes for performance
        print("7. Creating performance indexes...")
        
        indexes = [
            ("idx_tufe_data_sources_priority", "tufe_data_sources", "priority"),
            ("idx_tufe_data_sources_health_status", "tufe_data_sources", "health_status"),
            ("idx_tufe_fetch_sessions_status", "tufe_fetch_sessions", "status"),
            ("idx_tufe_fetch_sessions_session_id", "tufe_fetch_sessions", "session_id"),
            ("idx_tufe_data_cache_year", "tufe_data_cache", "year"),
            ("idx_tufe_api_keys_source_id", "tufe_api_keys", "source_id")
        ]
        
        for index_name, table_name, column_name in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
                print(f"  ✓ Created index: {index_name}")
            except sqlite3.Error as e:
                print(f"  ⚠️ Index {index_name} might already exist: {e}")
        
        # 8. Insert default data
        print("8. Inserting default data...")
        
        # Insert default source manager
        cursor.execute("""
            INSERT OR IGNORE INTO tufe_source_managers (name, active_sources, health_check_interval, failure_threshold, success_threshold, max_retry_attempts, retry_delay)
            VALUES ('default_manager', '[]', 300, 3, 2, 3, 5)
        """)
        print("  ✓ Inserted default source manager")
        
        # Insert default auto config
        cursor.execute("""
            INSERT OR IGNORE INTO tufe_auto_configs (config_name, auto_discovery_enabled, default_priority_order, fallback_to_manual, cache_duration_hours, validation_enabled)
            VALUES ('default_config', 1, '[]', 1, 24, 1)
        """)
        print("  ✓ Inserted default auto config")
        
        # Update existing TufeDataSource records with default values
        cursor.execute("""
            UPDATE tufe_data_sources 
            SET priority = 5, reliability_score = 0.5, health_status = 'unknown', failure_count = 0, success_count = 0, avg_response_time = 0.0, rate_limit_remaining = 1000
            WHERE priority IS NULL
        """)
        print("  ✓ Updated existing TufeDataSource records with default values")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show summary
        print("\n📊 Migration Summary:")
        cursor.execute("SELECT COUNT(*) FROM tufe_data_sources")
        print(f"  - TufeDataSource records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM tufe_fetch_sessions")
        print(f"  - TufeFetchSession records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM tufe_source_managers")
        print(f"  - TufeSourceManager records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM tufe_auto_configs")
        print(f"  - TufeAutoConfig records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM tufe_api_keys")
        print(f"  - TufeApiKey records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM tufe_data_cache")
        print(f"  - TufeDataCache records: {cursor.fetchone()[0]}")

if __name__ == "__main__":
    run_migration()
