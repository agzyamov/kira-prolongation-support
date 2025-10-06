"""
Pytest configuration for TÜFE feature testing.
Provides test database setup and fixtures for easy TÜFE data fetching tests.
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from src.storage.data_store import DataStore


@pytest.fixture
def test_db_path():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def test_data_store(test_db_path):
    """Create a DataStore instance with test database."""
    data_store = DataStore(test_db_path)
    
    # Run migrations to set up test database
    from scripts.migrate_add_tufe_tables import migrate_add_tufe_tables
    from scripts.migrate_enhance_tufe_tables import run_migration
    
    # Temporarily change to test database
    original_db = "rental_negotiation.db"
    if os.path.exists(original_db):
        os.rename(original_db, f"{original_db}.backup")
    
    try:
        # Create test database with same name as expected
        test_db = Path(test_db_path)
        test_db.rename("rental_negotiation.db")
        
        # Run migrations
        migrate_add_tufe_tables()
        run_migration()
        
        # Rename back to test path
        Path("rental_negotiation.db").rename(test_db_path)
        
    finally:
        # Restore original database if it existed
        if os.path.exists(f"{original_db}.backup"):
            os.rename(f"{original_db}.backup", original_db)
    
    return data_store


@pytest.fixture
def sample_tufe_data_source():
    """Sample TÜFE data source for testing."""
    return {
        'source_name': 'TCMB EVDS API',
        'api_endpoint': 'https://evds2.tcmb.gov.tr/service/evds/',
        'series_code': 'TP.FE.OKTG01',
        'data_format': 'json',
        'requires_auth': True,
        'rate_limit_per_hour': 100,
        'is_active': True,
        'priority': 1,
        'reliability_score': 0.95,
        'health_status': 'healthy',
        'failure_count': 0,
        'success_count': 10,
        'avg_response_time': 500.0,
        'rate_limit_remaining': 1000
    }


@pytest.fixture
def sample_tufe_api_key():
    """Sample TÜFE API key for testing."""
    return {
        'key_name': 'Test TCMB Key',
        'api_key': 'test_api_key_12345',
        'source_id': 1,
        'is_active': True,
        'source_priority': 1,
        'auto_configured': False,
        'usage_count': 0,
        'is_valid': True
    }


@pytest.fixture
def sample_tufe_fetch_session():
    """Sample TÜFE fetch session for testing."""
    return {
        'session_id': 'test_session_123',
        'requested_year': 2023,
        'status': 'pending',
        'source_attempts': '[]',
        'retry_count': 0,
        'user_id': 'test_user'
    }


@pytest.fixture
def sample_tufe_source_manager():
    """Sample TÜFE source manager for testing."""
    return {
        'name': 'test_manager',
        'active_sources': '[1, 2, 3]',
        'health_check_interval': 300,
        'failure_threshold': 3,
        'success_threshold': 2,
        'max_retry_attempts': 3,
        'retry_delay': 5
    }


@pytest.fixture
def sample_tufe_auto_config():
    """Sample TÜFE auto config for testing."""
    return {
        'config_name': 'test_config',
        'auto_discovery_enabled': True,
        'default_priority_order': '[1, 2, 3]',
        'fallback_to_manual': True,
        'cache_duration_hours': 24,
        'validation_enabled': True
    }


@pytest.fixture
def sample_tufe_data_cache():
    """Sample TÜFE data cache for testing."""
    return {
        'year': 2023,
        'tufe_rate': 64.27,
        'source_name': 'TCMB EVDS API',
        'fetched_at': '2023-12-01 10:00:00',
        'expires_at': '2023-12-02 10:00:00',
        'is_validated': True,
        'source_attempts': '[1, 2]',
        'fetch_duration': 1200.0,
        'validation_status': 'valid',
        'data_quality_score': 0.95
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set test environment variables
    os.environ['TUFU_DEBUG_MODE'] = 'true'
    os.environ['TUFU_LOG_LEVEL'] = 'DEBUG'
    os.environ['TUFU_CACHE_DURATION_HOURS'] = '1'  # Short cache for tests
    os.environ['TUFU_RATE_LIMIT_DELAY_SECONDS'] = '0.1'  # Fast rate limit for tests
    
    yield
    
    # Cleanup environment variables
    test_vars = ['TUFU_DEBUG_MODE', 'TUFU_LOG_LEVEL', 'TUFU_CACHE_DURATION_HOURS', 'TUFU_RATE_LIMIT_DELAY_SECONDS']
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]


# Performance test fixtures
@pytest.fixture
def performance_test_config():
    """Configuration for performance tests."""
    return {
        'max_fetch_time_seconds': 2.0,
        'max_cache_lookup_ms': 100,
        'max_source_selection_ms': 50,
        'max_health_check_ms': 500
    }


# Mock fixtures for external dependencies
@pytest.fixture
def mock_requests():
    """Mock requests library for testing API calls."""
    import requests
    from unittest.mock import Mock, patch
    
    with patch('requests.get') as mock_get, patch('requests.head') as mock_head:
        # Configure default successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'TARIH': '2023-12-01',
                    'TP_FE_OKTG01': 64.27
                }
            ]
        }
        mock_response.text = '{"items":[{"TARIH":"2023-12-01","TP_FE_OKTG01":64.27}]}'
        
        mock_get.return_value = mock_response
        mock_head.return_value = mock_response
        
        yield {
            'get': mock_get,
            'head': mock_head,
            'response': mock_response
        }


@pytest.fixture
def mock_time():
    """Mock time functions for testing."""
    from unittest.mock import patch
    import time
    
    with patch('time.time') as mock_time_func, patch('time.sleep') as mock_sleep:
        mock_time_func.return_value = 1701432000.0  # Fixed timestamp
        yield {
            'time': mock_time_func,
            'sleep': mock_sleep
        }
