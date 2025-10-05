"""
Contract test for DataStore market rate methods removal.
This test verifies that market rate related methods are removed from DataStore.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_data_store_market_rate_methods_removed():
    """Test that market rate methods are removed from DataStore."""
    
    from src.storage.data_store import DataStore
    
    # Create a DataStore instance
    data_store = DataStore(":memory:")
    
    # These methods should no longer exist after removal
    with pytest.raises(AttributeError):
        data_store.save_market_rate(None)
        pytest.fail("save_market_rate method still exists and should be removed")
    
    with pytest.raises(AttributeError):
        data_store.get_market_rates()
        pytest.fail("get_market_rates method still exists and should be removed")
    
    with pytest.raises(AttributeError):
        data_store.delete_market_rate(1)
        pytest.fail("delete_market_rate method still exists and should be removed")
    
    with pytest.raises(AttributeError):
        data_store.get_market_rates_by_location("test")
        pytest.fail("get_market_rates_by_location method still exists and should be removed")

def test_data_store_initialization_without_market_rates():
    """Test that DataStore can be initialized without market rate functionality."""
    
    from src.storage.data_store import DataStore
    
    # This should work without errors
    data_store = DataStore(":memory:")
    
    # Verify that core methods still exist
    assert hasattr(data_store, 'save_rental_agreement')
    assert hasattr(data_store, 'get_rental_agreements')
    assert hasattr(data_store, 'save_exchange_rate')
    assert hasattr(data_store, 'get_exchange_rates')
    assert hasattr(data_store, 'save_payment_record')
    assert hasattr(data_store, 'get_payment_records')

def test_database_schema_without_market_rates():
    """Test that database schema no longer includes market_rates table."""
    
    from src.storage.data_store import DataStore
    
    data_store = DataStore(":memory:")
    
    # Get database connection to check schema
    with data_store._get_connection() as conn:
        cursor = conn.cursor()
        
        # Check that market_rates table does not exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='market_rates'
        """)
        
        result = cursor.fetchone()
        assert result is None, "market_rates table still exists and should be removed"
        
        # Verify that core tables still exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='rental_agreements'
        """)
        assert cursor.fetchone() is not None, "rental_agreements table should still exist"
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='exchange_rates'
        """)
        assert cursor.fetchone() is not None, "exchange_rates table should still exist"
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='payment_records'
        """)
        assert cursor.fetchone() is not None, "payment_records table should still exist"
