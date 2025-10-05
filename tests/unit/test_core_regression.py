"""
Unit tests for core functionality regression after market comparison removal.
These tests ensure that all core rental tracking functionality remains intact.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_rental_agreement_model():
    """Test that RentalAgreement model still works correctly."""
    from src.models.rental_agreement import RentalAgreement
    
    agreement = RentalAgreement(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        base_amount_tl=Decimal("15000"),
        notes="Test agreement"
    )
    
    assert agreement.start_date == date(2023, 1, 1)
    assert agreement.base_amount_tl == Decimal("15000")
    assert agreement.notes == "Test agreement"

def test_exchange_rate_model():
    """Test that ExchangeRate model still works correctly."""
    from src.models.exchange_rate import ExchangeRate
    
    rate = ExchangeRate(
        date=date(2023, 1, 1),
        rate=Decimal("30.0"),
        source="TCMB"
    )
    
    assert rate.date == date(2023, 1, 1)
    assert rate.rate == Decimal("30.0")
    assert rate.source == "TCMB"

def test_payment_record_model():
    """Test that PaymentRecord model still works correctly."""
    from src.models.payment_record import PaymentRecord
    
    payment = PaymentRecord(
        rental_agreement_id=1,
        payment_date=date(2023, 1, 1),
        amount_tl=Decimal("15000"),
        amount_usd=Decimal("500"),
        exchange_rate=Decimal("30.0")
    )
    
    assert payment.rental_agreement_id == 1
    assert payment.amount_tl == Decimal("15000")
    assert payment.amount_usd == Decimal("500")

def test_data_store_core_operations():
    """Test that DataStore core operations still work."""
    from src.storage.data_store import DataStore
    from src.models.rental_agreement import RentalAgreement
    from src.models.exchange_rate import ExchangeRate
    from src.models.payment_record import PaymentRecord
    
    data_store = DataStore(":memory:")
    
    # Test rental agreement operations
    agreement = RentalAgreement(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        base_amount_tl=Decimal("15000"),
        notes="Test agreement"
    )
    
    agreement_id = data_store.save_rental_agreement(agreement)
    assert agreement_id is not None
    
    agreements = data_store.get_rental_agreements()
    assert len(agreements) == 1
    assert agreements[0].base_amount_tl == Decimal("15000")
    
    # Test exchange rate operations
    rate = ExchangeRate(
        date=date(2023, 1, 1),
        rate=Decimal("30.0"),
        source="TCMB"
    )
    
    rate_id = data_store.save_exchange_rate(rate)
    assert rate_id is not None
    
    rates = data_store.get_exchange_rates()
    assert len(rates) == 1
    assert rates[0].rate == Decimal("30.0")
    
    # Test payment record operations
    payment = PaymentRecord(
        rental_agreement_id=agreement_id,
        payment_date=date(2023, 1, 1),
        amount_tl=Decimal("15000"),
        amount_usd=Decimal("500"),
        exchange_rate=Decimal("30.0")
    )
    
    payment_id = data_store.save_payment_record(payment)
    assert payment_id is not None
    
    payments = data_store.get_payment_records()
    assert len(payments) == 1
    assert payments[0].amount_tl == Decimal("15000")

def test_calculation_service_core_methods():
    """Test that CalculationService core methods still work."""
    from src.services.calculation_service import CalculationService
    from src.services.exchange_rate_service import ExchangeRateService
    from src.storage.data_store import DataStore
    from src.models.rental_agreement import RentalAgreement
    from src.models.payment_record import PaymentRecord
    
    data_store = DataStore(":memory:")
    exchange_rate_service = ExchangeRateService(data_store)
    calculation_service = CalculationService(exchange_rate_service)
    
    # Test percentage calculation
    increase = calculation_service.calculate_percentage_increase(
        Decimal("100"), Decimal("120")
    )
    assert increase == 20.0
    
    # Test payment record calculation
    agreement = RentalAgreement(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        base_amount_tl=Decimal("15000"),
        notes="Test agreement"
    )
    
    payment_records = calculation_service.calculate_payment_records(agreement)
    assert len(payment_records) > 0
    
    # Test payment summary
    payments = [
        PaymentRecord(
            rental_agreement_id=1,
            payment_date=date(2023, 1, 1),
            amount_tl=Decimal("15000"),
            amount_usd=Decimal("500"),
            exchange_rate=Decimal("30.0")
        )
    ]
    
    summary = calculation_service.calculate_payment_summary(payments)
    assert "total_payments" in summary
    assert "avg_tl" in summary
    assert "avg_usd" in summary

def test_chart_generator_core_methods():
    """Test that ChartGenerator core methods still work."""
    from src.utils.chart_generator import ChartGenerator
    from src.models.payment_record import PaymentRecord
    
    chart_generator = ChartGenerator()
    
    # Test TL vs USD chart
    payments = [
        PaymentRecord(
            rental_agreement_id=1,
            payment_date=date(2023, 1, 1),
            amount_tl=Decimal("15000"),
            amount_usd=Decimal("500"),
            exchange_rate=Decimal("30.0")
        )
    ]
    
    chart = chart_generator.create_tl_vs_usd_chart(payments)
    assert chart is not None
    
    # Test payment history chart
    history_chart = chart_generator.create_payment_history_chart(payments)
    assert history_chart is not None

def test_export_service_core_methods():
    """Test that ExportService core methods still work."""
    from src.services.export_service import ExportService
    from src.models.rental_agreement import RentalAgreement
    from src.models.payment_record import PaymentRecord
    
    export_service = ExportService()
    
    # Test negotiation summary generation
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
    
    summary = export_service.generate_negotiation_summary(agreements, payments)
    assert summary is not None
    assert len(summary) > 0

def test_database_schema_core_tables():
    """Test that core database tables still exist."""
    from src.storage.data_store import DataStore
    
    data_store = DataStore(":memory:")
    
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
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='inflation_data'
        """)
        assert cursor.fetchone() is not None, "inflation_data table should exist"
        
        # Verify market_rates table does not exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='market_rates'
        """)
        assert cursor.fetchone() is None, "market_rates table should not exist"
