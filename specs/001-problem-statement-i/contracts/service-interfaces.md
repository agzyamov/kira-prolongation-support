# Service Interfaces: Rental Fee Negotiation Support Tool

## Exchange Rate Service

### Interface: ExchangeRateService
**Purpose**: Fetch and manage USD/TL exchange rates from TCMB

#### Methods

##### `fetch_exchange_rate(date: date) -> ExchangeRate`
**Purpose**: Fetch exchange rate for a specific date
**Parameters**:
- `date`: Date object for the requested rate
**Returns**: ExchangeRate object with rate and metadata
**Exceptions**: 
- `ExchangeRateError`: If TCMB API is unavailable
- `InvalidDateError`: If date is invalid or in future

##### `fetch_exchange_rates(start_date: date, end_date: date) -> List[ExchangeRate]`
**Purpose**: Fetch exchange rates for a date range
**Parameters**:
- `start_date`: Start date for range
- `end_date`: End date for range
**Returns**: List of ExchangeRate objects
**Exceptions**:
- `ExchangeRateError`: If TCMB API is unavailable
- `InvalidDateRangeError`: If date range is invalid

##### `get_monthly_average_rate(year: int, month: int) -> Decimal`
**Purpose**: Calculate monthly average exchange rate
**Parameters**:
- `year`: Year for calculation
- `month`: Month for calculation (1-12)
**Returns**: Decimal average rate
**Exceptions**:
- `ExchangeRateError`: If insufficient data for month

## Calculation Service

### Interface: CalculationService
**Purpose**: Calculate rental payments and USD equivalents

#### Methods

##### `calculate_payment_records(agreement: RentalAgreement) -> List[PaymentRecord]`
**Purpose**: Generate payment records for an agreement
**Parameters**:
- `agreement`: RentalAgreement object
**Returns**: List of PaymentRecord objects
**Exceptions**:
- `CalculationError`: If agreement data is invalid
- `ExchangeRateError`: If exchange rates unavailable

##### `apply_conditional_rules(agreement: RentalAgreement, payment_date: date) -> Decimal`
**Purpose**: Apply conditional pricing rules for a specific date
**Parameters**:
- `agreement`: RentalAgreement with conditional rules
- `payment_date`: Date for calculation
**Returns**: Decimal amount in TL
**Exceptions**:
- `CalculationError`: If conditional rules are invalid

##### `calculate_percentage_increase(start_amount: Decimal, end_amount: Decimal) -> Decimal`
**Purpose**: Calculate percentage increase between two amounts
**Parameters**:
- `start_amount`: Initial amount
- `end_amount`: Final amount
**Returns**: Decimal percentage increase
**Exceptions**:
- `CalculationError`: If amounts are invalid

## Screenshot Parser Service

### Interface: ScreenshotParserService
**Purpose**: Parse rental data from sahibinden.com screenshots

#### Methods

##### `parse_screenshot(image_data: bytes, filename: str) -> List[MarketRate]`
**Purpose**: Extract rental amounts from screenshot
**Parameters**:
- `image_data`: Raw image bytes
- `filename`: Original filename
**Returns**: List of MarketRate objects
**Exceptions**:
- `ParsingError`: If image cannot be processed
- `ValidationError`: If parsed data is invalid

##### `validate_parsed_amount(amount: str) -> Decimal`
**Purpose**: Validate and convert parsed amount string
**Parameters**:
- `amount`: Raw amount string from OCR
**Returns**: Decimal validated amount
**Exceptions**:
- `ValidationError`: If amount is invalid

## Inflation Service

### Interface: InflationService
**Purpose**: Fetch and manage Turkish inflation data

#### Methods

##### `fetch_inflation_data(year: int, month: int) -> InflationData`
**Purpose**: Fetch inflation data for specific period
**Parameters**:
- `year`: Year for data
- `month`: Month for data (1-12)
**Returns**: InflationData object
**Exceptions**:
- `InflationDataError`: If TCMB data unavailable

##### `get_legal_maximum_increase(agreement_date: date) -> Decimal`
**Purpose**: Get legal maximum rent increase for agreement date
**Parameters**:
- `agreement_date`: Date of rental agreement
**Returns**: Decimal maximum increase percentage
**Exceptions**:
- `LegalRuleError`: If no rule applies to date

## Export Service

### Interface: ExportService
**Purpose**: Generate and export negotiation materials

