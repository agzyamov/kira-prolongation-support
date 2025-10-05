"""
Data models for Kira Prolongation Support application.
All models are immutable dataclasses with built-in validation.
"""
from .rental_agreement import RentalAgreement
from .exchange_rate import ExchangeRate
from .payment_record import PaymentRecord
from .market_rate import MarketRate
from .inflation_data import InflationData

__all__ = [
    "RentalAgreement",
    "ExchangeRate",
    "PaymentRecord",
    "MarketRate",
    "InflationData",
]

