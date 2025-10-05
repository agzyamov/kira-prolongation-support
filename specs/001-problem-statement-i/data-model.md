# Data Model: Rental Fee Negotiation Support Tool

**Date**: 2025-10-05  
**Purpose**: Define data entities and their relationships  
**Source**: Derived from spec.md requirements

## Entity Overview

This application manages five core entities:

1. **RentalAgreement**: Time-bound rental contracts with pricing
2. **ExchangeRate**: Historical USD/TL exchange rate data
3. **PaymentRecord**: Calculated monthly payments in TL and USD
4. **MarketRate**: Comparable apartment rents from screenshots
5. **InflationData**: Turkish official inflation rates

## Entity Definitions

### 1. RentalAgreement

Represents a rental agreement period with associated pricing rules.

**Attributes**:
```python
id: int  # Primary key
start_date: date  # Agreement start (month/year precision)
end_date: date  # Agreement end (month/year precision)
base_amount_tl: decimal  # Base monthly rent in Turkish Lira
conditional_rules: Optional[JSON]  # Conditional pricing (see below)
notes: Optional[str]  # User notes about this agreement
created_at: datetime
updated_at: datetime
```

**Conditional Rules Structure** (JSON):
```json
{
  "condition_type": "exchange_rate",
  "rules": [
    {
      "condition": "usd_tl_rate < 40",
      "amount_tl": 35000
    },
    {
      "condition": "usd_tl_rate >= 40",
      "amount_tl": 40000
    }
  ],
  "applies_from": "2024-12-01"
}
```

**Business Rules**:
- start_date must be before end_date
- base_amount_tl must be > 0
- Agreements should not overlap (warning, not hard constraint)
- Conditional rules are optional
- Dates stored as YYYY-MM (month precision sufficient)

**Example**:
```python
RentalAgreement(
    id=1,
    start_date=date(2022, 11, 1),
    end_date=date(2023, 10, 31),
    base_amount_tl=15000,
    conditional_rules=None,
    notes="Initial agreement"
)

RentalAgreement(
    id=4,
    start_date=date(2024, 12, 1),
    end_date=None,  # Current/ongoing
    base_amount_tl=31000,
    conditional_rules={...},  # As shown above
    notes="Agreement with USD rate conditions"
)
```

### 2. ExchangeRate

Historical USD/TL exchange rates (monthly averages for payment calculations).

**Attributes**:
```python
id: int  # Primary key
month: int  # 1-12
year: int  # e.g., 2024
rate_tl_per_usd: decimal  # How many TL for 1 USD (e.g., 32.50)
source: str  # "TCMB" or "exchangerate-api.io"
fetched_at: datetime  # When data was retrieved
```

**Business Rules**:
- Unique constraint on (month, year)
- rate_tl_per_usd must be > 0
- Rates are cached locally to minimize API calls
- If multiple rates exist for same month/year, use most recent fetch

**Example**:
```python
ExchangeRate(
    id=1,
    month=11,
    year=2022,
    rate_tl_per_usd=18.65,  # Monthly average
    source="TCMB",
    fetched_at=datetime(2025, 10, 5, 10, 30)
)
```

### 3. PaymentRecord

Calculated monthly payments combining rental agreements and exchange rates.

**Attributes**:
```python
id: int  # Primary key
agreement_id: int  # Foreign key to RentalAgreement
month: int  # 1-12
year: int  # e.g., 2024
amount_tl: decimal  # Actual amount paid in TL
amount_usd: decimal  # Calculated USD equivalent
exchange_rate_id: int  # Foreign key to ExchangeRate used
calculated_at: datetime  # When this record was generated
```

**Relationships**:
- Many-to-one with RentalAgreement
- Many-to-one with ExchangeRate

**Business Rules**:
- amount_tl determined by agreement base_amount or conditional rules
- amount_usd = amount_tl / exchange_rate
- Unique constraint on (agreement_id, month, year)
- Records are recalculated if exchange rates update

