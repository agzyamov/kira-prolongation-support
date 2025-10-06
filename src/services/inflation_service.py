"""
Inflation data service for Turkish inflation rates.
Supports CSV import, legal maximum rent increase calculations, and secure TÜFE data management.

Features:
- CSV import and export of inflation data
- Legal maximum rent increase calculations (25% cap until June 2024, TÜFE after July 2024)
- Secure TÜFE data fetching from TCMB EVDS API
- TÜFE data caching with 24-hour expiration
- Data source attribution and tracking
- Manual TÜFE data entry and validation
- Integration with TCMB API for official data

TÜFE Data Management:
- fetch_tufe_from_tcmb_api(): Fetch TÜFE data from TCMB EVDS API
- cache_tufe_data(): Cache TÜFE data with source attribution
- get_cached_tufe_data(): Retrieve cached TÜFE data
- is_tufe_cache_valid(): Check cache validity
- get_tufe_data_sources(): Get available TÜFE data sources
- get_active_tufe_source(): Get currently active TÜFE source

Security:
- API keys are managed securely through TufeConfigService
- All API calls use HTTPS
- Data validation before storage
- Source attribution for data lineage
"""
import pandas as pd
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
import io

from src.models import InflationData
from src.storage import DataStore
from src.services.exceptions import CSVParseError, TufeApiError, TufeValidationError
from src.services.oecd_api_client import OECDApiClient
from src.services.rate_limit_handler import RateLimitHandler
from src.services.data_validator import DataValidator
from src.utils import validate_month, validate_year


