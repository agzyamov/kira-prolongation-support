"""
Contract tests for extended ExportService.
Tests the new data source disclosure methods before implementation.
"""

import pytest
from src.services.export_service import ExportService
from src.models.rental_agreement import RentalAgreement
from datetime import datetime
from decimal import Decimal


class TestExportServiceExtensions:
    """Contract tests for ExportService extensions."""

    def test_add_data_source_disclosure_returns_string(self):
        """Test that add_data_source_disclosure returns a string."""
        service = ExportService()
        
        content = "This is test export content."
        result = service.add_data_source_disclosure(content)
        
        assert isinstance(result, str)
        assert len(result) > len(content)

    def test_add_data_source_disclosure_includes_required_text(self):
        """Test that add_data_source_disclosure includes required disclosure text."""
        service = ExportService()
        
        content = "Test content"
        result = service.add_data_source_disclosure(content)
        
        assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in result

    def test_add_data_source_disclosure_preserves_original_content(self):
        """Test that add_data_source_disclosure preserves original content."""
        service = ExportService()
        
        content = "Original export content with important data."
        result = service.add_data_source_disclosure(content)
        
        assert content in result

    def test_generate_negotiation_summary_returns_string(self):
        """Test that generate_negotiation_summary returns a string."""
        service = ExportService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        summary = service.generate_negotiation_summary(agreement, "calm")
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_generate_negotiation_summary_handles_different_modes(self):
        """Test that generate_negotiation_summary handles different negotiation modes."""
        service = ExportService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        calm_summary = service.generate_negotiation_summary(agreement, "calm")
        assertive_summary = service.generate_negotiation_summary(agreement, "assertive")
        
        assert isinstance(calm_summary, str)
        assert isinstance(assertive_summary, str)
        assert len(calm_summary) > 0
        assert len(assertive_summary) > 0

    def test_generate_negotiation_summary_uses_neutral_phrasing(self):
        """Test that generate_negotiation_summary uses neutral phrasing."""
        service = ExportService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        summary = service.generate_negotiation_summary(agreement, "calm")
        
        # Should not contain emotionally charged terms
        assert "Above average" not in summary
        assert "Below average" not in summary
        assert "Excessive" not in summary
        assert "Too high" not in summary
        assert "Too low" not in summary

    def test_generate_negotiation_summary_includes_legal_context(self):
        """Test that generate_negotiation_summary includes legal context."""
        service = ExportService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        summary = service.generate_negotiation_summary(agreement, "calm")
        
        # Should include legal context
        assert "Legal max increase" in summary or "legal" in summary.lower()

    def test_data_source_disclosure_format(self):
        """Test that data source disclosure has correct format."""
        service = ExportService()
        
        content = "Test"
        result = service.add_data_source_disclosure(content)
        
        # Should end with the disclosure
        assert result.endswith("Data source: TCMB (exchange rates), TÜFE (inflation)")
        
        # Should have proper formatting (newline before disclosure)
        lines = result.split('\n')
        assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in lines[-1]
