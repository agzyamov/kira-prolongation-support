# Service Interfaces: Rental Fee Negotiation Support Tool

**Date**: 2025-10-05  
**Purpose**: Define service contracts and interfaces  
**Note**: These are Python service interfaces (not REST APIs) for Streamlit app

## Overview

Since this is a Streamlit application, services communicate via direct Python function calls rather than HTTP APIs. These interfaces define the contracts between components.

## Service Interfaces

### 1. ExchangeRateService

**Purpose**: Fetch and manage USD/TL exchange rate data

**Interface**:
```python
from typing import List, Optional
from datetime import date
from decimal import Decimal

class ExchangeRateService:
    """Service for fetching and caching exchange rates"""
    
    def fetch_rate(self, month: int, year: int) -> ExchangeRate:
        """
        Fetch exchange rate for a specific month/year.
        Tries TCMB first, falls back to backup API.
        Caches result in database.
        
        Args:
            month: Month (1-12)
            year: Year (e.g., 2024)
            
        Returns:
            ExchangeRate object
            
        Raises:
            ExchangeRateAPIError: If all APIs fail
            ValidationError: If month/year invalid
        """
        pass
    
    def fetch_rate_range(self, start_date: date, end_date: date) -> List[ExchangeRate]:
        """
        Fetch exchange rates for a date range (monthly averages).
        
        Args:
            start_date: Start of range
            end_date: End of range
            
        Returns:
            List of ExchangeRate objects (one per month)
        """
        pass
    
    def get_cached_rate(self, month: int, year: int) -> Optional[ExchangeRate]:
        """
        Get cached exchange rate from database.
        
        Returns:
            ExchangeRate if found, None if not cached
        """
        pass
    
    def calculate_monthly_average(self, month: int, year: int) -> Decimal:
        """
        Calculate monthly average exchange rate from daily rates.
        
        Returns:
            Decimal: Average TL per USD for the month
        """
        pass
```

**Dependencies**: `requests` (HTTP), `data_store` (SQLite caching)

---

### 2. InflationService

**Purpose**: Manage Turkish inflation data

**Interface**:
```python
class InflationService:
    """Service for managing inflation data"""
    
    def import_from_csv(self, csv_path: str) -> List[InflationData]:
        """
        Import inflation data from TUIK CSV file.
        
        Args:
            csv_path: Path to CSV file (uploaded by user)
            
        Returns:
            List of InflationData objects imported
            
        Raises:
            CSVParseError: If CSV format invalid
        """
        pass
    
    def get_inflation_rate(self, month: int, year: int) -> Optional[InflationData]:
        """
        Get inflation rate for specific month/year.
        
        Returns:
            InflationData if found, None otherwise
        """
        pass
    
    def calculate_legal_max_increase(
        self, 
        current_rent_tl: Decimal, 
        inflation_rate_percent: Decimal
    ) -> Decimal:
        """
        Calculate legal maximum rent increase based on inflation.
        
        Args:
            current_rent_tl: Current rent in TL
            inflation_rate_percent: Inflation rate (e.g., 49.38 for 49.38%)
            
        Returns:
            Maximum allowed rent in TL
        """
        pass
    
    def scrape_tuik_data(self, start_year: int, end_year: int) -> List[InflationData]:
        """
        Optional: Scrape inflation data from TUIK website.
        
        Returns:
            List of InflationData objects
            
        Note: Implementation optional (Phase 2 enhancement)
        """
        pass
```

**Dependencies**: `pandas` (CSV parsing), `data_store`, `beautifulsoup4` (scraping, optional)

---

### 3. ScreenshotParserService

**Purpose**: Extract rental prices from sahibinden.com screenshots using OCR

