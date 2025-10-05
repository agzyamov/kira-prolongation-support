"""
Regression test for core functionality preservation.
This test verifies that all core rental tracking functionality remains intact after market comparison removal.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_rental_agreement_functionality():
    """Test that rental agreement functionality still works."""
    
    from src.models.rental_agreement import RentalAgreement
    from src.storage.data_store import DataStore
    
    # Create test data
    agreement = RentalAgreement(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        base_amount_tl=Decimal("15000"),
        notes="Test agreement",
        has_conditional_pricing=True
    )
    
    # Test DataStore operations
    data_store = DataStore(":memory:")
    
    # Save agreement
    agreement_id = data_store.save_rental_agreement(agreement)
    assert agreement_id is not None
    
    # Retrieve agreement
    agreements = data_store.get_rental_agreements()
    assert len(agreements) == 1
    assert agreements[0].base_amount_tl == Decimal("15000")

def test_exchange_rate_functionality():
    """Test that exchange rate functionality still works."""
    
    from src.models.exchange_rate import ExchangeRate
    from src.storage.data_store import DataStore
    
    # Create test data
    exchange_rate = ExchangeRate(
        date=date(2023, 1, 1),
        rate=Decimal("30.0"),
        source="TCMB"
    )
    
    # Test DataStore operations
    data_store = DataStore(":memory:")
    
    # Save exchange rate
    rate_id = data_store.save_exchange_rate(exchange_rate)
    assert rate_id is not None
    
    # Retrieve exchange rate
    rates = data_store.get_exchange_rates()
    assert len(rates) == 1
    assert rates[0].rate == Decimal("30.0")

def test_payment_record_functionality():
    """Test that payment record functionality still works."""
    
    from src.models.payment_record import PaymentRecord
    from src.storage.data_store import DataStore
    
    # Create test data
    payment_record = PaymentRecord(
        rental_agreement_id=1,
        payment_date=date(2023, 1, 1),
        amount_tl=Decimal("15000"),
        amount_usd=Decimal("500"),
        exchange_rate=Decimal("30.0")
    )
    
    # Test DataStore operations
    data_store = DataStore(":memory:")
    
    # Save payment record
    record_id = data_store.save_payment_record(payment_record)
    assert record_id is not None
    
    # Retrieve payment records
    records = data_store.get_payment_records()
    assert len(records) == 1
    assert records[0].amount_tl == Decimal("15000")

def test_calculation_service_functionality():
    """Test that calculation service functionality still works."""
    
    from src.services.calculation_service import CalculationService
    from src.services.exchange_rate_service import ExchangeRateService
    from src.models.rental_agreement import RentalAgreement
    from src.storage.data_store import DataStore
    from datetime import date
    from decimal import Decimal
    
    # Create test data
    data_store = DataStore(":memory:")
    exchange_rate_service = ExchangeRateService(data_store)
    calculation_service = CalculationService(exchange_rate_service)
    
    agreement = RentalAgreement(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        base_amount_tl=Decimal("15000"),
        notes="Test agreement"
    )
    
    # Test payment record calculation
    payment_records = calculation_service.calculate_payment_records(agreement)
    assert len(payment_records) > 0
    
    # Test USD equivalent calculation
    usd_amount = calculation_service.calculate_usd_equivalent(Decimal("15000"), date(2023, 1, 1))
    assert usd_amount is not None

def test_export_service_functionality():
    """Test that export service functionality still works."""
    
    from src.services.export_service import ExportService
    from src.models.rental_agreement import RentalAgreement
    from src.models.payment_record import PaymentRecord
    from datetime import date
    from decimal import Decimal
    
    # Create test data
    agreement = RentalAgreement(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        base_amount_tl=Decimal("15000"),
        notes="Test agreement"
    )
    
    payment_record = PaymentRecord(
        rental_agreement_id=1,
        payment_date=date(2023, 1, 1),
        amount_tl=Decimal("15000"),
        amount_usd=Decimal("500"),
        exchange_rate=Decimal("30.0")
    )
    
    export_service = ExportService()
    
    # Test negotiation summary generation
    summary = export_service.generate_negotiation_summary([agreement], [payment_record])
    assert summary is not None
    assert len(summary) > 0

def test_chart_generator_functionality():
    """Test that chart generator functionality still works."""
    
    from src.utils.chart_generator import ChartGenerator
    from src.models.payment_record import PaymentRecord
    from datetime import date
    from decimal import Decimal
    
    # Create test data
    payment_record = PaymentRecord(
        rental_agreement_id=1,
        payment_date=date(2023, 1, 1),
        amount_tl=Decimal("15000"),
        amount_usd=Decimal("500"),
        exchange_rate=Decimal("30.0")
    )
    
    chart_generator = ChartGenerator()
    
    # Test chart generation
    chart = chart_generator.create_tl_usd_chart([payment_record])
    assert chart is not None
    
    # Test payment history chart
    history_chart = chart_generator.create_payment_history_chart([payment_record])
    assert history_chart is not None

def test_database_initialization():
    """Test that database initialization still works without market rates."""
    
    from src.storage.database_init import initialize_database
    
    # This should work without errors
    data_store = initialize_database()
    assert data_store is not None
    
    # Verify that core tables exist
    with data_store._get_connection() as conn:
        cursor = conn.cursor()
        
        # Check core tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='rental_agreements'
        """)
        assert cursor.fetchone() is not None, "rental_agreements table should exist"
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='exchange_rates'
        """)
        assert cursor.fetchone() is not None, "exchange_rates table should exist"
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='payment_records'
        """)
        assert cursor.fetchone() is not None, "payment_records table should exist"

def test_app_imports():
    """Test that app.py can still be imported without errors."""
    
    app_file = Path(__file__).parent.parent.parent / "app.py"
    
    # This should work without import errors
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", app_file)
    app_module = importlib.util.module_from_spec(spec)
    
    # This should not raise any import errors
    spec.loader.exec_module(app_module)
    
    # Verify that core functions exist
    assert hasattr(app_module, 'main'), "main function should exist in app.py"
    assert hasattr(app_module, 'initialize_services'), "initialize_services function should exist in app.py"
