"""
Test for Decimal to SQLite conversion bug.

Bug: User reported "Save Rate" fails with error:
"type 'decimal.Decimal' is not supported" when saving market rates.

Root cause: SQLite doesn't support Decimal types natively.
The confidence field (Decimal) needs to be converted to float or string.

Fix: Convert Decimal to float when saving to SQLite.
"""
from decimal import Decimal
from datetime import date
import tempfile
import os

from src.storage import DataStore
from src.models import MarketRate


def test_market_rate_with_decimal_confidence_saves_successfully():
    """Test that market rates with Decimal confidence can be saved to SQLite"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # Initialize DataStore with temp database
        data_store = DataStore(db_path=db_path)
        
        # Create a MarketRate with Decimal confidence
        rate = MarketRate(
            amount_tl=Decimal("30000"),
            location="Konyaaltı",
            screenshot_filename="test.png",
            date_captured=date.today(),
            confidence=Decimal("0.85"),  # This is a Decimal
            raw_ocr_text="30 bin TL Konyaaltı"
        )
        
        # This should NOT raise an error
        rate_id = data_store.save_market_rate(rate)
        
        # Verify it was saved
        assert rate_id > 0, "Market rate should be saved with valid ID"
        
        # Verify we can retrieve it
        retrieved_rates = data_store.get_market_rates()
        assert len(retrieved_rates) == 1, "Should retrieve saved market rate"
        
        retrieved_rate = retrieved_rates[0]
        assert retrieved_rate.amount_tl == rate.amount_tl
        assert retrieved_rate.location == rate.location
        assert retrieved_rate.confidence is not None
        # Confidence should be close to original (allowing for float conversion)
        assert abs(float(retrieved_rate.confidence) - float(rate.confidence)) < 0.01
        
    finally:
        # Clean up temp database
        if os.path.exists(db_path):
            os.remove(db_path)


def test_market_rate_with_none_confidence_saves_successfully():
    """Test that market rates with None confidence can be saved"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create a MarketRate with None confidence
        rate = MarketRate(
            amount_tl=Decimal("35000"),
            location="Muratpaşa",
            screenshot_filename="test2.png",
            date_captured=date.today(),
            confidence=None,  # No confidence
            raw_ocr_text="35 bin TL"
        )
        
        # This should work fine
        rate_id = data_store.save_market_rate(rate)
        assert rate_id > 0
        
        # Verify we can retrieve it
        retrieved_rates = data_store.get_market_rates()
        assert len(retrieved_rates) == 1
        assert retrieved_rates[0].confidence is None
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_all_decimal_fields_converted_for_sqlite():
    """Test that all Decimal fields in MarketRate are properly converted"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Create rate with all Decimal fields
        rate = MarketRate(
            amount_tl=Decimal("50000.50"),
            location="Test",
            screenshot_filename="test.png",
            date_captured=date.today(),
            confidence=Decimal("0.95"),
            raw_ocr_text="test"
        )
        
        # Save and retrieve
        data_store.save_market_rate(rate)
        retrieved = data_store.get_market_rates()[0]
        
        # All numeric values should be retrievable
        assert retrieved.amount_tl is not None
        assert retrieved.confidence is not None
        
        # Values should match (within float precision)
        assert abs(float(retrieved.amount_tl) - float(rate.amount_tl)) < 0.01
        assert abs(float(retrieved.confidence) - float(rate.confidence)) < 0.01
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