**Interface**:
```python
from PIL import Image

class ScreenshotParserService:
    """Service for parsing rental listings from screenshots"""
    
    def parse_screenshot(self, image: Image, filename: str) -> List[MarketRate]:
        """
        Extract rental prices from screenshot using OCR.
        
        Args:
            image: PIL Image object
            filename: Original filename for reference
            
        Returns:
            List of MarketRate objects (may be multiple listings in one screenshot)
            
        Raises:
            OCRError: If OCR processing fails
        """
        pass
    
    def preprocess_image(self, image: Image) -> Image:
        """
        Preprocess image for better OCR accuracy.
        - Convert to grayscale
        - Increase contrast
        - Denoise
        
        Returns:
            Preprocessed PIL Image
        """
        pass
    
    def extract_price_from_text(self, text: str) -> Optional[Decimal]:
        """
        Extract rental price from OCR text using regex patterns.
        Handles Turkish number formatting (e.g., "35.000 TL")
        
        Returns:
            Decimal amount or None if not found
        """
        pass
    
    def extract_location(self, text: str) -> Optional[str]:
        """
        Try to extract location/district from OCR text.
        
        Returns:
            Location string or None
        """
        pass
    
    def calculate_confidence(self, image: Image, extracted_text: str) -> float:
        """
        Estimate OCR confidence score.
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        pass
```

**Dependencies**: `pytesseract`, `Pillow`, `re` (regex)

---

### 4. CalculationService

**Purpose**: Calculate payments, USD equivalents, and statistics

**Interface**:
```python
class CalculationService:
    """Service for rental payment calculations and statistics"""
    
    def calculate_payments(
        self, 
        agreement: RentalAgreement,
        exchange_rates: List[ExchangeRate]
    ) -> List[PaymentRecord]:
        """
        Calculate monthly payments for an agreement.
        Handles conditional pricing rules.
        
        Args:
            agreement: RentalAgreement object
            exchange_rates: List of ExchangeRate objects covering the period
            
        Returns:
            List of PaymentRecord objects (one per month)
        """
        pass
    
    def apply_conditional_rules(
        self, 
        rules: Dict, 
        exchange_rate: Decimal
    ) -> Decimal:
        """
        Evaluate conditional pricing rules.
        
        Args:
            rules: Conditional rules JSON from agreement
            exchange_rate: Current USD/TL rate
            
        Returns:
            Amount in TL to charge for this month
        """
        pass
    
    def calculate_percentage_change(
        self, 
        initial_amount: Decimal, 
        final_amount: Decimal
    ) -> Decimal:
        """
        Calculate percentage change between two amounts.
        
        Returns:
            Percentage change (e.g., 66.67 for 66.67% increase)
        """
        pass
    
    def calculate_total_paid(
        self, 
        payments: List[PaymentRecord], 
        currency: str = "TL"
    ) -> Decimal:
        """
        Calculate total amount paid across all payments.
        
        Args:
            payments: List of PaymentRecord objects
            currency: "TL" or "USD"
            
        Returns:
            Total amount in specified currency
        """
        pass
    
    def calculate_average_usd_rate(self, payments: List[PaymentRecord]) -> Decimal:
        """
        Calculate average USD equivalent rent across payments.
        
        Returns:
            Average rent in USD
        """
        pass
    
    def compare_with_market(
        self, 
        current_rent: Decimal, 
        market_rates: List[MarketRate]
    ) -> Dict:
        """
        Compare current rent with market rates.
        
        Returns:
            Dict with statistics:
            - min_market: Minimum market rate
            - max_market: Maximum market rate
            - avg_market: Average market rate
            - percentile: Where current rent falls (0-100)
            - comparison: "below", "within", or "above" market
        """
        pass
```

**Dependencies**: `data_store`, entity classes

---

### 5. ExportService

**Purpose**: Export summaries and visualizations

**Interface**:
```python
class ExportService:
    """Service for exporting reports and visualizations"""
    
    def export_chart_as_png(
        self, 
        figure: go.Figure, 
        filename: str,
        width: int = 800,
        height: int = 600
    ) -> bytes:
        """
        Export Plotly figure as PNG image.
        
        Args:
            figure: Plotly Figure object
            filename: Output filename
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            PNG image as bytes
        """
        pass
    
    def export_summary_pdf(
        self, 
        data: Dict,
        charts: List[go.Figure]
    ) -> bytes:
        """
        Export comprehensive summary as PDF.
        Includes charts, statistics, and negotiation points.
        
        Args:
            data: Summary statistics dictionary
            charts: List of Plotly figures to include
            
        Returns:
            PDF as bytes
        """
        pass
    
    def create_whatsapp_optimized_image(
        self, 
        figures: List[go.Figure]
    ) -> bytes:
        """
        Create single image with multiple charts optimized for WhatsApp.
        - Compressed for smaller file size
        - Readable on mobile devices
        - Max 1600px width for WhatsApp compatibility
        
        Returns:
            PNG image as bytes
        """
        pass
```

