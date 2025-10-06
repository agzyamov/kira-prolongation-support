#!/usr/bin/env python3
"""
Database migration to enhance TÜFE tables for OECD API integration
"""

import sqlite3
import os
from pathlib import Path

def migrate_enhance_oecd_tables():
    """Enhance existing TÜFE tables for OECD API integration"""
    
    print("🔧 Enhancing TÜFE tables for OECD API integration...")
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Try both possible database paths
    db_paths = [
        Path("rental_negotiation.db"),
        data_dir / "rental_negotiation.db"
    ]
    
    db_path = None
    for path in db_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found in any of the expected locations:")
        for path in db_paths:
            print(f"   - {path}")
        print("Please run the base TÜFE migration first")
        return False
    
    print(f"📊 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 Adding rate limiting fields to tufe_data_sources...")
        
        # Check if rate limiting fields already exist in tufe_data_sources
        cursor.execute("PRAGMA table_info(tufe_data_sources)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        if 'rate_limit_remaining' not in existing_columns:
            cursor.execute("""
                ALTER TABLE tufe_data_sources 
                ADD COLUMN rate_limit_remaining INTEGER DEFAULT NULL
            """)
            print("   ✅ Added rate_limit_remaining column")
        else:
            print("   ⚠️ rate_limit_remaining column already exists")
        
        if 'rate_limit_reset' not in existing_columns:
            cursor.execute("""
                ALTER TABLE tufe_data_sources 
                ADD COLUMN rate_limit_reset TIMESTAMP DEFAULT NULL
            """)
            print("   ✅ Added rate_limit_reset column")
        else:
            print("   ⚠️ rate_limit_reset column already exists")
        
        print("📊 Adding TTL fields to tufe_data_cache...")
        
        # Check if TTL fields already exist in tufe_data_cache
        cursor.execute("PRAGMA table_info(tufe_data_cache)")
        existing_cache_columns = [row[1] for row in cursor.fetchall()]
        
        if 'expires_at' not in existing_cache_columns:
            cursor.execute("""
                ALTER TABLE tufe_data_cache 
                ADD COLUMN expires_at TIMESTAMP NOT NULL DEFAULT (datetime('now', '+7 days'))
            """)
            print("   ✅ Added expires_at column")
        else:
            print("   ⚠️ expires_at column already exists")
        
        if 'fetch_duration' not in existing_cache_columns:
            cursor.execute("""
                ALTER TABLE tufe_data_cache 
                ADD COLUMN fetch_duration REAL DEFAULT NULL
            """)
            print("   ✅ Added fetch_duration column")
        else:
            print("   ⚠️ fetch_duration column already exists")
        
        if 'retry_count' not in existing_cache_columns:
            cursor.execute("""
                ALTER TABLE tufe_data_cache 
                ADD COLUMN retry_count INTEGER DEFAULT 0
            """)
            print("   ✅ Added retry_count column")
        else:
            print("   ⚠️ retry_count column already exists")
        
        print("📊 Creating new tables for OECD API integration...")
        
        # Create rate limiting configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                max_requests_per_hour INTEGER DEFAULT 100,
                max_requests_per_day INTEGER DEFAULT 1000,
                backoff_factor REAL DEFAULT 2.0,
                max_retries INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES tufe_data_sources (id)
            )
        """)
        print("   ✅ Created rate_limit_config table")
        
        # Create API request logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT DEFAULT 'GET',
                status_code INTEGER,
                response_time REAL,
                rate_limit_remaining INTEGER,
                rate_limit_reset TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES tufe_data_sources (id)
            )
        """)
        print("   ✅ Created api_request_logs table")
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tufe_cache_expires_at 
            ON tufe_data_cache (expires_at)
        """)
        print("   ✅ Created index on tufe_data_cache.expires_at")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_logs_created_at 
            ON api_request_logs (created_at)
        """)
        print("   ✅ Created index on api_request_logs.created_at")
        
        # Insert default OECD data source if it doesn't exist
        cursor.execute("""
            SELECT COUNT(*) FROM tufe_data_sources 
            WHERE source_name = 'OECD SDMX API'
        """)
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("""
                INSERT INTO tufe_data_sources (
                    source_name, api_endpoint, series_code, data_format, requires_auth, 
                    rate_limit_per_hour, is_active, priority, reliability_score, health_status
                ) VALUES (
                    'OECD SDMX API',
                    'https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all',
                    'A.TUR.CPALTT01.M',
                    'xml',
                    0,
                    100,
                    1,
                    1,
                    0.95,
                    'unknown'
                )
            """)
            print("   ✅ Inserted default OECD SDMX API data source")
        else:
            print("   ⚠️ OECD SDMX API data source already exists")
        
        # Insert default rate limit configuration
        cursor.execute("""
            SELECT id FROM tufe_data_sources WHERE source_name = 'OECD SDMX API'
        """)
        result = cursor.fetchone()
        if result:
            source_id = result[0]
            cursor.execute("""
                SELECT COUNT(*) FROM rate_limit_config WHERE source_id = ?
            """, (source_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("""
                    INSERT INTO rate_limit_config (
                        source_id, max_requests_per_hour, max_requests_per_day,
                        backoff_factor, max_retries
                    ) VALUES (?, 100, 1000, 2.0, 3)
                """, (source_id,))
                print("   ✅ Inserted default rate limit configuration")
            else:
                print("   ⚠️ Rate limit configuration already exists")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM tufe_data_sources")
        sources_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tufe_data_cache")
        cache_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rate_limit_config")
        config_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Summary:")
        print(f"   TÜFE Data Sources: {sources_count}")
        print(f"   TÜFE Data Cache: {cache_count}")
        print(f"   Rate Limit Configs: {config_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = migrate_enhance_oecd_tables()
    if success:
        print("\n🎯 Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        exit(1)
