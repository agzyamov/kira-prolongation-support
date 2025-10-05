"""
Tests for exchange rate service functionality.
These tests should FAIL initially (TDD approach).
Includes mocking of HTTP requests to TCMB and backup APIs.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, patch, MagicMock


class TestExchangeRateFetching:
    """Test fetching exchange rates from APIs"""
    
    @patch('requests.get')
    def test_fetch_rate_from_tcmb_success(self, mock_get):
        """Test successful fetch from TCMB API"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''<?xml version="1.0"?>
        <Tarih_Date Tarih="01.11.2022">
            <Currency CurrencyCode="USD">
                <ForexBuying>18.6234</ForexBuying>
                <ForexSelling>18.6789</ForexSelling>
            </Currency>
        </Tarih_Date>'''
        mock_get.return_value = mock_response
        
        # Act
        from src.services.exchange_rate_service import ExchangeRateService
        service = ExchangeRateService()
        rate = service.fetch_rate(11, 2022)
        
        # Assert
        assert rate.month == 11
        assert rate.year == 2022
        assert rate.rate_tl_per_usd > Decimal("0")
        assert rate.source == "TCMB"
    
    @patch('requests.get')
    def test_fetch_rate_tcmb_fails_uses_backup(self, mock_get):
        """Test fallback to backup API when TCMB fails"""
        # Arrange - TCMB fails, backup succeeds
        tcmb_response = Mock()
        tcmb_response.status_code = 500
        
        backup_response = Mock()
        backup_response.status_code = 200
        backup_response.json.return_value = {
            "rates": {"TRY": 18.65}
        }
        
        mock_get.side_effect = [tcmb_response, backup_response]
        
        # Act
        from src.services.exchange_rate_service import ExchangeRateService
        service = ExchangeRateService()
        rate = service.fetch_rate(11, 2022)
        
        # Assert
        assert rate.source != "TCMB"  # Should be backup API
        assert rate.rate_tl_per_usd > Decimal("0")
    
    @patch('requests.get')
    def test_fetch_rate_both_apis_fail_raises_error(self, mock_get):
        """Test that error is raised when all APIs fail"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        # Act & Assert
        from src.services.exchange_rate_service import ExchangeRateService
        from src.services.exchange_rate_service import ExchangeRateAPIError
        
        service = ExchangeRateService()
        with pytest.raises(ExchangeRateAPIError):
            service.fetch_rate(11, 2022)
    
    def test_fetch_rate_invalid_month_raises_error(self):
        """Test that invalid month raises ValidationError"""
        from src.services.exchange_rate_service import ExchangeRateService
        
        service = ExchangeRateService()
        with pytest.raises(ValueError):
            service.fetch_rate(13, 2022)  # Month 13 invalid
    
    def test_fetch_rate_invalid_year_raises_error(self):
        """Test that invalid year raises ValidationError"""
        from src.services.exchange_rate_service import ExchangeRateService
        
        service = ExchangeRateService()
        with pytest.raises(ValueError):
            service.fetch_rate(1, 1900)  # Too old


class TestExchangeRateCaching:
    """Test caching behavior of exchange rate service"""
    
    def test_get_cached_rate_returns_none_if_not_cached(self):
        """Test getting non-existent cached rate"""
        from src.services.exchange_rate_service import ExchangeRateService
        
        service = ExchangeRateService()
        result = service.get_cached_rate(11, 2022)
        
        assert result is None
    
    @patch('requests.get')
    def test_fetch_rate_caches_result(self, mock_get):
        """Test that fetched rate is cached in database"""
        pytest.skip("Requires DataStore implementation")
    
    def test_cached_rate_used_on_second_fetch(self):
        """Test that cached rate is returned without API call"""
        pytest.skip("Requires DataStore implementation")


class TestExchangeRateRange:
    """Test fetching exchange rates for date ranges"""
    
    def test_fetch_rate_range_returns_monthly_rates(self):
        """Test fetching rates for date range"""
        pytest.skip("Requires complete implementation")
    
    def test_fetch_rate_range_handles_missing_months(self):
        """Test handling when some months are missing"""
        pytest.skip("Requires complete implementation")


class TestMonthlyAverageCalculation:
    """Test calculation of monthly average exchange rates"""
    
    def test_calculate_monthly_average_from_daily_rates(self):
        """Test averaging daily rates to monthly"""
        # Arrange
        daily_rates = [
            Decimal("18.50"),
            Decimal("18.60"),
            Decimal("18.70"),
            Decimal("18.65")
        ]
        expected_avg = Decimal("18.61")  # Average
        
        # Act
        from src.services.exchange_rate_service import ExchangeRateService
        service = ExchangeRateService()
        result = service.calculate_monthly_average(daily_rates)
        
        # Assert
        assert abs(result - expected_avg) < Decimal("0.01")
    
    def test_calculate_monthly_average_empty_list_raises_error(self):
        """Test that empty rate list raises error"""
        from src.services.exchange_rate_service import ExchangeRateService
        
        service = ExchangeRateService()
        with pytest.raises(ValueError):
            service.calculate_monthly_average([])

