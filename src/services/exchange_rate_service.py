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
    Source: TCMB (Central Bank of Turkey) - official exchange rates only.
    No backup APIs per Constitution Principle V.
    """
    
    # TCMB API endpoint
    TCMB_API_URL = "https://www.tcmb.gov.tr/kurlar/{year}{month:02d}/{day:02d}{month:02d}{year}.xml"
    
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
        Uses cache first, then fetches from TCMB API if needed.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            ExchangeRate object
            
        Raises:
            ExchangeRateAPIError: If TCMB API fails (use manual entry as alternative)
        """
        validate_month(month)
        validate_year(year)
        
        # Check cache first
        cached_rate = self.data_store.get_exchange_rate(month, year)
        if cached_rate:
            return cached_rate
        
        # Fetch from TCMB API (single source of truth per Constitution Principle V)
        try:
            rate = self._fetch_from_tcmb(month, year)
            self.data_store.save_exchange_rate(rate)
            return rate
        except Exception as tcmb_error:
            raise ExchangeRateAPIError(
                f"TCMB API failed: {tcmb_error}. Please use manual entry instead."
            )
    
    def _fetch_from_tcmb(self, month: int, year: int) -> ExchangeRate:
        """
        Fetch exchange rate from TCMB (Central Bank of Turkey).
        
        TCMB provides daily rates. We'll try multiple days in the month to find
        available data, as TCMB doesn't have data for weekends/holidays.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            ExchangeRate object
            
        Raises:
            Exception: If TCMB API fails for all attempted days
        """
        # Try multiple days in the month to find available data
        # Start with mid-month, then try other days
        days_to_try = [15, 14, 16, 13, 17, 12, 18, 11, 19, 10, 20, 9, 21, 8, 22, 7, 23, 6, 24, 5, 25, 4, 26, 3, 27, 2, 28, 1, 29, 30, 31]
        
        last_error = None
        
        for day in days_to_try:
            try:
                # Skip invalid days for the month
                if month in [4, 6, 9, 11] and day > 30:  # 30-day months
                    continue
                elif month == 2 and day > 28:  # February (ignoring leap years for simplicity)
                    continue
                
                url = self.TCMB_API_URL.format(year=year, month=month, day=day)
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Parse XML response
                root = ET.fromstring(response.content)
                
                # Find USD currency
                usd_element = root.find(".//Currency[@CurrencyCode='USD']")
                if usd_element is None:
                    continue  # Try next day
                
                # Get ForexBuying rate (TL per 1 USD)
                forex_buying = usd_element.find("ForexBuying")
                if forex_buying is None or not forex_buying.text:
                    continue  # Try next day
                
                rate_value = Decimal(forex_buying.text.replace(',', '.'))
                
                return ExchangeRate(
                    month=month,
                    year=year,
                    rate_tl_per_usd=rate_value,
                    source="TCMB",
                    notes=f"Fetched from TCMB on {year}-{month:02d}-{day:02d}"
                )
                
            except Exception as e:
                last_error = e
                continue  # Try next day
        
        # If we get here, all days failed
        raise Exception(f"TCMB API failed for all days in {year}-{month:02d}. Last error: {last_error}")
    
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

