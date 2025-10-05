"""
Exchange rate service for fetching and caching USD/TRY rates.
"""
import requests
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from xml.etree import ElementTree as ET

from src.models import ExchangeRate
from src.storage import DataStore
from src.services.exceptions import ExchangeRateAPIError
from src.utils import validate_month, validate_year


class ExchangeRateService:
    """
    Service for fetching USD/TRY exchange rates.
    Primary source: TCMB (Central Bank of Turkey)
    Fallback: exchangerate-api.com or similar free API
    """
    
    # TCMB API endpoint
    TCMB_API_URL = "https://www.tcmb.gov.tr/kurlar/{year}{month:02d}/{day:02d}{month:02d}{year}.xml"
    
    # Backup API (free tier)
    BACKUP_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
    
    def __init__(self, data_store: DataStore):
        """
        Initialize ExchangeRateService.
        
        Args:
            data_store: DataStore instance for caching
        """
        self.data_store = data_store
    
    def fetch_rate(self, month: int, year: int) -> ExchangeRate:
        """
        Fetch exchange rate for specific month/year.
        Uses cache first, then fetches from API if needed.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            ExchangeRate object
            
        Raises:
            ExchangeRateAPIError: If all APIs fail
        """
        validate_month(month)
        validate_year(year)
        
        # Check cache first
        cached_rate = self.data_store.get_exchange_rate(month, year)
        if cached_rate:
            return cached_rate
        
        # Try TCMB API
        try:
            rate = self._fetch_from_tcmb(month, year)
            self.data_store.save_exchange_rate(rate)
            return rate
        except Exception as tcmb_error:
            # TCMB failed, try backup
            try:
                rate = self._fetch_from_backup_api(month, year)
                self.data_store.save_exchange_rate(rate)
                return rate
            except Exception as backup_error:
                raise ExchangeRateAPIError(
                    f"All APIs failed. TCMB: {tcmb_error}, Backup: {backup_error}"
                )
    
    def _fetch_from_tcmb(self, month: int, year: int) -> ExchangeRate:
        """
        Fetch exchange rate from TCMB (Central Bank of Turkey).
        
        TCMB provides daily rates. We'll fetch mid-month rate as approximation
        of monthly average.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            ExchangeRate object
            
        Raises:
            Exception: If TCMB API fails
        """
        # Use mid-month (15th) as representative day
        day = 15
        
        url = self.TCMB_API_URL.format(year=year, month=month, day=day)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Find USD currency
        usd_element = root.find(".//Currency[@CurrencyCode='USD']")
        if usd_element is None:
            raise Exception("USD not found in TCMB response")
        
        # Get ForexBuying rate (TL per 1 USD)
        forex_buying = usd_element.find("ForexBuying")
        if forex_buying is None or not forex_buying.text:
            raise Exception("ForexBuying rate not found")
        
        rate_value = Decimal(forex_buying.text.replace(',', '.'))
        
        return ExchangeRate(
            month=month,
            year=year,
            rate_tl_per_usd=rate_value,
            source="TCMB",
            notes=f"Fetched from TCMB on {datetime.now().date()}"
        )
    
    def _fetch_from_backup_api(self, month: int, year: int) -> ExchangeRate:
        """
        Fetch exchange rate from backup API.
        
        Note: Most free APIs only provide current/recent rates,
        not historical. This is a simplified fallback.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            ExchangeRate object
            
        Raises:
            Exception: If backup API fails
        """
        response = requests.get(self.BACKUP_API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Get TRY rate (this gives USD to TRY)
        if 'rates' not in data or 'TRY' not in data['rates']:
            raise Exception("TRY rate not found in backup API response")
        
        rate_value = Decimal(str(data['rates']['TRY']))
        
        return ExchangeRate(
            month=month,
            year=year,
            rate_tl_per_usd=rate_value,
            source="ExchangeRate-API",
            notes=f"Fetched from backup API on {datetime.now().date()}"
        )
    
    def get_cached_rate(self, month: int, year: int) -> Optional[ExchangeRate]:
        """
        Get cached exchange rate without fetching.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            ExchangeRate if cached, None otherwise
        """
        validate_month(month)
        validate_year(year)
        
        return self.data_store.get_exchange_rate(month, year)
    
    def calculate_monthly_average(self, daily_rates: List[Decimal]) -> Decimal:
        """
        Calculate monthly average from daily rates.
        
        Args:
            daily_rates: List of daily exchange rates
            
        Returns:
            Monthly average rate
            
        Raises:
            ValueError: If daily_rates is empty
        """
        if not daily_rates:
            raise ValueError("daily_rates cannot be empty")
        
        total = sum(daily_rates)
        average = total / len(daily_rates)
        
        return average.quantize(Decimal("0.0001"))
    
    def fetch_rate_range(
        self, 
        start_month: int, 
        start_year: int,
        end_month: int,
        end_year: int
    ) -> List[ExchangeRate]:
        """
        Fetch exchange rates for a date range.
        
        Args:
            start_month: Start month (1-12)
            start_year: Start year
            end_month: End month (1-12)
            end_year: End year
            
        Returns:
            List of ExchangeRate objects
        """
        rates = []
        
        current_month = start_month
        current_year = start_year
        
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            try:
                rate = self.fetch_rate(current_month, current_year)
                rates.append(rate)
            except ExchangeRateAPIError:
                # Skip months where fetch fails
                pass
            
            # Move to next month
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
        
        return rates

