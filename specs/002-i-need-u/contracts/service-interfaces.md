# Service Interfaces: Remove Market Comparison Feature

**Feature**: Remove Market Comparison Feature  
**Date**: 2025-10-05  
**Branch**: `002-i-need-u`

## Overview

This document defines the service interface changes required to remove market comparison functionality. The changes focus on removing market-related services while preserving all core rental tracking services.

## Services to Remove

### ScreenshotParserService
**Status**: DELETE

**Current Interface**:
```python
class ScreenshotParserService:
    def __init__(self)
    def parse_screenshot(self, image: Image.Image, screenshot_filename: str) -> List[MarketRate]
    def preprocess_image(self, image: Image.Image) -> Image.Image
    def extract_all_prices_from_text(self, text: str) -> List[Decimal]
    def extract_location(self, text: str) -> Optional[str]
```

**Removal Rationale**:
- Only used for market comparison feature
- No other services depend on it
- Safe to remove without affecting core functionality

**File to Delete**: `src/services/screenshot_parser.py`

## Services to Preserve

### ExchangeRateService
**Status**: PRESERVE

**Current Interface**:
```python
class ExchangeRateService:
    def __init__(self, data_store: DataStore)
    def fetch_exchange_rates(self, start_date: date, end_date: date) -> List[ExchangeRate]
    def get_exchange_rate(self, date: date) -> Optional[ExchangeRate]
    def save_exchange_rate(self, exchange_rate: ExchangeRate) -> int
```

**Preservation Rationale**:
- Core service for USD equivalent calculations
- No market comparison dependencies
- Essential for negotiation support

### CalculationService
**Status**: PRESERVE

**Current Interface**:
```python
class CalculationService:
    def __init__(self, exchange_rate_service: ExchangeRateService)
    def calculate_payment_records(self, rental_agreement: RentalAgreement) -> List[PaymentRecord]
    def calculate_usd_equivalent(self, amount_tl: Decimal, date: date) -> Decimal
    def apply_conditional_pricing(self, agreement: RentalAgreement, date: date) -> Decimal
```

**Preservation Rationale**:
- Core service for payment calculations
- No market comparison dependencies
- Essential for rental tracking

### InflationService
**Status**: PRESERVE

**Current Interface**:
```python
class InflationService:
    def __init__(self, data_store: DataStore)
    def fetch_inflation_data(self, start_date: date, end_date: date) -> List[InflationData]
    def get_legal_maximum_increase(self, date: date) -> Decimal
    def save_inflation_data(self, inflation_data: InflationData) -> int
```

**Preservation Rationale**:
- Used for legal maximum increase calculations
- No market comparison dependencies
- Important for negotiation context

### ExportService
**Status**: PRESERVE (with modifications)

**Current Interface**:
```python
class ExportService:
    def __init__(self)
    def generate_negotiation_summary(self, agreements: List[RentalAgreement], 
                                   payment_records: List[PaymentRecord],
                                   market_rates: List[MarketRate]) -> str
    def export_chart_as_png(self, chart_figure, filename: str) -> str
    def export_chart_as_pdf(self, chart_figure, filename: str) -> str
```

**Modifications Required**:
- Remove `market_rates` parameter from `generate_negotiation_summary`
- Update method to exclude market comparison data

**Updated Interface**:
```python
class ExportService:
    def __init__(self)
    def generate_negotiation_summary(self, agreements: List[RentalAgreement], 
                                   payment_records: List[PaymentRecord]) -> str
    def export_chart_as_png(self, chart_figure, filename: str) -> str
    def export_chart_as_pdf(self, chart_figure, filename: str) -> str
```

## DataStore Changes

### Methods to Remove

#### Market Rate Methods
```python
# Remove these methods from DataStore class:
def save_market_rate(self, market_rate: MarketRate) -> int
def get_market_rates(self, start_date: Optional[date] = None, 
                    end_date: Optional[date] = None) -> List[MarketRate]
def delete_market_rate(self, market_rate_id: int) -> bool
def get_market_rates_by_location(self, location: str) -> List[MarketRate]
```

