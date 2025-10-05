# Data Model: Add New Functional Requirements

**Feature**: Add New Functional Requirements for Rental Fee Negotiation Support Tool  
**Date**: 2025-10-05  
**Branch**: 003-add-new-functional

## Entity Extensions

### RentalAgreement (Extended)
**File**: `src/models/rental_agreement.py`

**New Fields**:
- No new fields required - existing `start_date` and `end_date` are sufficient for legal rule determination

**New Methods**:
- `get_legal_rule_for_date(date: datetime) -> str`: Returns applicable legal rule ("25%_cap" or "cpi_based")
- `get_legal_rule_label(date: datetime) -> str`: Returns human-readable label ("+25% (limit until July 2024)" or "+CPI (Yearly TÜFE)")

**Validation Rules**:
- Existing validation remains unchanged
- New methods must handle edge cases (dates outside agreement period)

### InflationData (Extended)
**File**: `src/models/inflation_data.py`

**New Fields**:
- No new fields required - existing structure supports TÜFE data

**New Methods**:
- `get_yearly_tufe(year: int) -> Optional[Decimal]`: Returns yearly TÜFE rate for given year
- `is_tufe_available(year: int) -> bool`: Checks if TÜFE data is available for given year

**Validation Rules**:
- Existing validation remains unchanged
- New methods must handle missing data gracefully

## New Entities

### NegotiationSettings
**File**: `src/models/negotiation_settings.py`

**Fields**:
- `mode: str` - "calm" or "assertive"
- `created_at: datetime` - when setting was created
- `updated_at: datetime` - when setting was last updated

**Validation Rules**:
- `mode` must be one of ["calm", "assertive"]
- `created_at` and `updated_at` must be valid datetime objects

**Methods**:
- `is_calm_mode() -> bool`: Returns True if mode is "calm"
- `is_assertive_mode() -> bool`: Returns True if mode is "assertive"

### LegalRule
**File**: `src/models/legal_rule.py`

**Fields**:
- `rule_type: str` - "25%_cap" or "cpi_based"
- `effective_start: datetime` - when rule becomes effective
- `effective_end: datetime` - when rule expires (None for current rules)
- `rate: Optional[Decimal]` - fixed rate for 25% cap, None for CPI-based
- `label: str` - human-readable description

**Validation Rules**:
- `rule_type` must be one of ["25%_cap", "cpi_based"]
- `effective_start` must be before `effective_end` (if not None)
- `rate` must be positive if provided
- `label` must not be empty

**Methods**:
- `is_applicable_for_date(date: datetime) -> bool`: Checks if rule applies to given date
- `get_display_label() -> str`: Returns formatted label for UI display

## Database Schema Changes

### New Tables

#### negotiation_settings
```sql
CREATE TABLE IF NOT EXISTS negotiation_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('calm', 'assertive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### legal_rules
```sql
CREATE TABLE IF NOT EXISTS legal_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type VARCHAR(20) NOT NULL CHECK (rule_type IN ('25%_cap', 'cpi_based')),
    effective_start DATE NOT NULL,
    effective_end DATE,
    rate DECIMAL(6, 2),
    label VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Data Initialization

#### Default Legal Rules
```sql
INSERT INTO legal_rules (rule_type, effective_start, effective_end, rate, label) VALUES
('25%_cap', '2020-01-01', '2024-06-30', 25.00, '+25% (limit until July 2024)'),
('cpi_based', '2024-07-01', NULL, NULL, '+CPI (Yearly TÜFE)');
```

#### Default Negotiation Settings
```sql
INSERT INTO negotiation_settings (mode) VALUES ('calm');
```

## State Transitions

### NegotiationSettings
- **Initial State**: mode = "calm" (default)
- **Transition**: User changes mode via UI
- **Final State**: mode = "assertive" or "calm" (user choice)

### LegalRule
- **Initial State**: Rules loaded from database initialization
- **Transition**: System determines applicable rule based on date
- **Final State**: Rule selected for calculation

## Relationships

### RentalAgreement → LegalRule
- **Relationship**: Many-to-One (agreement can have multiple applicable rules over time)
- **Implementation**: Date-based lookup in `get_legal_rule_for_date()`

### NegotiationSettings → User Interface
- **Relationship**: One-to-One (single setting per session)
- **Implementation**: Streamlit session state with database persistence

### InflationData → LegalRule
- **Relationship**: One-to-Many (TÜFE data supports CPI-based rules)
- **Implementation**: Year-based lookup in `get_yearly_tufe()`

## Data Flow

1. **User selects negotiation mode** → NegotiationSettings updated in session state
2. **System calculates legal rule** → RentalAgreement.get_legal_rule_for_date() called
3. **Rule determination** → LegalRule.is_applicable_for_date() returns applicable rule
4. **TÜFE data lookup** → InflationData.get_yearly_tufe() called if CPI-based rule
5. **Display generation** → LegalRule.get_display_label() returns formatted text
6. **Chart generation** → NegotiationSettings.mode affects visual styling
7. **Export generation** → Data source disclosure added to all exports
