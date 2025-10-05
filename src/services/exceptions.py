"""
Service-level exceptions for Kira Prolongation Support.
"""


class ServiceError(Exception):
    """Base exception for service errors"""
    pass


class ExchangeRateAPIError(ServiceError):
    """Raised when exchange rate API fails"""
    pass


class OCRError(ServiceError):
    """Raised when OCR processing fails"""
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

