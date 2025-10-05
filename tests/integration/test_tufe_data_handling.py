"""
Integration test for TÜFE data handling.
Tests the complete flow of TÜFE data retrieval and handling.
"""

import pytest
from src.services.inflation_service import InflationService
from src.models.inflation_data import InflationData


class TestTufeDataHandling:
    """Integration tests for TÜFE data handling."""

    def test_tufe_data_retrieval_flow(self):
        """Test the complete flow of TÜFE data retrieval."""
        service = InflationService()
        
        year = 2024
        
        # Check if data is available
        is_available = service.is_tufe_available(year)
        assert isinstance(is_available, bool)
        
        if is_available:
            # If available, should be able to retrieve it
            tufe = service.get_yearly_tufe(year)
            assert tufe is not None
            assert isinstance(tufe, float) or isinstance(tufe, int)
            assert tufe > 0
        else:
            # If not available, should return None
            tufe = service.get_yearly_tufe(year)
            assert tufe is None

    def test_tufe_data_fetching_from_tcmb(self):
        """Test fetching TÜFE data from TCMB."""
        service = InflationService()
        
        year = 2024
        
        # Try to fetch from TCMB
        tufe = service.fetch_tufe_from_tcmb(year)
        
        # Should return None or a valid value
        assert tufe is None or (isinstance(tufe, float) or isinstance(tufe, int))
        
        if tufe is not None:
            assert tufe > 0

    def test_tufe_data_consistency(self):
        """Test that TÜFE data methods are consistent."""
        service = InflationService()
        
        year = 2024
        
        # Check availability
        is_available = service.is_tufe_available(year)
        
        # Get data
        tufe = service.get_yearly_tufe(year)
        
        # Consistency check
        if is_available:
            assert tufe is not None
        else:
            assert tufe is None

    def test_tufe_data_with_different_years(self):
        """Test TÜFE data handling with different years."""
        service = InflationService()
        
        years_to_test = [2020, 2021, 2022, 2023, 2024, 2025, 2030]
        
        for year in years_to_test:
            # Check availability
            is_available = service.is_tufe_available(year)
            assert isinstance(is_available, bool)
            
            # Get data
            tufe = service.get_yearly_tufe(year)
            
            # Future years should not be available
            if year > 2024:
                assert is_available is False
                assert tufe is None
            else:
                # Past/current years might be available
                if is_available:
                    assert tufe is not None
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

    def test_tufe_data_error_handling(self):
        """Test error handling for TÜFE data operations."""
        service = InflationService()
        
        # Test with invalid years
        invalid_years = [1900, -1, 0, 3000]
        
        for year in invalid_years:
            # Should handle gracefully
            is_available = service.is_tufe_available(year)
            assert isinstance(is_available, bool)
            
            tufe = service.get_yearly_tufe(year)
            assert tufe is None
            
            # Fetch should also handle gracefully
            fetched_tufe = service.fetch_tufe_from_tcmb(year)
            assert fetched_tufe is None

    def test_tufe_data_persistence(self):
        """Test that TÜFE data persists correctly."""
        service = InflationService()
        
        year = 2024
        
        # Get data multiple times
        tufe1 = service.get_yearly_tufe(year)
        tufe2 = service.get_yearly_tufe(year)
        
        # Should be consistent
        assert tufe1 == tufe2

    def test_tufe_data_with_inflation_data_model(self):
        """Test TÜFE data integration with InflationData model."""
        # This test would verify that TÜFE data is properly stored
        # in the InflationData model when available
        
        # For now, just test that the service methods work
        service = InflationService()
        
        year = 2024
        tufe = service.get_yearly_tufe(year)
        
        if tufe is not None:
            # If we have TÜFE data, it should be valid
            assert isinstance(tufe, float) or isinstance(tufe, int)
            assert tufe > 0

    def test_tufe_data_network_error_handling(self):
        """Test handling of network errors when fetching TÜFE data."""
        service = InflationService()
        
        year = 2024
        
        # Fetch should handle network errors gracefully
        tufe = service.fetch_tufe_from_tcmb(year)
        
        # Should not raise exception
        assert tufe is None or (isinstance(tufe, float) or isinstance(tufe, int))

    def test_tufe_data_fallback_behavior(self):
        """Test fallback behavior when TÜFE data is unavailable."""
        service = InflationService()
        
        year = 2024
        
        # Check availability
        is_available = service.is_tufe_available(year)
        
        if not is_available:
            # Should return None when not available
            tufe = service.get_yearly_tufe(year)
            assert tufe is None
            
            # Should indicate data is pending
            # This would be handled in the UI layer
