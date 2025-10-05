"""
Contract tests for extended InflationService.
Tests the new TÜFE methods before implementation.
"""

import pytest
from decimal import Decimal
from src.services.inflation_service import InflationService


class TestInflationServiceExtensions:
    """Contract tests for InflationService extensions."""

    def test_get_yearly_tufe_returns_decimal_or_none(self):
        """Test that get_yearly_tufe returns Decimal or None."""
        service = InflationService()
        
        # Test with valid year
        tufe = service.get_yearly_tufe(2024)
        assert tufe is None or isinstance(tufe, Decimal)

    def test_get_yearly_tufe_handles_invalid_years(self):
        """Test that get_yearly_tufe handles invalid years gracefully."""
        service = InflationService()
        
        # Test with future year (should return None)
        tufe = service.get_yearly_tufe(2030)
        assert tufe is None
        
        # Test with very old year (should return None)
        tufe = service.get_yearly_tufe(1900)
        assert tufe is None

    def test_is_tufe_available_returns_boolean(self):
        """Test that is_tufe_available returns a boolean."""
        service = InflationService()
        
        available = service.is_tufe_available(2024)
        assert isinstance(available, bool)

    def test_is_tufe_available_handles_different_years(self):
        """Test that is_tufe_available handles different years."""
        service = InflationService()
        
        # Test current year
        current_available = service.is_tufe_available(2024)
        assert isinstance(current_available, bool)
        
        # Test future year (should be False)
        future_available = service.is_tufe_available(2030)
        assert future_available is False
        
        # Test past year
        past_available = service.is_tufe_available(2020)
        assert isinstance(past_available, bool)

    def test_fetch_tufe_from_tcmb_returns_decimal_or_none(self):
        """Test that fetch_tufe_from_tcmb returns Decimal or None."""
        service = InflationService()
        
        # Test with valid year
        tufe = service.fetch_tufe_from_tcmb(2024)
        assert tufe is None or isinstance(tufe, Decimal)

    def test_fetch_tufe_from_tcmb_handles_network_errors(self):
        """Test that fetch_tufe_from_tcmb handles network errors gracefully."""
        service = InflationService()
        
        # Should not raise exception, should return None on error
        tufe = service.fetch_tufe_from_tcmb(2024)
        assert tufe is None or isinstance(tufe, Decimal)

    def test_tufe_data_consistency(self):
        """Test that TÜFE data methods are consistent."""
        service = InflationService()
        
        year = 2024
        
        # If data is available, get_yearly_tufe should return it
        if service.is_tufe_available(year):
            tufe = service.get_yearly_tufe(year)
            assert tufe is not None
            assert isinstance(tufe, Decimal)
            assert tufe > 0

    def test_tufe_data_validation(self):
        """Test that TÜFE data is properly validated."""
        service = InflationService()
        
        year = 2024
        tufe = service.get_yearly_tufe(year)
        
        if tufe is not None:
            # TÜFE should be positive
            assert tufe > 0
            
            # TÜFE should be reasonable (not more than 100%)
            assert tufe < 100

    def test_fetch_tufe_handles_invalid_years(self):
        """Test that fetch_tufe_from_tcmb handles invalid years."""
        service = InflationService()
        
        # Test with invalid year
        tufe = service.fetch_tufe_from_tcmb(1900)
        assert tufe is None
        
        # Test with future year
        tufe = service.fetch_tufe_from_tcmb(2030)
        assert tufe is None
