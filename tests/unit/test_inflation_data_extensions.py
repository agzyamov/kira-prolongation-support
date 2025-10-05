"""
Unit tests for extended InflationData methods.
"""

import pytest
from decimal import Decimal
from src.models.inflation_data import InflationData


class TestInflationDataExtensions:
    """Unit tests for extended InflationData methods."""

    def test_is_from_tcmb_api_true(self):
        """Test checking if data is from TCMB API."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TCMB EVDS API"
        )
        
        assert inflation_data.is_from_tcmb_api() is True

    def test_is_from_tcmb_api_case_insensitive(self):
        """Test checking if data is from TCMB API (case insensitive)."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="tcmb evds api"
        )
        
        assert inflation_data.is_from_tcmb_api() is True

    def test_is_from_tcmb_api_with_evds(self):
        """Test checking if data is from TCMB API with EVDS in source."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="EVDS API"
        )
        
        assert inflation_data.is_from_tcmb_api() is True

    def test_is_from_tcmb_api_false(self):
        """Test checking if data is not from TCMB API."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="Manual Entry"
        )
        
        assert inflation_data.is_from_tcmb_api() is False

    def test_is_from_tcmb_api_other_source(self):
        """Test checking if data is not from TCMB API with other source."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TUİK"
        )
        
        assert inflation_data.is_from_tcmb_api() is False

    def test_get_source_attribution_tcmb(self):
        """Test getting source attribution for TCMB data."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TCMB EVDS API"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: TCMB EVDS API"

    def test_get_source_attribution_manual(self):
        """Test getting source attribution for manual entry."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="Manual Entry"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: Manual Entry"

    def test_get_source_attribution_other(self):
        """Test getting source attribution for other source."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TUİK"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: TUİK"

    def test_get_source_attribution_case_insensitive_manual(self):
        """Test getting source attribution for manual entry (case insensitive)."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="manual entry"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: manual entry"

    def test_get_source_attribution_contains_manual(self):
        """Test getting source attribution for source containing 'Manual'."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="Manual TÜFE Entry"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: Manual Entry"

    def test_get_source_attribution_tcmb_case_insensitive(self):
        """Test getting source attribution for TCMB data (case insensitive)."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="tcmb evds api"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: TCMB EVDS API"

    def test_get_source_attribution_evds_only(self):
        """Test getting source attribution for EVDS-only source."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="EVDS API"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: TCMB EVDS API"

    def test_source_attribution_integration(self):
        """Test source attribution integration with is_from_tcmb_api."""
        # TCMB source
        tcmb_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TCMB EVDS API"
        )
        
        assert tcmb_data.is_from_tcmb_api() is True
        assert tcmb_data.get_source_attribution() == "Data source: TCMB EVDS API"
        
        # Manual source
        manual_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="Manual Entry"
        )
        
        assert manual_data.is_from_tcmb_api() is False
        assert manual_data.get_source_attribution() == "Data source: Manual Entry"
        
        # Other source
        other_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TUİK"
        )
        
        assert other_data.is_from_tcmb_api() is False
        assert other_data.get_source_attribution() == "Data source: TUİK"

    def test_source_attribution_with_special_characters(self):
        """Test source attribution with special characters in source name."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TCMB EVDS API v2.0"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: TCMB EVDS API"

    def test_source_attribution_with_unicode(self):
        """Test source attribution with Unicode characters."""
        inflation_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TÜFE Veri Kaynağı"
        )
        
        attribution = inflation_data.get_source_attribution()
        assert attribution == "Data source: TÜFE Veri Kaynağı"

    def test_is_from_tcmb_api_with_partial_match(self):
        """Test is_from_tcmb_api with partial matches."""
        # Should match TCMB
        tcmb_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="TCMB Data"
        )
        assert tcmb_data.is_from_tcmb_api() is True
        
        # Should match EVDS
        evds_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="EVDS Data"
        )
        assert evds_data.is_from_tcmb_api() is True
        
        # Should not match
        other_data = InflationData(
            year=2024,
            month=12,
            inflation_rate_percent=Decimal("44.38"),
            source="Other Data"
        )
        assert other_data.is_from_tcmb_api() is False
