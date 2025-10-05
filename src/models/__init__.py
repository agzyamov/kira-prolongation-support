"""
Data models for Kira Prolongation Support application.
All models are immutable dataclasses with built-in validation.
"""
from .rental_agreement import RentalAgreement
from .exchange_rate import ExchangeRate
from .payment_record import PaymentRecord
from .inflation_data import InflationData
from .negotiation_settings import NegotiationSettings
from .legal_rule import LegalRule
from .tufe_data_source import TufeDataSource
from .tufe_api_key import TufeApiKey
from .tufe_data_cache import TufeDataCache

__all__ = [
    "RentalAgreement",
    "ExchangeRate",
    "PaymentRecord",
    "InflationData",
    "NegotiationSettings",
    "LegalRule",
    "TufeDataSource",
    "TufeApiKey",
    "TufeDataCache",
]

