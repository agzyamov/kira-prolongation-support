"""
Test for exchange rate gaps in TCMB data.

Bug: User reports gaps in exchange rate data - missing months like 2023-01, 2023-04, etc.
The TCMB service should fetch all available months, not skip some.

Root cause: TCMB service may have issues with:
1. Date range calculation
2. API response parsing
3. Missing data handling
4. Month iteration logic

Fix: Investigate and fix TCMB service to ensure all available months are fetched.
"""
from decimal import Decimal
from datetime import date, datetime
import tempfile
import os
from unittest.mock import patch, MagicMock

from src.storage import DataStore
from src.services import ExchangeRateService
from src.models import ExchangeRate


def test_tcmb_service_fetches_all_available_months():
    """Test that TCMB service fetches all available months without gaps"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        exchange_service = ExchangeRateService(data_store)
        
        # Mock the TCMB API response to return data for all months in a range
        mock_response_data = {
            'items': [
                {'Tarih': '2023-01', 'TP_DK_USD_S': '18.7'},
                {'Tarih': '2023-02', 'TP_DK_USD_S': '18.8'},
                {'Tarih': '2023-03', 'TP_DK_USD_S': '18.9'},
                {'Tarih': '2023-04', 'TP_DK_USD_S': '19.0'},
                {'Tarih': '2023-05', 'TP_DK_USD_S': '19.1'},
                {'Tarih': '2023-06', 'TP_DK_USD_S': '19.2'},
            ]
        }
        
        with patch('requests.get') as mock_get:
            # Mock successful XML response for TCMB API
            mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
            <Tarih_Date Tarih="2023-01-15">
                <Currency CurrencyCode="USD">
                    <ForexBuying>18.7</ForexBuying>
                </Currency>
            </Tarih_Date>'''
            
            mock_response = MagicMock()
            mock_response.content = mock_xml_response.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Fetch exchange rates for a 6-month period
            exchange_service.fetch_rate_range(1, 2023, 6, 2023)
            
            # Verify all 6 months were saved
            saved_rates = data_store.get_exchange_rates()
            assert len(saved_rates) == 6, f"Expected 6 months, got {len(saved_rates)}"
            
            # Verify no gaps in months
            months = [rate.month for rate in saved_rates]
            expected_months = [1, 2, 3, 4, 5, 6]
            assert sorted(months) == expected_months, f"Missing months: {set(expected_months) - set(months)}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_tcmb_service_handles_missing_months_gracefully():
    """Test that TCMB service handles months with no data gracefully"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        exchange_service = ExchangeRateService(data_store)
        
        # Mock response with some missing months
        mock_response_data = {
            'items': [
                {'Tarih': '2023-01', 'TP_DK_USD_S': '18.7'},
                {'Tarih': '2023-03', 'TP_DK_USD_S': '18.9'},  # Missing 2023-02
                {'Tarih': '2023-05', 'TP_DK_USD_S': '19.1'},  # Missing 2023-04
            ]
        }
        
        with patch('requests.get') as mock_get:
            # Mock XML response for TCMB API
            mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
            <Tarih_Date Tarih="2023-01-15">
                <Currency CurrencyCode="USD">
                    <ForexBuying>18.7</ForexBuying>
                </Currency>
            </Tarih_Date>'''
            
            mock_response = MagicMock()
            mock_response.content = mock_xml_response.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Fetch exchange rates
            exchange_service.fetch_rate_range(1, 2023, 5, 2023)
            
            # Should save only the available months (3 out of 5)
            saved_rates = data_store.get_exchange_rates()
            assert len(saved_rates) == 3, f"Expected 3 available months, got {len(saved_rates)}"
            
            # Verify the correct months were saved
            months = [rate.month for rate in saved_rates]
            expected_months = [1, 3, 5]
            assert sorted(months) == expected_months, f"Expected months {expected_months}, got {sorted(months)}"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_tcmb_service_date_range_calculation():
    """Test that TCMB service calculates date ranges correctly"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        exchange_service = ExchangeRateService(data_store)
        
        # Test date range calculation
        # This should generate 12 months: Jan through Dec 2023
        with patch('requests.get') as mock_get:
            # Mock XML response for TCMB API
            mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
            <Tarih_Date Tarih="2023-01-15">
                <Currency CurrencyCode="USD">
                    <ForexBuying>18.7</ForexBuying>
                </Currency>
            </Tarih_Date>'''
            
            mock_response = MagicMock()
            mock_response.content = mock_xml_response.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            exchange_service.fetch_rate_range(1, 2023, 12, 2023)
            
            # Verify the API was called with correct date range
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            
            # Check that the URL contains the correct date range
            url = call_args[0][0] if call_args[0] else call_args[1]['url']
            assert '2023-01' in url, "Start date should be in URL"
            assert '2023-12' in url, "End date should be in URL"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_exchange_rate_gaps_detection():
    """Test detection of gaps in exchange rate data"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        data_store = DataStore(db_path=db_path)
        
        # Insert exchange rates with gaps (like the user's data)
        rates_with_gaps = [
            ExchangeRate(id=1, month=11, year=2022, rate_tl_per_usd=Decimal('18.5864'), source='TCMB'),
            ExchangeRate(id=2, month=12, year=2022, rate_tl_per_usd=Decimal('18.6254'), source='TCMB'),
            ExchangeRate(id=3, month=2, year=2023, rate_tl_per_usd=Decimal('18.8282'), source='TCMB'),  # Missing Jan 2023
            ExchangeRate(id=4, month=3, year=2023, rate_tl_per_usd=Decimal('18.9583'), source='TCMB'),
            ExchangeRate(id=5, month=5, year=2023, rate_tl_per_usd=Decimal('19.6386'), source='TCMB'),  # Missing Apr 2023
        ]
        
        for rate in rates_with_gaps:
            data_store.save_exchange_rate(rate)
        
        # Get all rates and check for gaps
        all_rates = data_store.get_exchange_rates()
        
        # Group by year and check for gaps
        rates_by_year = {}
        for rate in all_rates:
            if rate.year not in rates_by_year:
                rates_by_year[rate.year] = []
            rates_by_year[rate.year].append(rate.month)
        
        # Check 2023 for gaps
        if 2023 in rates_by_year:
            months_2023 = sorted(rates_by_year[2023])
            expected_months = list(range(1, 13))  # All 12 months
            
            missing_months = set(expected_months) - set(months_2023)
            assert len(missing_months) > 0, "Should detect missing months in 2023"
            assert 1 in missing_months, "January 2023 should be missing"
            assert 4 in missing_months, "April 2023 should be missing"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