### Methods to Preserve

All other DataStore methods remain unchanged:
- Rental agreement methods
- Exchange rate methods
- Payment record methods
- Inflation data methods
- Legal rule methods
- Negotiation mode methods

## Chart Generator Changes

### ChartGeneratorService
**Status**: PRESERVE (with modifications)

**Current Interface**:
```python
class ChartGenerator:
    def __init__(self)
    def create_tl_usd_chart(self, payment_records: List[PaymentRecord],
                          market_rates: List[MarketRate]) -> go.Figure
    def create_payment_history_chart(self, payment_records: List[PaymentRecord]) -> go.Figure
```

**Modifications Required**:
- Remove `market_rates` parameter from `create_tl_usd_chart`
- Update method to exclude market comparison overlays

**Updated Interface**:
```python
class ChartGenerator:
    def __init__(self)
    def create_tl_usd_chart(self, payment_records: List[PaymentRecord]) -> go.Figure
    def create_payment_history_chart(self, payment_records: List[PaymentRecord]) -> go.Figure
```

## Exception Handling Changes

### Exceptions to Remove

#### OCRError
```python
class OCRError(RentalNegotiationError):
    """Raised when OCR processing fails."""
    pass
```

**Removal Rationale**:
- Only used by ScreenshotParserService
- No other services use OCR functionality
- Safe to remove

### Exceptions to Preserve

All other exceptions remain unchanged:
- `ExchangeRateError`
- `CalculationError`
- `ValidationError`
- `DatabaseError`
- `ExportError`
- `ChartError`

## Service Initialization Changes

### App.py Service Initialization
**Current Code**:
```python
if 'screenshot_parser' not in st.session_state:
    st.session_state.screenshot_parser = ScreenshotParserService()
```

**Updated Code**:
```python
# Remove screenshot_parser initialization
# No replacement needed
```

## Integration Points

### Service Dependencies
**Before**:
- ExportService depends on MarketRate data
- ChartGenerator depends on MarketRate data
- App.py initializes ScreenshotParserService

**After**:
- ExportService no longer depends on MarketRate data
- ChartGenerator no longer depends on MarketRate data
- App.py no longer initializes ScreenshotParserService

### Data Flow Changes
**Before**:
```
Screenshot → ScreenshotParserService → MarketRate → ExportService/ChartGenerator
```

**After**:
```
RentalAgreement → CalculationService → PaymentRecord → ExportService/ChartGenerator
```

## Testing Implications

### Contract Tests to Remove
- ScreenshotParserService contract tests
- Market rate related DataStore contract tests

### Contract Tests to Update
- ExportService contract tests (remove market rate parameters)
- ChartGenerator contract tests (remove market rate parameters)

### Contract Tests to Preserve
- All core service contract tests
- Exchange rate service tests
- Calculation service tests
- Inflation service tests

## Migration Strategy

### Phase 1: Update Service Interfaces
1. Remove ScreenshotParserService
2. Update ExportService interface
3. Update ChartGenerator interface
4. Remove market rate methods from DataStore

### Phase 2: Update Service Implementations
1. Implement updated ExportService
2. Implement updated ChartGenerator
3. Remove market rate methods from DataStore implementation

### Phase 3: Update Service Initialization
1. Remove ScreenshotParserService initialization from app.py
2. Update service dependency injection

### Phase 4: Update Tests
1. Remove ScreenshotParserService tests
2. Update ExportService tests
3. Update ChartGenerator tests
4. Update DataStore tests

## Conclusion

The service interface changes for removing market comparison functionality are well-defined and low-risk. The ScreenshotParserService is isolated with no dependencies from other services. The modifications to ExportService and ChartGenerator are minimal and focused on removing market comparison parameters.

**Key Benefits**:
- Simplified service architecture
- Reduced service dependencies
- Cleaner service interfaces
- Easier maintenance

**Risk Mitigation**:
- Comprehensive testing of modified services
- Gradual service removal approach
- Validation of no broken service dependencies
- Clear interface documentation
