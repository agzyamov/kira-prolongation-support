"""
Unit tests for graceful handling of missing market data.
These tests ensure the application handles the absence of market data gracefully.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_data_store_handles_missing_market_rates_gracefully():
    """Test that DataStore handles missing market rates gracefully."""
    from src.storage.data_store import DataStore
    
    data_store = DataStore(":memory:")
    
    # These methods should not exist, but if they do, they should handle gracefully
    if hasattr(data_store, 'get_market_rates'):
        # If method exists, it should return empty list
        market_rates = data_store.get_market_rates()
        assert market_rates == []
    else:
        # Method should not exist
        assert not hasattr(data_store, 'get_market_rates')

def test_calculation_service_handles_missing_market_comparison():
    """Test that CalculationService handles missing market comparison gracefully."""
    from src.services.calculation_service import CalculationService
    from src.services.exchange_rate_service import ExchangeRateService
    from src.storage.data_store import DataStore
    
    data_store = DataStore(":memory:")
    exchange_rate_service = ExchangeRateService(data_store)
    calculation_service = CalculationService(exchange_rate_service)
    
    # Market comparison method should not exist
    assert not hasattr(calculation_service, 'calculate_market_comparison')

def test_chart_generator_handles_missing_market_chart():
    """Test that ChartGenerator handles missing market comparison chart gracefully."""
    from src.utils.chart_generator import ChartGenerator
    
    chart_generator = ChartGenerator()
    
    # Market comparison chart method should not exist
    assert not hasattr(chart_generator, 'create_market_comparison_chart')

def test_export_service_handles_missing_market_data():
    """Test that ExportService handles missing market data gracefully."""
    from src.services.export_service import ExportService
    from src.models.rental_agreement import RentalAgreement
    from src.models.payment_record import PaymentRecord
    
    export_service = ExportService()
    
    # Create test data without market rates
    agreements = [
        RentalAgreement(
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            base_amount_tl=Decimal("15000"),
            notes="Test agreement"
        )
    ]
    
    payments = [
        PaymentRecord(
            rental_agreement_id=1,
            payment_date=date(2023, 1, 1),
            amount_tl=Decimal("15000"),
            amount_usd=Decimal("500"),
            exchange_rate=Decimal("30.0")
        )
    ]
    
    # Should work without market data
    summary = export_service.generate_negotiation_summary(agreements, payments)
    assert summary is not None
    assert len(summary) > 0
    
    # Summary should not contain market references
    assert "market" not in summary.lower()
    assert "comparison" not in summary.lower()

def test_app_handles_missing_screenshot_parser():
    """Test that app.py handles missing ScreenshotParserService gracefully."""
    app_file = Path(__file__).parent.parent.parent / "app.py"
    
    with open(app_file, 'r') as f:
        app_content = f.read()
    
    # Should not import ScreenshotParserService
    assert "from src.services.screenshot_parser import ScreenshotParserService" not in app_content
    
    # Should not initialize screenshot_parser in services
    assert "screenshot_parser" not in app_content
    
    # Should not reference ScreenshotParserService
    assert "ScreenshotParserService" not in app_content

def test_database_handles_missing_market_rates_table():
    """Test that database handles missing market_rates table gracefully."""
    from src.storage.data_store import DataStore
    
    data_store = DataStore(":memory:")
    
    with data_store._get_connection() as conn:
        cursor = conn.cursor()
        
        # Check that market_rates table does not exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='market_rates'
        """)
        
        result = cursor.fetchone()
        assert result is None, "market_rates table should not exist"
        
        # Core tables should still exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='rental_agreements'
        """)
        assert cursor.fetchone() is not None, "rental_agreements table should exist"

def test_models_handle_missing_market_rate():
    """Test that models handle missing MarketRate gracefully."""
    from src.models import RentalAgreement, ExchangeRate, PaymentRecord, InflationData
    
    # These should still work
    agreement = RentalAgreement(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        base_amount_tl=Decimal("15000"),
        notes="Test agreement"
    )
    
    rate = ExchangeRate(
        date=date(2023, 1, 1),
        rate=Decimal("30.0"),
        source="TCMB"
    )
    
    payment = PaymentRecord(
        rental_agreement_id=1,
        payment_date=date(2023, 1, 1),
        amount_tl=Decimal("15000"),
        amount_usd=Decimal("500"),
        exchange_rate=Decimal("30.0")
    )
    
    inflation = InflationData(
        month=1,
        year=2023,
        inflation_rate_percent=Decimal("50.0"),
        source="TCMB"
    )
    
    # All should be created successfully
    assert agreement is not None
    assert rate is not None
    assert payment is not None
    assert inflation is not None

def test_imports_handle_missing_market_rate():
    """Test that imports handle missing MarketRate gracefully."""
    from src.models import RentalAgreement, ExchangeRate, PaymentRecord, InflationData
    
    # Should be able to import core models
    assert RentalAgreement is not None
    assert ExchangeRate is not None
    assert PaymentRecord is not None
    assert InflationData is not None
    
    # Should not be able to import MarketRate
    with pytest.raises(ImportError):
        from src.models.market_rate import MarketRate
