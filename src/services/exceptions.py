"""
Service-level exceptions for Kira Prolongation Support.
"""


class ServiceError(Exception):
    """Base exception for service errors"""
    pass


class ExchangeRateAPIError(ServiceError):
    """Raised when exchange rate API fails"""
    pass


class CalculationError(ServiceError):
    """Raised when calculation fails"""
    pass


class ExportError(ServiceError):
    """Raised when export operation fails"""
    pass


class CSVParseError(ServiceError):
    """Raised when CSV parsing fails"""
    pass


class NegotiationModeError(ServiceError):
    """Raised when invalid negotiation mode is provided"""
    pass


class LegalRuleError(ServiceError):
    """Raised when legal rule cannot be determined"""
    pass


class TufeDataError(ServiceError):
    """Raised when TÜFE data is unavailable or invalid"""
    pass


class TufeApiError(ServiceError):
    """Raised when TÜFE API operations fail"""
    pass


class TufeValidationError(ServiceError):
    """Raised when TÜFE data validation fails"""
    pass


class TufeDataSourceError(ServiceError):
    """Raised when TÜFE data source operations fail"""
    pass


class TufeApiKeyError(ServiceError):
    """Raised when TÜFE API key operations fail"""
    pass


class TufeCacheError(ServiceError):
    """Raised when TÜFE cache operations fail"""
    pass


class TufeConfigError(ServiceError):
    """Raised when TÜFE configuration operations fail"""
    pass

