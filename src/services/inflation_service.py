"""
Inflation data service for Turkish inflation rates.
Supports CSV import and legal maximum rent increase calculations.
"""
import pandas as pd
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
import io

from src.models import InflationData
from src.storage import DataStore
from src.services.exceptions import CSVParseError
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

