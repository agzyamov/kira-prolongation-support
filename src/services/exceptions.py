"""
Custom exceptions for TÜFE data services.

This module defines custom exception classes for handling various error scenarios
in TÜFE data fetching, validation, and caching operations.
"""


class TufeApiError(Exception):
    """
    Base exception for TÜFE API-related errors.
    
    Raised when there are issues with API requests, responses, or connectivity.
    """
    
    def __init__(self, message: str, status_code: int = None, response_data: str = None):
        """
        Initialize TÜFE API error.
        
        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response_data: Response data (if applicable)
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
    
    def __str__(self):
        """Return string representation of the error."""
        if self.status_code:
            return f"TÜFE API Error {self.status_code}: {super().__str__()}"
        return f"TÜFE API Error: {super().__str__()}"
    
    def __repr__(self):
        """Return detailed representation of the error."""
        return f"TufeApiError(message='{super().__str__()}', status_code={self.status_code})"


class TufeValidationError(Exception):
    """
    Exception for TÜFE data validation errors.
    
    Raised when TÜFE data fails validation checks.
    """
    
    def __init__(self, message: str, field: str = None, value: any = None):
        """
        Initialize TÜFE validation error.
        
        Args:
            message: Error message
            field: Field that failed validation (if applicable)
            value: Value that failed validation (if applicable)
        """
        super().__init__(message)
        self.field = field
        self.value = value
    
    def __str__(self):
        """Return string representation of the error."""
        if self.field:
            return f"TÜFE Validation Error in field '{self.field}': {super().__str__()}"
        return f"TÜFE Validation Error: {super().__str__()}"
    
    def __repr__(self):
        """Return detailed representation of the error."""
        return f"TufeValidationError(message='{super().__str__()}', field='{self.field}', value={self.value})"


class TufeCacheError(Exception):
    """
    Exception for TÜFE cache-related errors.
    
    Raised when there are issues with caching operations.
    """
    
    def __init__(self, message: str, operation: str = None, key: str = None):
        """
        Initialize TÜFE cache error.
        
        Args:
            message: Error message
            operation: Cache operation that failed (if applicable)
            key: Cache key (if applicable)
        """
        super().__init__(message)
        self.operation = operation
        self.key = key
    
    def __str__(self):
        """Return string representation of the error."""
        if self.operation:
            return f"TÜFE Cache Error in operation '{self.operation}': {super().__str__()}"
        return f"TÜFE Cache Error: {super().__str__()}"
    
    def __repr__(self):
        """Return detailed representation of the error."""
        return f"TufeCacheError(message='{super().__str__()}', operation='{self.operation}', key='{self.key}')"


class TufeRateLimitError(TufeApiError):
    """
    Exception for TÜFE API rate limiting errors.
    
    Raised when API requests are rate limited.
    """
    
    def __init__(self, message: str, retry_after: int = None, rate_limit_remaining: int = None):
        """
        Initialize TÜFE rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying (if applicable)
            rate_limit_remaining: Remaining requests in current period (if applicable)
        """
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
        self.rate_limit_remaining = rate_limit_remaining
    
    def __str__(self):
        """Return string representation of the error."""
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} (Retry after {self.retry_after} seconds)"
        return base_msg
    
    def __repr__(self):
        """Return detailed representation of the error."""
        return f"TufeRateLimitError(message='{super().__str__()}', retry_after={self.retry_after}, rate_limit_remaining={self.rate_limit_remaining})"


class TufeDataNotFoundError(TufeApiError):
    """
    Exception for when TÜFE data is not found.
    
    Raised when requested TÜFE data is not available.
    """
    
    def __init__(self, message: str, year: int = None, month: int = None):
        """
        Initialize TÜFE data not found error.
        
        Args:
            message: Error message
            year: Year that was requested (if applicable)
            month: Month that was requested (if applicable)
        """
        super().__init__(message, status_code=404)
        self.year = year
        self.month = month
    
    def __str__(self):
        """Return string representation of the error."""
        base_msg = super().__str__()
        if self.year and self.month:
            return f"{base_msg} (Year: {self.year}, Month: {self.month})"
        elif self.year:
            return f"{base_msg} (Year: {self.year})"
        return base_msg
    
    def __repr__(self):
        """Return detailed representation of the error."""
        return f"TufeDataNotFoundError(message='{super().__str__()}', year={self.year}, month={self.month})"


class TufeConfigurationError(Exception):
    """
    Exception for TÜFE configuration errors.
    
    Raised when there are issues with service configuration.
    """
    
    def __init__(self, message: str, config_key: str = None):
        """
        Initialize TÜFE configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error (if applicable)
        """
        super().__init__(message)
        self.config_key = config_key
    
    def __str__(self):
        """Return string representation of the error."""
        if self.config_key:
            return f"TÜFE Configuration Error for key '{self.config_key}': {super().__str__()}"
        return f"TÜFE Configuration Error: {super().__str__()}"
    
    def __repr__(self):
        """Return detailed representation of the error."""
        return f"TufeConfigurationError(message='{super().__str__()}', config_key='{self.config_key}')"


class TufeServiceError(Exception):
    """
    Base exception for TÜFE service errors.
    
    Raised when there are general service-level errors.
    """
    
    def __init__(self, message: str, service_name: str = None):
        """
        Initialize TÜFE service error.
        
        Args:
            message: Error message
            service_name: Name of the service that caused the error (if applicable)
        """
        super().__init__(message)
        self.service_name = service_name
    
    def __str__(self):
        """Return string representation of the error."""
        if self.service_name:
            return f"TÜFE Service Error in '{self.service_name}': {super().__str__()}"
        return f"TÜFE Service Error: {super().__str__()}"
    
    def __repr__(self):
        """Return detailed representation of the error."""
        return f"TufeServiceError(message='{super().__str__()}', service_name='{self.service_name}')"


# Additional exception classes for other services
class ServiceError(Exception):
    """Base exception for all service errors."""
    pass

class ExchangeRateAPIError(Exception):
    """Exception for exchange rate API errors."""
    pass

class CalculationError(Exception):
    """Exception for calculation errors."""
    pass

class ExportError(Exception):
    """Exception for export errors."""
    pass

class CSVParseError(Exception):
    """Exception for CSV parsing errors."""
    pass

class NegotiationModeError(Exception):
    """Exception for negotiation mode errors."""
    pass

class LegalRuleError(Exception):
    """Exception for legal rule errors."""
    pass

class TufeDataError(Exception):
    """Exception for TÜFE data errors."""
    pass

class TufeDataSourceError(Exception):
    """Exception for TÜFE data source errors."""
    pass

class TufeApiKeyError(Exception):
    """Exception for TÜFE API key errors."""
    pass

class TufeConfigError(Exception):
    """Exception for TÜFE configuration errors."""
    pass

# Exception hierarchy for better error handling
TufeException = Exception  # Base for all TÜFE exceptions

# Specific exception types
TufeApiException = TufeApiError
TufeValidationException = TufeValidationError
TufeCacheException = TufeCacheError
TufeRateLimitException = TufeRateLimitError
TufeDataNotFoundException = TufeDataNotFoundError
TufeConfigurationException = TufeConfigurationError
TufeServiceException = TufeServiceError