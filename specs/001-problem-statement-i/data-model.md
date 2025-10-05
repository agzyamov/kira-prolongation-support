# Data Model: Rental Fee Negotiation Support Tool

## Core Entities

### RentalAgreement
**Purpose**: Represents a rental contract period with associated terms
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `start_date`: Date (Required)
- `end_date`: Date (Optional, null for ongoing agreements)
- `base_amount_tl`: Decimal (Required, precision 2)
- `conditional_rules`: JSON (Optional, stores conditional pricing logic)
- `notes`: Text (Optional, user notes)
- `created_at`: DateTime (Auto-generated)
- `updated_at`: DateTime (Auto-updated)

**Validation Rules**:
- start_date must be before end_date (if provided)
- base_amount_tl must be positive
- conditional_rules must be valid JSON if provided
- No overlapping agreements allowed (enforced at application level)

**Relationships**:
- One-to-many with PaymentRecord
- One-to-many with AgreementPeriod

### ExchangeRate
**Purpose**: Historical USD/TL exchange rates from TCMB
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `date`: Date (Required, unique)
- `rate`: Decimal (Required, precision 4)
- `source`: String (Required, default: "TCMB")
- `created_at`: DateTime (Auto-generated)

**Validation Rules**:
- date must be unique
- rate must be positive
- source must be "TCMB" (constitutional requirement)

**Relationships**:
- Referenced by PaymentRecord for USD calculations

### PaymentRecord
**Purpose**: Individual rental payment with USD equivalent
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `agreement_id`: Integer (Foreign Key to RentalAgreement)
- `payment_date`: Date (Required)
- `amount_tl`: Decimal (Required, precision 2)
- `amount_usd`: Decimal (Required, precision 2)
- `exchange_rate`: Decimal (Required, precision 4)
- `created_at`: DateTime (Auto-generated)

**Validation Rules**:
- payment_date must be within agreement period
- amount_tl must be positive
- amount_usd must be positive
- exchange_rate must be positive

**Relationships**:
- Many-to-one with RentalAgreement
- References ExchangeRate for rate used

### MarketRate
**Purpose**: Comparable apartment rental data from screenshots
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `amount_tl`: Decimal (Required, precision 2)
- `location`: String (Optional, parsed from screenshot)
- `screenshot_filename`: String (Required)
- `confidence`: Decimal (Optional, OCR confidence score)
- `created_at`: DateTime (Auto-generated)

**Validation Rules**:
- amount_tl must be positive
- screenshot_filename must be provided
- confidence must be between 0 and 1 if provided

**Relationships**:
- None (standalone market data)

### InflationData
**Purpose**: Official Turkish inflation rates from TCMB
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `period`: Date (Required, unique)
- `inflation_rate`: Decimal (Required, precision 2)
- `source`: String (Required, default: "TCMB")
- `created_at`: DateTime (Auto-generated)

**Validation Rules**:
- period must be unique
- inflation_rate must be between -100 and 1000 (realistic range)
- source must be "TCMB"

**Relationships**:
- Referenced by LegalRule for period-specific rules

### LegalRule
**Purpose**: Applicable rent increase regulations by period
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `start_date`: Date (Required)
- `end_date`: Date (Optional, null for current rule)
- `rule_type`: String (Required, "fixed_cap" or "tufe")
- `cap_percentage`: Decimal (Optional, for fixed_cap rules)
- `description`: String (Required, human-readable description)
- `created_at`: DateTime (Auto-generated)

**Validation Rules**:
- start_date must be before end_date (if provided)
- rule_type must be "fixed_cap" or "tufe"
- cap_percentage required for fixed_cap rules
- No overlapping rules allowed

**Relationships**:
- Referenced by AgreementPeriod for rule determination

### AgreementPeriod
**Purpose**: Time segments of agreements that determine legal rules
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `agreement_id`: Integer (Foreign Key to RentalAgreement)
- `start_date`: Date (Required)
- `end_date`: Date (Required)
- `legal_rule_id`: Integer (Foreign Key to LegalRule)
- `created_at`: DateTime (Auto-generated)

**Validation Rules**:
- start_date must be before end_date
- period must be within agreement dates
- legal_rule_id must reference valid rule

**Relationships**:
- Many-to-one with RentalAgreement
- Many-to-one with LegalRule

