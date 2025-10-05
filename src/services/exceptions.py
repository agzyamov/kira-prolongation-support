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