**Calculation Logic**:
```python
def calculate_payment(agreement, month, year, exchange_rate):
    # Check if conditional rules apply
    if agreement.conditional_rules:
        for rule in agreement.conditional_rules['rules']:
            if evaluate_condition(rule['condition'], exchange_rate.rate_tl_per_usd):
                amount_tl = rule['amount_tl']
                break
    else:
        amount_tl = agreement.base_amount_tl
    
    amount_usd = amount_tl / exchange_rate.rate_tl_per_usd
    
    return PaymentRecord(
        agreement_id=agreement.id,
        month=month,
        year=year,
        amount_tl=amount_tl,
        amount_usd=amount_usd,
        exchange_rate_id=exchange_rate.id
    )
```

**Example**:
```python
PaymentRecord(
    id=1,
    agreement_id=1,
    month=11,
    year=2022,
    amount_tl=15000,
    amount_usd=804.29,  # 15000 / 18.65
    exchange_rate_id=1
)
```

### 4. MarketRate

Comparable apartment rental rates parsed from sahibinden.com screenshots.

**Attributes**:
```python
id: int  # Primary key
amount_tl: decimal  # Rental price in TL
location: Optional[str]  # Area/district if parseable
screenshot_filename: str  # Original screenshot file reference
parsed_at: datetime  # When OCR parsing occurred
confidence: Optional[float]  # OCR confidence score (0-1)
verified: bool  # User confirmed this is accurate
notes: Optional[str]  # User notes about this listing
```

**Business Rules**:
- amount_tl must be > 0
- screenshot_filename must be unique
- If confidence < 0.7, mark for user verification
- User can manually edit amount if OCR was wrong

**Example**:
```python
MarketRate(
    id=1,
    amount_tl=38000,
    location="Kadıköy",  # Extracted from screenshot if possible
    screenshot_filename="sahibinden_2025_10_05_001.png",
    parsed_at=datetime(2025, 10, 5, 11, 00),
    confidence=0.92,
    verified=True,
    notes="3+1, 120m2, similar building"
)
```

### 5. InflationData

Turkish official inflation rates (for showing legal maximum rent increase).

**Attributes**:
```python
id: int  # Primary key
month: int  # 1-12
year: int  # e.g., 2024
inflation_rate_percent: decimal  # e.g., 64.77 for 64.77%
source: str  # "TUIK" (Turkish Statistical Institute)
notes: Optional[str]  # Context about this rate
created_at: datetime
```

**Business Rules**:
- Unique constraint on (month, year)
- inflation_rate_percent can be negative (deflation)
- Used to calculate legal maximum rent increase:
  - legal_max_increase = previous_rent * (1 + inflation_rate / 100)

**Example**:
```python
InflationData(
    id=1,
    month=10,
    year=2024,
    inflation_rate_percent=49.38,  # Turkish YoY inflation
    source="TUIK",
    notes="Annual inflation rate"
)
```

## Entity Relationships

```
RentalAgreement (1) ──→ (N) PaymentRecord
                                ↓
                          ExchangeRate (N) ──→ (1)

MarketRate (standalone, no direct relationships)

InflationData (standalone, used for calculations)
```

**Key Relationships**:
1. One `RentalAgreement` has many `PaymentRecords` (one per month)
2. Each `PaymentRecord` references one `ExchangeRate` for that month
3. `MarketRate` and `InflationData` are reference data (no foreign keys)

## SQLite Schema