### NegotiationMode
**Purpose**: User preference for presentation style
**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `mode`: String (Required, "calm" or "assertive")
- `description`: String (Required, user-friendly description)
- `created_at`: DateTime (Auto-generated)

**Validation Rules**:
- mode must be "calm" or "assertive"
- Only one active mode allowed (enforced at application level)

**Relationships**:
- Referenced by UI components for styling

## Database Schema

### Tables
```sql
-- Rental Agreements
CREATE TABLE rental_agreements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date DATE NOT NULL,
    end_date DATE,
    base_amount_tl DECIMAL(10,2) NOT NULL,
    conditional_rules TEXT, -- JSON
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Exchange Rates
CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    rate DECIMAL(10,4) NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'TCMB',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Payment Records
CREATE TABLE payment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agreement_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    amount_tl DECIMAL(10,2) NOT NULL,
    amount_usd DECIMAL(10,2) NOT NULL,
    exchange_rate DECIMAL(10,4) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agreement_id) REFERENCES rental_agreements(id)
);

-- Market Rates
CREATE TABLE market_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_tl DECIMAL(10,2) NOT NULL,
    location VARCHAR(255),
    screenshot_filename VARCHAR(255) NOT NULL,
    confidence DECIMAL(3,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Inflation Data
CREATE TABLE inflation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period DATE NOT NULL UNIQUE,
    inflation_rate DECIMAL(5,2) NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'TCMB',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Legal Rules
CREATE TABLE legal_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date DATE NOT NULL,
    end_date DATE,
    rule_type VARCHAR(20) NOT NULL,
    cap_percentage DECIMAL(5,2),
    description VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Agreement Periods
CREATE TABLE agreement_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agreement_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    legal_rule_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agreement_id) REFERENCES rental_agreements(id),
    FOREIGN KEY (legal_rule_id) REFERENCES legal_rules(id)
);

-- Negotiation Modes
CREATE TABLE negotiation_modes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_rental_agreements_dates ON rental_agreements(start_date, end_date);
CREATE INDEX idx_exchange_rates_date ON exchange_rates(date);
CREATE INDEX idx_payment_records_agreement ON payment_records(agreement_id);
CREATE INDEX idx_payment_records_date ON payment_records(payment_date);
CREATE INDEX idx_legal_rules_dates ON legal_rules(start_date, end_date);
CREATE INDEX idx_agreement_periods_agreement ON agreement_periods(agreement_id);
```

## Data Relationships

### Entity Relationship Diagram
```
RentalAgreement (1) ----< (N) PaymentRecord
RentalAgreement (1) ----< (N) AgreementPeriod
LegalRule (1) ----< (N) AgreementPeriod
ExchangeRate (1) ----< (N) PaymentRecord [via rate reference]
```

### Business Rules
1. **No Overlapping Agreements**: Only one active agreement per time period
2. **Legal Rule Application**: Agreements spanning July 1, 2024 use different rules for each period
3. **Exchange Rate Consistency**: All USD calculations use TCMB rates
4. **Data Source Attribution**: All data must include source information
5. **Negotiation Mode**: Only one active mode at a time

## Data Validation

### Input Validation
- Date ranges must be logical (start < end)
- Monetary amounts must be positive
- JSON fields must be valid JSON
- Required fields cannot be null

### Business Logic Validation
- Agreement periods cannot overlap
- Payment dates must be within agreement periods
- Exchange rates must be from TCMB
- Legal rules must be consistent with Turkish law

### Data Integrity
- Foreign key constraints enforced
- Unique constraints on critical fields
- Check constraints on value ranges
- Application-level validation for complex rules

## Data Migration

### Initial Data Setup
```sql
-- Insert default legal rules
INSERT INTO legal_rules (start_date, end_date, rule_type, cap_percentage, description) VALUES
('2020-01-01', '2024-06-30', 'fixed_cap', 25.00, '+25% (limit until July 2024)'),
('2024-07-01', NULL, 'tufe', NULL, '+CPI (Yearly TÜFE)');

-- Insert default negotiation modes
INSERT INTO negotiation_modes (mode, description) VALUES
('calm', 'Professional presentation with subdued visuals'),
('assertive', 'Bold presentation highlighting changes');
```

### Data Backup Strategy
- Export functionality for all user data
- SQLite file backup before major updates
- JSON export for data portability
- Screenshot files stored with metadata