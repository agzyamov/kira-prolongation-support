"""
Integration test for export service market data removal.
This test verifies that export service no longer accepts market rate parameters.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_export_service_without_market_rates():
    """Test that ExportService no longer accepts market rate parameters."""
    
    from src.services.export_service import ExportService
    from src.models.rental_agreement import RentalAgreement
    from src.models.payment_record import PaymentRecord
    
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
    
    # This should work without market rates parameter
    summary = export_service.generate_negotiation_summary([agreement], [payment_record])
    
    assert summary is not None
    assert len(summary) > 0
    
    # Verify that summary doesn't contain market comparison references
    assert "market" not in summary.lower()
    assert "comparison" not in summary.lower()
    assert "screenshot" not in summary.lower()

def test_export_service_method_signature():
    """Test that ExportService.generate_negotiation_summary has correct signature without market rates."""
    
    from src.services.export_service import ExportService
    import inspect
    
    export_service = ExportService()
    
    # Get the method signature
    method = getattr(export_service, 'generate_negotiation_summary')
    signature = inspect.signature(method)
    
    # Check that the method only takes agreements and payment_records parameters
    params = list(signature.parameters.keys())
    
    # Should only have agreements and payment_records parameters
    assert len(params) == 2, f"Expected 2 parameters, got {len(params)}: {params}"
    assert "agreements" in params
    assert "payment_records" in params
    
    # Should not have market_rates parameter
    assert "market_rates" not in params, "market_rates parameter still exists in generate_negotiation_summary"

def test_chart_generator_without_market_rates():
    """Test that ChartGenerator no longer accepts market rate parameters."""
    
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
    
    # This should work without market rates parameter
    chart = chart_generator.create_tl_usd_chart([payment_record])
    
    assert chart is not None

def test_chart_generator_method_signature():
    """Test that ChartGenerator.create_tl_usd_chart has correct signature without market rates."""
    
    from src.utils.chart_generator import ChartGenerator
    import inspect
    
    chart_generator = ChartGenerator()
    
    # Get the method signature
    method = getattr(chart_generator, 'create_tl_usd_chart')
    signature = inspect.signature(method)
    
    # Check that the method only takes payment_records parameter
    params = list(signature.parameters.keys())
    
    # Should only have payment_records parameter
    assert len(params) == 1, f"Expected 1 parameter, got {len(params)}: {params}"
    assert "payment_records" in params
    
    # Should not have market_rates parameter
    assert "market_rates" not in params, "market_rates parameter still exists in create_tl_usd_chart"

def test_export_service_imports():
    """Test that ExportService no longer imports market rate related components."""
    
    export_service_file = Path(__file__).parent.parent.parent / "src" / "services" / "export_service.py"
    
    with open(export_service_file, 'r') as f:
        content = f.read()
    
    # These imports should not be present after removal
    assert "from src.models.market_rate import MarketRate" not in content, "MarketRate import still exists in ExportService"
    assert "MarketRate" not in content, "MarketRate still referenced in ExportService"

def test_chart_generator_imports():
    """Test that ChartGenerator no longer imports market rate related components."""
    
    chart_generator_file = Path(__file__).parent.parent.parent / "src" / "utils" / "chart_generator.py"
    
    with open(chart_generator_file, 'r') as f:
        content = f.read()
    
    # These imports should not be present after removal
    assert "from src.models.market_rate import MarketRate" not in content, "MarketRate import still exists in ChartGenerator"
    assert "MarketRate" not in content, "MarketRate still referenced in ChartGenerator"
