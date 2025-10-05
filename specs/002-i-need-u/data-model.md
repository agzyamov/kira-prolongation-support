# Data Model: Remove Market Comparison Feature

**Feature**: Remove Market Comparison Feature  
**Date**: 2025-10-05  
**Branch**: `002-i-need-u`

## Overview

This document defines the data model changes required to remove market comparison functionality from the Rental Fee Negotiation Support Tool. The changes focus on removing market-related entities while preserving all core rental tracking functionality.

## Entities to Remove

### MarketRate Entity
**Status**: DELETE

**Current Definition**:
```python
class MarketRate:
    id: int
    amount_tl: Decimal
    screenshot_filename: str
    date_captured: date
    location: Optional[str]
    confidence: Decimal
    raw_ocr_text: str
    created_at: datetime
```

**Removal Rationale**:
- Only used for market comparison feature
- No relationships with core rental data
- Safe to remove without affecting other functionality

**Database Impact**:
- Drop `market_rates` table
- Remove all market rate data
- No foreign key constraints to handle

## Entities to Preserve

### RentalAgreement Entity
**Status**: PRESERVE

**Current Definition**:
```python
class RentalAgreement:
    id: int
    start_date: date
    end_date: Optional[date]
    base_amount_tl: Decimal
    notes: Optional[str]
    has_conditional_pricing: bool
    created_at: datetime
```

**Preservation Rationale**:
- Core entity for rental tracking
- No market comparison dependencies
- Essential for primary use case

### ExchangeRate Entity
**Status**: PRESERVE

**Current Definition**:
```python
class ExchangeRate:
    id: int
    date: date
    rate: Decimal
    source: str
    created_at: datetime
```

**Preservation Rationale**:
- Core entity for USD equivalent calculations
- No market comparison dependencies
- Essential for negotiation support

### PaymentRecord Entity
**Status**: PRESERVE

**Current Definition**:
```python
class PaymentRecord:
    id: int
    rental_agreement_id: int
    payment_date: date
    amount_tl: Decimal
    amount_usd: Decimal
    exchange_rate: Decimal
    created_at: datetime
```

**Preservation Rationale**:
- Core entity for payment tracking
- No market comparison dependencies
- Essential for historical analysis

### InflationData Entity
**Status**: PRESERVE

**Current Definition**:
```python
class InflationData:
    id: int
    period: date
    inflation_rate: Decimal
    source: str
    created_at: datetime
```

**Preservation Rationale**:
- Used for legal maximum increase calculations
- No market comparison dependencies
- Important for negotiation context

## Database Schema Changes

### Tables to Remove

#### market_rates
```sql
DROP TABLE IF EXISTS market_rates;
```

**Migration Script**:
```sql
-- Remove market_rates table
DROP TABLE IF EXISTS market_rates;

-- Verify removal
SELECT name FROM sqlite_master WHERE type='table' AND name='market_rates';
-- Should return no results
```

### Tables to Preserve

All other tables remain unchanged:
- `rental_agreements`
- `exchange_rates`
- `payment_records`
- `inflation_data`
- `legal_rules`
- `negotiation_modes`

## Data Store Changes

### Methods to Remove

#### Market Rate Methods
```python
# Remove these methods from DataStore class:
def save_market_rate(self, market_rate) -> int
def get_market_rates(self, start_date=None, end_date=None)
def delete_market_rate(self, market_rate_id: int)
def get_market_rates_by_location(self, location: str)
```

### Methods to Preserve

All other DataStore methods remain unchanged:
- Rental agreement methods
- Exchange rate methods
- Payment record methods
- Inflation data methods
- Legal rule methods
- Negotiation mode methods

## Validation Rules

### Removed Validations
- Market rate amount validation
- Screenshot filename validation
- OCR confidence validation
- Location format validation

### Preserved Validations
- Rental agreement date validation
- Exchange rate validation
- Payment record validation
- Inflation data validation

## State Transitions

### Removed State Transitions
- Market rate creation workflow
- Screenshot processing workflow
- OCR result validation workflow

### Preserved State Transitions
- Rental agreement lifecycle
- Payment record calculation
- Exchange rate fetching
- Inflation data updates

## Data Migration Strategy

### Phase 1: Backup (Optional)
```sql
-- Create backup of market_rates table (if needed)
CREATE TABLE market_rates_backup AS SELECT * FROM market_rates;
```

### Phase 2: Remove Data
```sql
-- Remove all market rate data
DELETE FROM market_rates;
```

### Phase 3: Remove Table
```sql
-- Drop the table
DROP TABLE market_rates;
```

### Phase 4: Verify
```sql
-- Verify table is removed
SELECT name FROM sqlite_master WHERE type='table' AND name='market_rates';
-- Should return no results
```

## Impact Analysis

### No Impact Areas
- **Core Rental Tracking**: All rental agreement functionality preserved
- **Exchange Rate Calculations**: USD equivalent calculations unchanged
- **Payment History**: Historical payment tracking unaffected
- **Negotiation Support**: Core negotiation features preserved

### Affected Areas
- **Market Comparison**: Complete removal of market comparison functionality
- **Screenshot Processing**: No more OCR or image processing
- **Market Data Storage**: No more market rate data persistence

## Testing Considerations

### Tests to Remove
- Market rate model tests
- Screenshot parser tests
- Market comparison integration tests

### Tests to Update
- DataStore tests (remove market rate methods)
- Integration tests (remove market comparison scenarios)
- UI tests (remove market comparison page)

### Tests to Preserve
- All core rental tracking tests
- Exchange rate calculation tests
- Payment record tests
- Inflation data tests

## Conclusion

The data model changes for removing market comparison functionality are straightforward and low-risk. The MarketRate entity is well-isolated with no dependencies on core rental tracking functionality. The removal will simplify the data model while preserving all essential features for rental payment tracking and negotiation support.

**Key Benefits**:
- Simplified data model
- Reduced database complexity
- Fewer entities to maintain
- Clearer separation of concerns

**Risk Mitigation**:
- Comprehensive testing of core functionality
- Gradual removal approach
- Backup strategy for existing data
- Validation of no broken references