class InflationService:
    """
    Service for managing Turkish inflation data.
    Calculates legal maximum rent increases based on official rates.
    """
    
    def __init__(self, data_store: DataStore):
        """
        Initialize InflationService.
        
        Args:
            data_store: DataStore instance for persistence
        """
        self.data_store = data_store
        
        # Initialize OECD API components
        self.oecd_client = OECDApiClient()
        self.rate_limit_handler = RateLimitHandler()
        self.data_validator = DataValidator()
    
    def import_from_csv(self, csv_content: str) -> int:
        """
        Import inflation data from CSV content.
        
        Expected CSV format:
        month,year,inflation_rate_percent,source
        11,2022,85.51,TUIK
        11,2023,61.98,TUIK
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            Number of records imported
            
        Raises:
            CSVParseError: If CSV parsing fails
        """
        try:
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validate required columns
            required_columns = ['month', 'year', 'inflation_rate_percent']
            if not all(col in df.columns for col in required_columns):
                raise CSVParseError(
                    f"CSV must contain columns: {required_columns}"
                )
            
            # Import each row
            count = 0
            for _, row in df.iterrows():
                inflation_data = InflationData(
                    month=int(row['month']),
                    year=int(row['year']),
                    inflation_rate_percent=Decimal(str(row['inflation_rate_percent'])),
                    source=row.get('source', 'CSV Import'),
                    notes=row.get('notes', None)
                )
                
                self.data_store.save_inflation_data(inflation_data)
                count += 1
            
            return count
        
        except pd.errors.ParserError as e:
            raise CSVParseError(f"Failed to parse CSV: {e}")
        except (ValueError, KeyError) as e:
            raise CSVParseError(f"Invalid CSV data: {e}")
    
    def get_inflation_for_period(
        self, 
        month: int, 
        year: int
    ) -> Optional[InflationData]:
        """
        Get inflation data for specific month/year.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            InflationData if found, None otherwise
        """
        validate_month(month)
        validate_year(year)
        
        all_data = self.data_store.get_inflation_data_range(year, year)
        
        for data in all_data:
            if data.month == month and data.year == year:
                return data
        
        return None
    
    def calculate_legal_max_increase(
        self, 
        base_amount: Decimal, 
        month: int, 
        year: int
    ) -> Decimal:
        """
        Calculate legal maximum rent increase based on inflation.
        
        Args:
            base_amount: Current rent amount in TL
            month: Month of increase
            year: Year of increase
            
        Returns:
            Legal maximum rent amount
            
        Example:
            If base_amount = 15000 TL and inflation = 85.51%,
            legal max = 15000 * (1 + 0.8551) = 27,826.50 TL
        """
        inflation = self.get_inflation_for_period(month, year)
        
        if not inflation:
            # No inflation data available
            # Return base amount (no increase allowed without data)
            return base_amount
        
        multiplier = inflation.legal_max_increase_multiplier()
        legal_max = base_amount * multiplier
        
        return legal_max.quantize(Decimal("0.01"))
    
    def save_manual_entry(
        self, 
        month: int, 
        year: int, 
        inflation_rate_percent: Decimal,
        source: str = "Manual Entry",
        notes: Optional[str] = None
    ) -> None:
        """
        Manually save inflation data entry.
        
        Args:
            month: Month (1-12)
            year: Year
            inflation_rate_percent: Inflation rate as percentage
            source: Data source
            notes: Optional notes
        """
        validate_month(month)
        validate_year(year)
        
        inflation_data = InflationData(
            month=month,
            year=year,
            inflation_rate_percent=inflation_rate_percent,
            source=source,
            notes=notes
        )
        
        self.data_store.save_inflation_data(inflation_data)
    
    def get_all_inflation_data(
        self, 
        start_year: int = 2020, 
        end_year: Optional[int] = None
    ) -> List[InflationData]:
        """
        Get all inflation data for year range.
        
        Args:
            start_year: Start year
            end_year: End year (defaults to current year)
            
        Returns:
            List of InflationData records
        """
        if end_year is None:
            end_year = datetime.now().year
        
        validate_year(start_year)
        validate_year(end_year)
        
        return self.data_store.get_inflation_data_range(start_year, end_year)
    
    def get_yearly_tufe(self, year: int) -> Optional[Decimal]:
        """
        Get yearly TÜFE rate for given year.
        
        Args:
            year: Year to get TÜFE for
            
        Returns:
            TÜFE rate as Decimal or None if not available
        """
        if not isinstance(year, int):
            raise ValueError("year must be an integer")
        
        if year < 2000 or year > 2100:
            raise ValueError("year must be between 2000-2100")
        
        try:
            # Try to get from database first
            inflation_data = self.data_store.get_inflation_data_range(year, year)
            if inflation_data:
                # Return the latest month's data for the year
                latest_data = max(inflation_data, key=lambda x: x.month)
                return latest_data.inflation_rate_percent
        except Exception:
            # If database fails, return None
            pass
        
        return None
    
    def is_tufe_available(self, year: int) -> bool:
        """
        Check if TÜFE data is available for given year.
        
        Args:
            year: Year to check
            
        Returns:
            True if TÜFE data is available
        """
        if not isinstance(year, int):
            raise ValueError("year must be an integer")
        
        if year < 2000 or year > 2100:
            return False
        
        try:
            # Check if data exists in database
            inflation_data = self.data_store.get_inflation_data_range(year, year)
            return len(inflation_data) > 0
        except Exception:
            # If database fails, return False
            return False
    
    def fetch_tufe_from_tcmb(self, year: int) -> Optional[Decimal]:
        """
        Fetch TÜFE data from TCMB website.
        
        Args:
            year: Year to fetch TÜFE for
            
        Returns:
            TÜFE rate as Decimal or None if not available
        """
        if not isinstance(year, int):
            raise ValueError("year must be an integer")
        
        if year < 2000 or year > 2100:
            return None
        
        try:
            import requests
            from bs4 import BeautifulSoup
            import re
            
            # TCMB TÜFE data URL
            url = "https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Istatistikler/Enflasyon+Verileri/Tuketici+Fiyatlari"
            
            # Fetch the page
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for TÜFE data in tables or specific elements
            # This is a simplified approach - in practice, you'd need to adapt to TCMB's actual HTML structure
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Look for year in first cell and percentage in second cell
                        first_cell = cells[0].get_text(strip=True)
                        second_cell = cells[1].get_text(strip=True)
                        
                        # Check if this row contains data for our target year
                        if str(year) in first_cell:
                            # Extract percentage value
                            percentage_match = re.search(r'(\d+[,.]?\d*)', second_cell)
                            if percentage_match:
                                percentage_str = percentage_match.group(1).replace(',', '.')
                                try:
                                    percentage = float(percentage_str)
                                    return Decimal(str(percentage))
                                except ValueError:
                                    continue
            
            # If no data found in tables, try alternative approach
            # Look for TÜFE data in text content
            page_text = soup.get_text()
            year_pattern = rf'{year}.*?(\d+[,.]?\d*)\s*%'
            match = re.search(year_pattern, page_text, re.IGNORECASE)
            if match:
                percentage_str = match.group(1).replace(',', '.')
                try:
                    percentage = float(percentage_str)
                    return Decimal(str(percentage))
                except ValueError:
                    pass
            
            return None
            
        except requests.RequestException as e:
            # Network error
            return None
        except Exception as e:
            # Other errors (parsing, etc.)
            return None
    
    def fetch_tufe_from_tcmb_api(self, year: int, api_key: str) -> Optional[Decimal]:
        """
        Fetch TÜFE data from TCMB EVDS API.
        
        Args:
            year: Year to fetch TÜFE for
            api_key: TCMB EVDS API key
            
        Returns:
            TÜFE rate as Decimal or None if not available
            
        Raises:
            TufeApiError: If API call fails
            TufeValidationError: If data validation fails
        """
        try:
            from src.services.tcmb_api_client import TCMBApiClient
            from src.services.exceptions import TufeApiError, TufeValidationError
            
            # Validate inputs
            if not api_key or not api_key.strip():
                raise TufeValidationError("API key is required")
            
            if not (2000 <= year <= 2100):
                raise TufeValidationError(f"Invalid year: {year}")
            
            # Create API client
            client = TCMBApiClient(api_key)
            
            # Fetch data from API
            response = client.fetch_tufe_data(year)
            
            # Extract TÜFE rate
            tufe_rate = client.extract_tufe_rate(response)
            
            if tufe_rate is not None:
                # Cache the data
                self.cache_tufe_data(year, tufe_rate, "TCMB EVDS API", str(response))
            
            return tufe_rate
            
        except Exception as e:
            if isinstance(e, (TufeApiError, TufeValidationError)):
                raise
            else:
                raise TufeApiError(f"Failed to fetch TÜFE from TCMB API: {e}")
    
    def get_tufe_data_sources(self) -> List:
        """Get all available TÜFE data sources."""
        try:
            from src.services.tufe_data_source_service import TufeDataSourceService
            source_service = TufeDataSourceService(self.data_store)
            return source_service.get_all_sources()
        except Exception as e:
            raise TufeApiError(f"Failed to get TÜFE data sources: {e}")
    
    def get_active_tufe_source(self) -> Optional:
        """Get the currently active TÜFE data source."""
        try:
            from src.services.tufe_data_source_service import TufeDataSourceService
            source_service = TufeDataSourceService(self.data_store)
            return source_service.get_active_source()
        except Exception as e:
            raise TufeApiError(f"Failed to get active TÜFE source: {e}")
    
    def cache_tufe_data(self, year: int, rate: Decimal, source: str, api_response: str) -> int:
        """
        Cache TÜFE data with source attribution.
        
        Args:
            year: Year for the data
            rate: TÜFE rate
            source: Data source name
            api_response: Raw API response
            
        Returns:
            Cache entry ID
        """
        try:
            from src.services.tufe_cache_service import TufeCacheService
            cache_service = TufeCacheService(self.data_store)
            return cache_service.cache_data(year, rate, source, api_response)
        except Exception as e:
            raise TufeApiError(f"Failed to cache TÜFE data: {e}")
    
    def get_cached_tufe_data(self, year: int) -> Optional:
        """Get cached TÜFE data for a year."""
        try:
            from src.services.tufe_cache_service import TufeCacheService
            cache_service = TufeCacheService(self.data_store)
            return cache_service.get_cached_data(year)
        except Exception as e:
            raise TufeApiError(f"Failed to get cached TÜFE data: {e}")
    
    def is_tufe_cache_valid(self, year: int) -> bool:
        """Check if TÜFE cache is valid for a year."""
        try:
            from src.services.tufe_cache_service import TufeCacheService
            cache_service = TufeCacheService(self.data_store)
            return cache_service.is_cache_valid(year)
        except Exception as e:
            raise TufeApiError(f"Failed to check TÜFE cache validity: {e}")
    
    # OECD API Integration Methods
    
    def fetch_tufe_from_oecd_api(self, start_year: int, end_year: int) -> List[InflationData]:
        """
        Fetch TÜFE data from OECD API for specified year range.
        
        Args:
            start_year: Starting year (2000-2025)
            end_year: Ending year (2000-2025)
        
        Returns:
            List of InflationData objects with TÜFE rates
        
        Raises:
            TufeApiError: If API request fails
            TufeValidationError: If data validation fails
        """
        try:
            # Fetch data from OECD API
            api_result = self.oecd_client.fetch_tufe_data(start_year, end_year)
            
            # Convert to InflationData objects
            inflation_data = []
            for item in api_result.get('items', []):
                try:
                    # Validate the data
                    self.data_validator.validate_complete_record(
                        item['year'], item['month'], item['value'], 'OECD SDMX API'
                    )
                    
                    # Create InflationData object
                    inflation_item = InflationData(
                        year=item['year'],
                        month=item['month'],
                        inflation_rate_percent=Decimal(str(item['value'])),
                        source='OECD SDMX API'
                    )
                    inflation_data.append(inflation_item)
                    
                except TufeValidationError as e:
                    # Skip invalid data points
                    continue
            
            return inflation_data
            
        except Exception as e:
            raise TufeApiError(f"Failed to fetch TÜFE data from OECD API: {e}")
    
    def fetch_and_cache_oecd_tufe_data(self, start_year: int, end_year: int) -> List[InflationData]:
        """
        Fetch TÜFE data from OECD API and cache it.
        
        Args:
            start_year: Starting year (2000-2025)
            end_year: Ending year (2000-2025)
        
        Returns:
            List of InflationData objects with TÜFE rates
        """
        try:
            # Fetch data from OECD API
            inflation_data = self.fetch_tufe_from_oecd_api(start_year, end_year)
            
            # Cache the data
            self.cache_oecd_tufe_data(inflation_data)
            
            return inflation_data
            
        except Exception as e:
            raise TufeApiError(f"Failed to fetch and cache OECD TÜFE data: {e}")
    
    def cache_oecd_tufe_data(self, inflation_data: List[InflationData]) -> None:
        """
        Cache OECD TÜFE data.
        
        Args:
            inflation_data: List of InflationData objects to cache
        """
        try:
            from src.services.tufe_cache_service import TufeCacheService
            cache_service = TufeCacheService(self.data_store)
            cache_service.cache_oecd_data(inflation_data, ttl_hours=168)  # 7 days
        except Exception as e:
            raise TufeApiError(f"Failed to cache OECD TÜFE data: {e}")
    
    def get_cached_oecd_tufe_data(self, year: int, month: int = None) -> Optional[InflationData]:
        """
        Get cached OECD TÜFE data.
        
        Args:
            year: Year to retrieve
            month: Month to retrieve (optional)
        
        Returns:
            InflationData object or None if not found
        """
        try:
            from src.services.tufe_cache_service import TufeCacheService
            cache_service = TufeCacheService(self.data_store)
            return cache_service.get_cached_oecd_data(year, month)
        except Exception as e:
            raise TufeApiError(f"Failed to get cached OECD TÜFE data: {e}")
    
    def is_oecd_api_healthy(self) -> bool:
        """
        Check if OECD API is healthy.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            return self.oecd_client.is_healthy()
        except Exception:
            return False
    
    def get_oecd_api_info(self) -> dict:
        """
        Get OECD API information.
        
        Returns:
            Dictionary with API information
        """
        try:
            return self.oecd_client.get_api_info()
        except Exception as e:
            raise TufeApiError(f"Failed to get OECD API info: {e}")
    
    def get_rate_limit_status(self) -> dict:
        """
        Get rate limit status.
        
        Returns:
            Dictionary with rate limit status
        """
        try:
            return self.rate_limit_handler.get_rate_limit_status()
        except Exception as e:
            raise TufeApiError(f"Failed to get rate limit status: {e}")
    
    def validate_oecd_data(self, data: List[dict]) -> List[dict]:
        """
        Validate OECD data.
        
        Args:
            data: List of data records to validate
        
        Returns:
            List of valid records
        """
        try:
            return self.data_validator.validate_batch_data(data)
        except Exception as e:
            raise TufeValidationError(f"Failed to validate OECD data: {e}")

