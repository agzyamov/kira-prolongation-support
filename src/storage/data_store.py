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
    MarketRate,
    InflationData
)


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
        
        CREATE TABLE IF NOT EXISTS market_rates (
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
    
    # === MarketRate Methods ===
    
    def save_market_rate(self, rate: MarketRate) -> int:
        """Save market rate from screenshot"""
        sql = """
        INSERT INTO market_rates 
            (amount_tl, location, screenshot_filename, date_captured, confidence, raw_ocr_text, property_details, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    sql,
                    (
                        str(rate.amount_tl),
                        rate.location,
                        rate.screenshot_filename,
                        rate.date_captured.isoformat(),
                        rate.confidence,
                        rate.raw_ocr_text,
                        rate.property_details,
                        rate.notes,
                        rate.created_at.isoformat()
                    )
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save market rate: {e}")
    
    def get_market_rates(self, verified_only: bool = False) -> List[MarketRate]:
        """Get market rates"""
        sql = "SELECT * FROM market_rates ORDER BY date_captured DESC"
        
        try:
            with self._get_connection() as conn:
                rows = conn.execute(sql).fetchall()
                return [self._row_to_market_rate(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get market rates: {e}")
    
    def _row_to_market_rate(self, row: sqlite3.Row) -> MarketRate:
        """Convert database row to MarketRate object"""
        return MarketRate(
            id=row['id'],
            amount_tl=Decimal(str(row['amount_tl'])),
            location=row['location'],
            screenshot_filename=row['screenshot_filename'],
            date_captured=date.fromisoformat(row['date_captured']),
            confidence=float(row['confidence']) if row['confidence'] else None,
            raw_ocr_text=row['raw_ocr_text'],
            property_details=row['property_details'],
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

