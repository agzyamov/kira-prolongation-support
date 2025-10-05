"""
SQLite data persistence layer for Kira Prolongation Support.
Handles all database operations for the application.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from src.models import (
    RentalAgreement,
    ExchangeRate,
    PaymentRecord,
    InflationData
)
from src.models.negotiation_settings import NegotiationSettings
from src.models.legal_rule import LegalRule
from src.models.tufe_data_source import TufeDataSource
from src.models.tufe_api_key import TufeApiKey
from src.models.tufe_data_cache import TufeDataCache


class DatabaseError(Exception):
    """Raised when database operation fails"""
    pass


class DataStore:
    """
    SQLite data persistence layer.
    Manages all CRUD operations for the application.
    """
    
    def __init__(self, db_path: str = "data/kira.db"):
        """
        Initialize DataStore with database path.
        Creates database and schema if it doesn't exist.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database file and schema if it doesn't exist"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create schema if database is new
        if not db_file.exists() or db_file.stat().st_size == 0:
            self._create_schema()
    
    def _create_schema(self):
        """Create database schema with all tables and indexes"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS rental_agreements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date DATE NOT NULL,
            end_date DATE,
            base_amount_tl DECIMAL(10, 2) NOT NULL,
            conditional_rules TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            year INTEGER NOT NULL,
            rate_tl_per_usd DECIMAL(10, 4) NOT NULL,
            source VARCHAR(50) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(month, year)
        );
        
        CREATE TABLE IF NOT EXISTS payment_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agreement_id INTEGER NOT NULL,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            year INTEGER NOT NULL,
            amount_tl DECIMAL(10, 2) NOT NULL,
            amount_usd DECIMAL(10, 2) NOT NULL,
            exchange_rate_id INTEGER NOT NULL,
            payment_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agreement_id) REFERENCES rental_agreements(id),
            FOREIGN KEY (exchange_rate_id) REFERENCES exchange_rates(id),
            UNIQUE(agreement_id, month, year)
        );
        
        CREATE TABLE IF NOT EXISTS inflation_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            year INTEGER NOT NULL,
            inflation_rate_percent DECIMAL(6, 2) NOT NULL,
            source VARCHAR(50) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(month, year)
        );
        
        CREATE INDEX IF NOT EXISTS idx_payment_records_agreement 
            ON payment_records(agreement_id);
        CREATE INDEX IF NOT EXISTS idx_payment_records_date 
            ON payment_records(year, month);
        CREATE INDEX IF NOT EXISTS idx_exchange_rates_date 
            ON exchange_rates(year, month);
        CREATE INDEX IF NOT EXISTS idx_inflation_date 
            ON inflation_data(year, month);
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create database schema: {e}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with custom row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # === RentalAgreement Methods ===
    
    def save_rental_agreement(self, agreement: RentalAgreement) -> int:
        """
        Save rental agreement to database.
        
        Args:
            agreement: RentalAgreement instance to save
            
        Returns:
            ID of saved agreement
        """
        sql = """
        INSERT INTO rental_agreements 
            (start_date, end_date, base_amount_tl, conditional_rules, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        conditional_rules_json = json.dumps(agreement.conditional_rules) if agreement.conditional_rules else None
        
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    sql,
                    (
                        agreement.start_date.isoformat(),
                        agreement.end_date.isoformat() if agreement.end_date else None,
                        str(agreement.base_amount_tl),
                        conditional_rules_json,
                        agreement.notes,
                        agreement.created_at.isoformat(),
                        agreement.updated_at.isoformat()
                    )
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save rental agreement: {e}")
    
    def get_rental_agreements(self) -> List[RentalAgreement]:
        """Get all rental agreements, ordered by start_date"""
        sql = "SELECT * FROM rental_agreements ORDER BY start_date DESC"
        
        try:
            with self._get_connection() as conn:
                rows = conn.execute(sql).fetchall()
                return [self._row_to_rental_agreement(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get rental agreements: {e}")
    
    def _row_to_rental_agreement(self, row: sqlite3.Row) -> RentalAgreement:
        """Convert database row to RentalAgreement object"""
        return RentalAgreement(
            id=row['id'],
            start_date=date.fromisoformat(row['start_date']),
            end_date=date.fromisoformat(row['end_date']) if row['end_date'] else None,
            base_amount_tl=Decimal(str(row['base_amount_tl'])),
            conditional_rules=json.loads(row['conditional_rules']) if row['conditional_rules'] else None,
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    # === ExchangeRate Methods ===
    
    def save_exchange_rate(self, rate: ExchangeRate) -> None:
        """Save or update exchange rate in cache"""
        sql = """
        INSERT INTO exchange_rates (month, year, rate_tl_per_usd, source, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(month, year) DO UPDATE SET
            rate_tl_per_usd = excluded.rate_tl_per_usd,
            source = excluded.source,
            notes = excluded.notes
        """
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    sql,
                    (
                        rate.month,
                        rate.year,
                        str(rate.rate_tl_per_usd),
                        rate.source,
                        rate.notes,
                        rate.created_at.isoformat()
                    )
                )
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save exchange rate: {e}")
    
    def get_exchange_rate(self, month: int, year: int) -> Optional[ExchangeRate]:
        """Get cached exchange rate for specific month/year"""
        sql = "SELECT * FROM exchange_rates WHERE month = ? AND year = ?"
        
        try:
            with self._get_connection() as conn:
                row = conn.execute(sql, (month, year)).fetchone()
                return self._row_to_exchange_rate(row) if row else None
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get exchange rate: {e}")
    
    def _row_to_exchange_rate(self, row: sqlite3.Row) -> ExchangeRate:
        """Convert database row to ExchangeRate object"""
        return ExchangeRate(
            id=row['id'],
            month=row['month'],
            year=row['year'],
            rate_tl_per_usd=Decimal(str(row['rate_tl_per_usd'])),
            source=row['source'],
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    # === PaymentRecord Methods ===
    
    def save_payment_record(self, payment: PaymentRecord) -> int:
        """Save payment record"""
        sql = """
        INSERT INTO payment_records 
            (agreement_id, month, year, amount_tl, amount_usd, exchange_rate_id, payment_date, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(agreement_id, month, year) DO UPDATE SET
            amount_tl = excluded.amount_tl,
            amount_usd = excluded.amount_usd,
            exchange_rate_id = excluded.exchange_rate_id,
            payment_date = excluded.payment_date,
            notes = excluded.notes
        """
        
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    sql,
                    (
                        payment.agreement_id,
                        payment.month,
                        payment.year,
                        str(payment.amount_tl),
                        str(payment.amount_usd),
                        payment.exchange_rate_id,
                        payment.payment_date.isoformat() if payment.payment_date else None,
                        payment.notes,
                        payment.created_at.isoformat()
                    )
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save payment record: {e}")
    
    def get_payment_records(
        self, 
        agreement_id: Optional[int] = None
    ) -> List[PaymentRecord]:
        """Get payment records, optionally filtered by agreement"""
        if agreement_id:
            sql = "SELECT * FROM payment_records WHERE agreement_id = ? ORDER BY year, month"
            params = (agreement_id,)
        else:
            sql = "SELECT * FROM payment_records ORDER BY year, month"
            params = ()
        
        try:
            with self._get_connection() as conn:
                rows = conn.execute(sql, params).fetchall()
                return [self._row_to_payment_record(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get payment records: {e}")
    
    def _row_to_payment_record(self, row: sqlite3.Row) -> PaymentRecord:
        """Convert database row to PaymentRecord object"""
        return PaymentRecord(
            id=row['id'],
            agreement_id=row['agreement_id'],
            month=row['month'],
            year=row['year'],
            amount_tl=Decimal(str(row['amount_tl'])),
            amount_usd=Decimal(str(row['amount_usd'])),
            exchange_rate_id=row['exchange_rate_id'],
            payment_date=date.fromisoformat(row['payment_date']) if row['payment_date'] else None,
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    # === InflationData Methods ===
    
    def save_inflation_data(self, data: InflationData) -> None:
        """Save inflation data point"""
        sql = """
        INSERT INTO inflation_data (month, year, inflation_rate_percent, source, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(month, year) DO UPDATE SET
            inflation_rate_percent = excluded.inflation_rate_percent,
            source = excluded.source,
            notes = excluded.notes
        """
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    sql,
                    (
                        data.month,
                        data.year,
                        str(data.inflation_rate_percent),
                        data.source,
                        data.notes,
                        data.created_at.isoformat()
                    )
                )
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save inflation data: {e}")
    
    def get_inflation_data_range(
        self, 
        start_year: int, 
        end_year: int
    ) -> List[InflationData]:
        """Get inflation data for year range"""
        sql = """
        SELECT * FROM inflation_data 
        WHERE year BETWEEN ? AND ? 
        ORDER BY year, month
        """
        
        try:
            with self._get_connection() as conn:
                rows = conn.execute(sql, (start_year, end_year)).fetchall()
                return [self._row_to_inflation_data(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get inflation data: {e}")
    
    def _row_to_inflation_data(self, row: sqlite3.Row) -> InflationData:
        """Convert database row to InflationData object"""
        return InflationData(
            id=row['id'],
            month=row['month'],
            year=row['year'],
            inflation_rate_percent=Decimal(str(row['inflation_rate_percent'])),
            source=row['source'],
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    # NegotiationSettings methods
    def save_negotiation_settings(self, settings: NegotiationSettings) -> int:
        """
        Save negotiation settings to database.
        
        Args:
            settings: NegotiationSettings object to save
            
        Returns:
            ID of saved record
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO negotiation_settings (mode, created_at, updated_at)
                VALUES (?, ?, ?)
            """, (
                settings.mode,
                settings.created_at.isoformat(),
                settings.updated_at.isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_negotiation_settings(self) -> Optional[NegotiationSettings]:
        """
        Get current negotiation settings from database.
        
        Returns:
            NegotiationSettings object or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM negotiation_settings 
                ORDER BY updated_at DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if row:
                return self._row_to_negotiation_settings(row)
            return None
    
    def _row_to_negotiation_settings(self, row) -> NegotiationSettings:
        """Convert database row to NegotiationSettings object."""
        return NegotiationSettings(
            mode=row['mode'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    # LegalRule methods
    def save_legal_rule(self, rule: LegalRule) -> int:
        """
        Save legal rule to database.
        
        Args:
            rule: LegalRule object to save
            
        Returns:
            ID of saved record
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO legal_rules 
                (rule_type, effective_start, effective_end, rate, label, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rule.rule_type,
                rule.effective_start.isoformat(),
                rule.effective_end.isoformat() if rule.effective_end else None,
                float(rule.rate) if rule.rate else None,
                rule.label,
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_legal_rules(self) -> List[LegalRule]:
        """
        Get all legal rules from database.
        
        Returns:
            List of LegalRule objects
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM legal_rules 
                ORDER BY effective_start
            """)
            rows = cursor.fetchall()
            
            return [self._row_to_legal_rule(row) for row in rows]
    
    def _row_to_legal_rule(self, row) -> LegalRule:
        """Convert database row to LegalRule object."""
        return LegalRule(
            rule_type=row['rule_type'],
            effective_start=date.fromisoformat(row['effective_start']),
            effective_end=date.fromisoformat(row['effective_end']) if row['effective_end'] else None,
            rate=Decimal(str(row['rate'])) if row['rate'] else None,
            label=row['label']
        )
    
    # TÜFE Data Source methods
    def save_tufe_data_source(self, source: TufeDataSource) -> int:
        """Save a TÜFE data source."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if source.id is None:
                # Insert new source
                cursor.execute("""
                    INSERT INTO tufe_data_sources 
                    (source_name, api_endpoint, series_code, data_format, requires_auth, 
                     rate_limit_per_hour, last_verified, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    source.source_name,
                    source.api_endpoint,
                    source.series_code,
                    source.data_format,
                    source.requires_auth,
                    source.rate_limit_per_hour,
                    source.last_verified,
                    source.is_active
                ))
                return cursor.lastrowid
            else:
                # Update existing source
                cursor.execute("""
                    UPDATE tufe_data_sources 
                    SET source_name=?, api_endpoint=?, series_code=?, data_format=?, 
                        requires_auth=?, rate_limit_per_hour=?, last_verified=?, is_active=?
                    WHERE id=?
                """, (
                    source.source_name,
                    source.api_endpoint,
                    source.series_code,
                    source.data_format,
                    source.requires_auth,
                    source.rate_limit_per_hour,
                    source.last_verified,
                    source.is_active,
                    source.id
                ))
                return source.id
    
    def get_tufe_data_source_by_id(self, source_id: int) -> Optional[sqlite3.Row]:
        """Get a TÜFE data source by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_data_sources WHERE id=?", (source_id,))
            return cursor.fetchone()
    
    def get_all_tufe_data_sources(self) -> List[sqlite3.Row]:
        """Get all TÜFE data sources."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_data_sources ORDER BY created_at DESC")
            return cursor.fetchall()
    
    def get_active_tufe_data_source(self) -> Optional[sqlite3.Row]:
        """Get the active TÜFE data source."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_data_sources WHERE is_active=1 LIMIT 1")
            return cursor.fetchone()
    
    def _row_to_tufe_data_source(self, row) -> TufeDataSource:
        """Convert database row to TufeDataSource object."""
        return TufeDataSource(
            id=row['id'],
            source_name=row['source_name'],
            api_endpoint=row['api_endpoint'],
            series_code=row['series_code'],
            data_format=row['data_format'],
            requires_auth=bool(row['requires_auth']),
            rate_limit_per_hour=row['rate_limit_per_hour'],
            last_verified=datetime.fromisoformat(row['last_verified']) if row['last_verified'] else None,
            is_active=bool(row['is_active']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
    
    # TÜFE API Key methods
    def save_tufe_api_key(self, api_key: TufeApiKey) -> int:
        """Save a TÜFE API key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if api_key.id is None:
                # Insert new API key
                cursor.execute("""
                    INSERT INTO tufe_api_keys 
                    (key_name, api_key, source_id, last_used, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    api_key.key_name,
                    api_key._encrypt_key(api_key.api_key),  # Store encrypted
                    api_key.source_id,
                    api_key.last_used,
                    api_key.is_active
                ))
                return cursor.lastrowid
            else:
                # Update existing API key
                cursor.execute("""
                    UPDATE tufe_api_keys 
                    SET key_name=?, api_key=?, source_id=?, last_used=?, is_active=?
                    WHERE id=?
                """, (
                    api_key.key_name,
                    api_key._encrypt_key(api_key.api_key),  # Store encrypted
                    api_key.source_id,
                    api_key.last_used,
                    api_key.is_active,
                    api_key.id
                ))
                return api_key.id
    
    def get_tufe_api_key_by_id(self, key_id: int) -> Optional[sqlite3.Row]:
        """Get a TÜFE API key by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_api_keys WHERE id=?", (key_id,))
            return cursor.fetchone()
    
    def get_active_tufe_api_key(self, source_id: int) -> Optional[sqlite3.Row]:
        """Get the active API key for a source."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_api_keys WHERE source_id=? AND is_active=1 LIMIT 1", (source_id,))
            return cursor.fetchone()
    
    def get_tufe_api_keys_for_source(self, source_id: int) -> List[sqlite3.Row]:
        """Get all API keys for a source."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_api_keys WHERE source_id=? ORDER BY created_at DESC", (source_id,))
            return cursor.fetchall()
    
    def _row_to_tufe_api_key(self, row) -> TufeApiKey:
        """Convert database row to TufeApiKey object."""
        # Decrypt the API key
        decrypted_key = TufeApiKey._decrypt_key(row['api_key'])
        
        return TufeApiKey(
            id=row['id'],
            key_name=row['key_name'],
            api_key=decrypted_key,
            source_id=row['source_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else None,
            is_active=bool(row['is_active'])
        )
    
    # TÜFE Data Cache methods
    def save_tufe_data_cache(self, cache_entry: TufeDataCache) -> int:
        """Save a TÜFE data cache entry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if cache_entry.id is None:
                # Insert new cache entry
                cursor.execute("""
                    INSERT INTO tufe_data_cache 
                    (year, tufe_rate, source_name, fetched_at, expires_at, api_response, is_validated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    cache_entry.year,
                    str(cache_entry.tufe_rate),
                    cache_entry.source_name,
                    cache_entry.fetched_at,
                    cache_entry.expires_at,
                    cache_entry.api_response,
                    cache_entry.is_validated
                ))
                return cursor.lastrowid
            else:
                # Update existing cache entry
                cursor.execute("""
                    UPDATE tufe_data_cache 
                    SET year=?, tufe_rate=?, source_name=?, fetched_at=?, expires_at=?, 
                        api_response=?, is_validated=?
                    WHERE id=?
                """, (
                    cache_entry.year,
                    str(cache_entry.tufe_rate),
                    cache_entry.source_name,
                    cache_entry.fetched_at,
                    cache_entry.expires_at,
                    cache_entry.api_response,
                    cache_entry.is_validated,
                    cache_entry.id
                ))
                return cache_entry.id
    
    def get_tufe_data_cache(self, year: int) -> Optional[sqlite3.Row]:
        """Get TÜFE data cache for a year."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_data_cache WHERE year=? ORDER BY fetched_at DESC LIMIT 1", (year,))
            return cursor.fetchone()
    
    def get_all_tufe_data_cache(self) -> List[sqlite3.Row]:
        """Get all TÜFE data cache entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tufe_data_cache ORDER BY year DESC, fetched_at DESC")
            return cursor.fetchall()
    
    def _row_to_tufe_data_cache(self, row) -> TufeDataCache:
        """Convert database row to TufeDataCache object."""
        return TufeDataCache(
            id=row['id'],
            year=row['year'],
            tufe_rate=Decimal(str(row['tufe_rate'])),
            source_name=row['source_name'],
            fetched_at=datetime.fromisoformat(row['fetched_at']) if row['fetched_at'] else None,
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            api_response=row['api_response'],
            is_validated=bool(row['is_validated']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