**Dependencies**: `plotly`, `kaleido` (image export)

---

### 6. DataStore

**Purpose**: Database persistence layer

**Interface**:
```python
class DataStore:
    """SQLite data persistence layer"""
    
    def save_rental_agreement(self, agreement: RentalAgreement) -> int:
        """
        Save rental agreement to database.
        
        Returns:
            ID of saved agreement
        """
        pass
    
    def get_rental_agreements(self) -> List[RentalAgreement]:
        """Get all rental agreements, ordered by start_date"""
        pass
    
    def save_exchange_rate(self, rate: ExchangeRate) -> None:
        """Save or update exchange rate in cache"""
        pass
    
    def get_exchange_rate(self, month: int, year: int) -> Optional[ExchangeRate]:
        """Get cached exchange rate"""
        pass
    
    def save_payment_record(self, payment: PaymentRecord) -> int:
        """Save payment record"""
        pass
    
    def get_payment_records(
        self, 
        agreement_id: Optional[int] = None
    ) -> List[PaymentRecord]:
        """Get payment records, optionally filtered by agreement"""
        pass
    
    def save_market_rate(self, rate: MarketRate) -> int:
        """Save market rate from screenshot"""
        pass
    
    def get_market_rates(self, verified_only: bool = False) -> List[MarketRate]:
        """Get market rates, optionally only verified ones"""
        pass
    
    def save_inflation_data(self, data: InflationData) -> None:
        """Save inflation data point"""
        pass
    
    def get_inflation_data_range(
        self, 
        start_year: int, 
        end_year: int
    ) -> List[InflationData]:
        """Get inflation data for year range"""
        pass
```

**Dependencies**: `sqlite3`, entity classes

---

## Error Handling

All services should raise specific exceptions:

```python
class ServiceError(Exception):
    """Base exception for service errors"""
    pass

class ExchangeRateAPIError(ServiceError):
    """Raised when exchange rate API fails"""
    pass

class OCRError(ServiceError):
    """Raised when OCR processing fails"""
    pass

class CSVParseError(ServiceError):
    """Raised when CSV parsing fails"""
    pass

class ValidationError(ServiceError):
    """Raised when data validation fails"""
    pass

class DatabaseError(ServiceError):
    """Raised when database operation fails"""
    pass
```

## Service Dependencies

```
Streamlit App (UI)
    ↓
┌───────────────────────────────────────┐
│  CalculationService                   │
│  ExportService                        │
│  ScreenshotParserService              │
│  ExchangeRateService                  │
│  InflationService                     │
└───────────────────────────────────────┘
              ↓
        DataStore (SQLite)
```

## Contract Testing

Each service should have contract tests verifying:

1. **Input Validation**: Raises ValidationError for invalid inputs
2. **Return Types**: Returns correct types as documented
3. **Error Handling**: Raises appropriate exceptions
4. **State Management**: Does not leak state between calls

Example test:
```python
def test_exchange_rate_service_contract():
    service = ExchangeRateService()
    
    # Test valid input
    rate = service.fetch_rate(11, 2022)
    assert isinstance(rate, ExchangeRate)
    assert rate.month == 11
    assert rate.year == 2022
    assert rate.rate_tl_per_usd > 0
    
    # Test invalid input
    with pytest.raises(ValidationError):
        service.fetch_rate(13, 2022)  # Invalid month
    
    # Test API failure handling
    with pytest.raises(ExchangeRateAPIError):
        service.fetch_rate(1, 1900)  # Too old, no data
```

## Implementation Notes

1. **Service Independence**: Services should be loosely coupled
2. **Dependency Injection**: Pass DataStore to service constructors
3. **Caching**: ExchangeRateService caches to minimize API calls
4. **Idempotency**: Repeated calls with same inputs should be safe
5. **Logging**: Use Python logging module for debugging
6. **Type Hints**: All methods use type hints for clarity

## Next Phase

Phase 1 continues with:
- **quickstart.md**: Manual testing guide
- **Agent context file**: Update Cursor with tech stack

