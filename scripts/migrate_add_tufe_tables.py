import sqlite3
from datetime import datetime, date
from decimal import Decimal

def migrate_add_tufe_tables():
    """Add new tables for TÜFE data sources, API keys, and caching."""
    db_path = "rental_negotiation.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tufe_data_sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tufe_data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                api_endpoint TEXT NOT NULL,
                series_code TEXT NOT NULL,
                data_format TEXT NOT NULL CHECK(data_format IN ('json', 'xml')),
                requires_auth BOOLEAN NOT NULL DEFAULT 1,
                rate_limit_per_hour INTEGER NOT NULL DEFAULT 100,
                last_verified TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create tufe_api_keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tufe_api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT NOT NULL,
                api_key TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                FOREIGN KEY (source_id) REFERENCES tufe_data_sources(id)
            );
        """)

        # Create tufe_data_cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tufe_data_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL CHECK(year BETWEEN 2000 AND 2100),
                tufe_rate DECIMAL(6,2) NOT NULL,
                source_name TEXT NOT NULL,
                fetched_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                api_response TEXT,
                is_validated BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(year, source_name)
            );
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tufe_cache_year ON tufe_data_cache(year);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tufe_cache_expires ON tufe_data_cache(expires_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tufe_api_keys_source ON tufe_api_keys(source_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tufe_sources_active ON tufe_data_sources(is_active);")

        conn.commit()
        print("✅ Successfully added TÜFE data source tables:")
        print("  - tufe_data_sources")
        print("  - tufe_api_keys")
        print("  - tufe_data_cache")
        print("  - All required indexes")

        # Insert default TCMB EVDS data source
        cursor.execute("SELECT COUNT(*) FROM tufe_data_sources WHERE source_name = 'TCMB EVDS API'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO tufe_data_sources 
                (source_name, api_endpoint, series_code, data_format, requires_auth, rate_limit_per_hour, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                'TCMB EVDS API',
                'https://evds2.tcmb.gov.tr/service/evds/',
                'TP.FE.OKTG01',
                'json',
                1,
                100,
                1
            ))
            conn.commit()
            print("  - Default TCMB EVDS data source inserted")

        # Verification
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tufe_data_sources';")
        tufe_sources_exists = cursor.fetchone()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tufe_api_keys';")
        tufe_keys_exists = cursor.fetchone()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tufe_data_cache';")
        tufe_cache_exists = cursor.fetchone()

        if tufe_sources_exists and tufe_keys_exists and tufe_cache_exists:
            print("✅ Verification: All TÜFE tables created successfully.")
        else:
            print("❌ Verification failed: One or more tables not found.")

    except sqlite3.Error as e:
        print(f"Database error during migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_add_tufe_tables()