```sql
CREATE TABLE rental_agreements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date DATE NOT NULL,
    end_date DATE,
    base_amount_tl DECIMAL(10, 2) NOT NULL,
    conditional_rules TEXT,  -- JSON stored as TEXT
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
    year INTEGER NOT NULL,
    rate_tl_per_usd DECIMAL(10, 4) NOT NULL,
    source VARCHAR(50) NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month, year)
);

CREATE TABLE payment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agreement_id INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
    year INTEGER NOT NULL,
    amount_tl DECIMAL(10, 2) NOT NULL,
    amount_usd DECIMAL(10, 2) NOT NULL,
    exchange_rate_id INTEGER NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agreement_id) REFERENCES rental_agreements(id),
    FOREIGN KEY (exchange_rate_id) REFERENCES exchange_rates(id),
    UNIQUE(agreement_id, month, year)
);

CREATE TABLE market_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_tl DECIMAL(10, 2) NOT NULL,
    location VARCHAR(255),
    screenshot_filename VARCHAR(255) NOT NULL UNIQUE,
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence DECIMAL(3, 2),
    verified BOOLEAN DEFAULT FALSE,
    notes TEXT
);

CREATE TABLE inflation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
    year INTEGER NOT NULL,
    inflation_rate_percent DECIMAL(6, 2) NOT NULL,
    source VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month, year)
);

-- Indexes for performance
CREATE INDEX idx_payment_records_agreement ON payment_records(agreement_id);
CREATE INDEX idx_payment_records_date ON payment_records(year, month);
CREATE INDEX idx_exchange_rates_date ON exchange_rates(year, month);
CREATE INDEX idx_inflation_date ON inflation_data(year, month);
```

## Python Class Definitions

```python
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, List

@dataclass
class RentalAgreement:
    id: Optional[int]
    start_date: date
    end_date: Optional[date]
    base_amount_tl: Decimal
    conditional_rules: Optional[Dict]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class ExchangeRate:
    id: Optional[int]
    month: int
    year: int
    rate_tl_per_usd: Decimal
    source: str
    fetched_at: datetime

@dataclass
class PaymentRecord:
    id: Optional[int]
    agreement_id: int
    month: int
    year: int
    amount_tl: Decimal
    amount_usd: Decimal
    exchange_rate_id: int
    calculated_at: datetime

@dataclass
class MarketRate:
    id: Optional[int]
    amount_tl: Decimal
    location: Optional[str]
    screenshot_filename: str
    parsed_at: datetime
    confidence: Optional[float]
    verified: bool
    notes: Optional[str]

@dataclass
class InflationData:
    id: Optional[int]
    month: int
    year: int
    inflation_rate_percent: Decimal
    source: str
    notes: Optional[str]
    created_at: datetime
```

## Data Validation Rules

1. **Date Validation**:
   - start_date < end_date (if end_date provided)
   - Dates must be valid (month 1-12, reasonable years)

2. **Amount Validation**:
   - All monetary amounts must be > 0
   - Precision: 2 decimal places for TL, USD
   - Exchange rates: 4 decimal places

3. **Foreign Key Integrity**:
   - payment_records.agreement_id must reference existing rental_agreement
   - payment_records.exchange_rate_id must reference existing exchange_rate

4. **Uniqueness Constraints**:
   - (month, year) unique in exchange_rates
   - (month, year) unique in inflation_data
   - (agreement_id, month, year) unique in payment_records
   - screenshot_filename unique in market_rates

## Data Flow

1. **User enters rental agreements** → `rental_agreements` table
2. **App fetches exchange rates** → `exchange_rates` table (cached)
3. **App calculates payments** → `payment_records` table (derived)
4. **User uploads screenshots** → OCR → `market_rates` table
5. **User uploads/enters inflation** → `inflation_data` table

## Storage Estimates

| Entity | Records | Size per Record | Total Size |
|--------|---------|-----------------|------------|
| rental_agreements | 10 | 200 bytes | 2 KB |
| exchange_rates | 50 | 100 bytes | 5 KB |
| payment_records | 150 | 150 bytes | 22 KB |
| market_rates | 100 | 300 bytes | 30 KB |
| inflation_data | 50 | 100 bytes | 5 KB |
| **Total** | **360** | - | **~64 KB** |

**Plus Screenshots**: 100 screenshots × 500 KB avg = 50 MB  
**Grand Total**: ~50 MB (well under 100MB constraint)

## Next Steps

Phase 1 continues with:
- **contracts/**: Service interface definitions
- **quickstart.md**: Manual testing guide
- **Agent context update**: Tech stack summary for Cursor