#### Methods

##### `export_chart_as_image(chart_data: dict, format: str) -> bytes`
**Purpose**: Export chart as image file
**Parameters**:
- `chart_data`: Chart configuration and data
- `format`: Image format ("png" or "pdf")
**Returns**: Raw image bytes
**Exceptions**:
- `ExportError`: If export fails

##### `generate_negotiation_summary(agreement: RentalAgreement, mode: str) -> str`
**Purpose**: Generate text summary for negotiations
**Parameters**:
- `agreement`: RentalAgreement object
- `mode`: Negotiation mode ("calm" or "assertive")
**Returns**: Formatted summary string
**Exceptions**:
- `ExportError`: If summary generation fails

## Data Store Interface

### Interface: DataStore
**Purpose**: Persist and retrieve application data

#### Methods

##### `save_rental_agreement(agreement: RentalAgreement) -> int`
**Purpose**: Save rental agreement to database
**Parameters**:
- `agreement`: RentalAgreement object
**Returns**: Database ID of saved agreement
**Exceptions**:
- `DatabaseError`: If save operation fails
- `ValidationError`: If agreement data is invalid

##### `get_rental_agreements() -> List[RentalAgreement]`
**Purpose**: Retrieve all rental agreements
**Returns**: List of RentalAgreement objects
**Exceptions**:
- `DatabaseError`: If retrieval fails

##### `save_market_rate(rate: MarketRate) -> int`
**Purpose**: Save market rate data
**Parameters**:
- `rate`: MarketRate object
**Returns**: Database ID of saved rate
**Exceptions**:
- `DatabaseError`: If save operation fails

##### `get_market_rates() -> List[MarketRate]`
**Purpose**: Retrieve all market rates
**Returns**: List of MarketRate objects
**Exceptions**:
- `DatabaseError`: If retrieval fails

## Chart Generator Interface

### Interface: ChartGenerator
**Purpose**: Generate visualizations for rental data

#### Methods

##### `generate_payment_chart(agreements: List[RentalAgreement], mode: str) -> dict`
**Purpose**: Generate payment visualization chart
**Parameters**:
- `agreements`: List of rental agreements
- `mode`: Negotiation mode for styling
**Returns**: Chart configuration dictionary
**Exceptions**:
- `ChartError`: If chart generation fails

##### `add_agreement_markers(chart_config: dict, agreements: List[RentalAgreement]) -> dict`
**Purpose**: Add vertical markers for agreement boundaries
**Parameters**:
- `chart_config`: Base chart configuration
- `agreements`: List of agreements for markers
**Returns**: Updated chart configuration
**Exceptions**:
- `ChartError`: If marker addition fails

## Error Handling

### Base Exception Classes
```python
class RentalNegotiationError(Exception):
    """Base exception for all application errors"""
    pass

class ExchangeRateError(RentalNegotiationError):
    """Exchange rate related errors"""
    pass

class CalculationError(RentalNegotiationError):
    """Calculation related errors"""
    pass

class ParsingError(RentalNegotiationError):
    """Screenshot parsing errors"""
    pass

class ValidationError(RentalNegotiationError):
    """Data validation errors"""
    pass

class DatabaseError(RentalNegotiationError):
    """Database operation errors"""
    pass

class ExportError(RentalNegotiationError):
    """Export operation errors"""
    pass

class ChartError(RentalNegotiationError):
    """Chart generation errors"""
    pass
```

### Error Response Format
All service methods should return structured error information:
```python
{
    "error": "ErrorType",
    "message": "Human readable error message",
    "details": "Technical details for debugging",
    "timestamp": "ISO datetime string"
}
```

## Service Dependencies

### Dependency Graph
```
ExchangeRateService -> TCMB API
CalculationService -> ExchangeRateService, DataStore
ScreenshotParserService -> EasyOCR, ValidationService
InflationService -> TCMB API
ExportService -> ChartGenerator, DataStore
DataStore -> SQLite
ChartGenerator -> Plotly, DataStore
```

### Service Initialization
All services should be initialized with:
- Configuration parameters
- Dependency injection for other services
- Error handling configuration
- Logging configuration

### Service Lifecycle
1. **Initialization**: Services created with dependencies
2. **Configuration**: Services configured with parameters
3. **Operation**: Services perform their functions
4. **Cleanup**: Services clean up resources on shutdown