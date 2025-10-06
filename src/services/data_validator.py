"""
Data Validator for TÜFE Data

This service validates TÜFE data fetched from various sources to ensure
data quality and consistency before storing in the database.
"""

from typing import Union, List, Dict, Any
from datetime import datetime

from src.config.oecd_config import VALIDATION_CONFIG
from src.services.exceptions import TufeValidationError


class DataValidator:
    """
    Validates TÜFE data for quality and consistency.
    
    Provides methods to validate TÜFE rates, years, months, data sources,
    and complete records according to business rules.
    """
    
    def __init__(self, min_rate: float = None, max_rate: float = None,
                 min_year: int = None, max_year_offset: int = None):
        """
        Initialize data validator.
        
        Args:
            min_rate: Minimum valid TÜFE rate (percentage) (default from config)
            max_rate: Maximum valid TÜFE rate (percentage) (default from config)
            min_year: Minimum valid year (default from config)
            max_year_offset: Maximum years in the future (default from config)
        """
        self.min_rate = min_rate or VALIDATION_CONFIG["min_tufe_rate"]
        self.max_rate = max_rate or VALIDATION_CONFIG["max_tufe_rate"]
        self.min_year = min_year or VALIDATION_CONFIG["min_year"]
        self.max_year_offset = max_year_offset or VALIDATION_CONFIG["max_year_offset"]
        self.valid_months = VALIDATION_CONFIG["valid_months"]
        self.required_source = VALIDATION_CONFIG["required_source"]
    
    def validate_tufe_rate(self, rate: Union[float, int, str]) -> None:
        """
        Validate TÜFE rate value.
        
        Args:
            rate: TÜFE rate to validate
        
        Raises:
            TufeValidationError: If rate is invalid
        """
        # Check if rate is None
        if rate is None:
            raise TufeValidationError("TÜFE rate cannot be None")
        
        # Check if rate is a number
        try:
            rate_float = float(rate)
        except (ValueError, TypeError):
            raise TufeValidationError(f"TÜFE rate must be a number, got: {type(rate).__name__}")
        
        # Check if rate is within valid range
        if not (self.min_rate <= rate_float <= self.max_rate):
            raise TufeValidationError(
                f"TÜFE rate must be between {self.min_rate}% and {self.max_rate}%, got: {rate_float}%"
            )
        
        # Check for NaN or infinite values
        if not (rate_float == rate_float):  # NaN check
            raise TufeValidationError("TÜFE rate cannot be NaN")
        
        if rate_float == float('inf') or rate_float == float('-inf'):
            raise TufeValidationError("TÜFE rate cannot be infinite")
    
    def validate_year(self, year: Union[int, str]) -> None:
        """
        Validate year value.
        
        Args:
            year: Year to validate
        
        Raises:
            TufeValidationError: If year is invalid
        """
        # Check if year is None
        if year is None:
            raise TufeValidationError("Year cannot be None")
        
        # Check if year is an integer
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            raise TufeValidationError(f"Year must be an integer, got: {type(year).__name__}")
        
        # Check if year is within valid range
        current_year = datetime.now().year
        max_year = current_year + self.max_year_offset
        
        if not (self.min_year <= year_int <= max_year):
            raise TufeValidationError(
                f"Year must be between {self.min_year} and {max_year}, got: {year_int}"
            )
    
    def validate_month(self, month: Union[int, str]) -> None:
        """
        Validate month value.
        
        Args:
            month: Month to validate
        
        Raises:
            TufeValidationError: If month is invalid
        """
        # Check if month is None
        if month is None:
            raise TufeValidationError("Month cannot be None")
        
        # Check if month is an integer
        try:
            month_int = int(month)
        except (ValueError, TypeError):
            raise TufeValidationError(f"Month must be an integer, got: {type(month).__name__}")
        
        # Check if month is within valid range
        if month_int not in self.valid_months:
            raise TufeValidationError(
                f"Month must be between 1 and 12, got: {month_int}"
            )
    
    def validate_data_source(self, source: str) -> None:
        """
        Validate data source.
        
        Args:
            source: Data source to validate
        
        Raises:
            TufeValidationError: If source is invalid
        """
        # Check if source is None
        if source is None:
            raise TufeValidationError("Data source cannot be None")
        
        # Check if source is a string
        if not isinstance(source, str):
            raise TufeValidationError(f"Data source must be a string, got: {type(source).__name__}")
        
        # Check if source is not empty
        if not source.strip():
            raise TufeValidationError("Data source cannot be empty or whitespace only")
        
        # Check if source is not too long (reasonable limit)
        if len(source) > 100:
            raise TufeValidationError(f"Data source too long (max 100 characters), got: {len(source)}")
    
    def validate_complete_record(self, year: Union[int, str], month: Union[int, str], 
                                rate: Union[float, int, str], source: str) -> None:
        """
        Validate complete TÜFE record.
        
        Args:
            year: Year
            month: Month
            rate: TÜFE rate
            source: Data source
        
        Raises:
            TufeValidationError: If any field is invalid
        """
        # Validate each field individually
        self.validate_year(year)
        self.validate_month(month)
        self.validate_tufe_rate(rate)
        self.validate_data_source(source)
        
        # Additional cross-field validations
        try:
            year_int = int(year)
            month_int = int(month)
            rate_float = float(rate)
        except (ValueError, TypeError):
            raise TufeValidationError("Invalid data types in record")
        
        # Check for reasonable TÜFE rate for the given year/month
        # (This could be expanded with historical data validation)
        if year_int == datetime.now().year:
            # For current year, rates should be reasonable
            if rate_float > 100:  # Very high inflation
                raise TufeValidationError(f"TÜFE rate {rate_float}% seems unusually high for {year_int}")
    
    def validate_batch_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate a batch of TÜFE data records.
        
        Args:
            data: List of data records to validate
        
        Returns:
            List of valid records
        
        Raises:
            TufeValidationError: If validation fails for any record
        """
        if not isinstance(data, list):
            raise TufeValidationError("Data must be a list")
        
        valid_records = []
        errors = []
        
        for i, record in enumerate(data):
            try:
                # Extract required fields
                year = record.get('year')
                month = record.get('month')
                rate = record.get('tufe_rate') or record.get('rate') or record.get('value')
                source = record.get('source')
                
                # Validate the record
                self.validate_complete_record(year, month, rate, source)
                
                # Add to valid records
                valid_records.append(record)
                
            except TufeValidationError as e:
                errors.append(f"Record {i}: {str(e)}")
        
        # If there are validation errors, raise them
        if errors:
            raise TufeValidationError(f"Validation errors: {'; '.join(errors)}")
        
        return valid_records
    
    def validate_time_period(self, time_period: str) -> Dict[str, int]:
        """
        Validate and parse time period string.
        
        Args:
            time_period: Time period string (e.g., "2024-01")
        
        Returns:
            Dictionary with parsed year and month
        
        Raises:
            TufeValidationError: If time period is invalid
        """
        if not isinstance(time_period, str):
            raise TufeValidationError("Time period must be a string")
        
        if not time_period.strip():
            raise TufeValidationError("Time period cannot be empty")
        
        # Check format (YYYY-MM)
        if len(time_period) != 7 or time_period[4] != '-':
            raise TufeValidationError(f"Time period must be in YYYY-MM format, got: {time_period}")
        
        try:
            year_str, month_str = time_period.split('-')
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            raise TufeValidationError(f"Invalid time period format: {time_period}")
        
        # Validate year and month
        self.validate_year(year)
        self.validate_month(month)
        
        return {'year': year, 'month': month}
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """
        Get current validation rules.
        
        Returns:
            Dictionary with validation rules
        """
        current_year = datetime.now().year
        
        return {
            'min_rate': self.min_rate,
            'max_rate': self.max_rate,
            'min_year': self.min_year,
            'max_year': current_year + self.max_year_offset,
            'valid_months': self.valid_months,
            'required_source': self.required_source
        }
    
    def is_valid_rate(self, rate: Union[float, int, str]) -> bool:
        """
        Check if TÜFE rate is valid without raising exception.
        
        Args:
            rate: TÜFE rate to check
        
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate_tufe_rate(rate)
            return True
        except TufeValidationError:
            return False
    
    def is_valid_year(self, year: Union[int, str]) -> bool:
        """
        Check if year is valid without raising exception.
        
        Args:
            year: Year to check
        
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate_year(year)
            return True
        except TufeValidationError:
            return False
    
    def is_valid_month(self, month: Union[int, str]) -> bool:
        """
        Check if month is valid without raising exception.
        
        Args:
            month: Month to check
        
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate_month(month)
            return True
        except TufeValidationError:
            return False
    
    def is_valid_source(self, source: str) -> bool:
        """
        Check if data source is valid without raising exception.
        
        Args:
            source: Data source to check
        
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate_data_source(source)
            return True
        except TufeValidationError:
            return False
