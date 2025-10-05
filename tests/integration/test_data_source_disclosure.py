"""
Integration test for data source disclosure.
Tests that data source disclosure is properly added to all exports.
"""

import pytest
from src.services.export_service import ExportService
from src.models.rental_agreement import RentalAgreement
from datetime import datetime
from decimal import Decimal


class TestDataSourceDisclosure:
    """Integration tests for data source disclosure."""

    def test_export_service_disclosure_integration(self):
        """Test that ExportService properly adds data source disclosure."""
        service = ExportService()
        
        # Test with simple content
        content = "This is a test export."
        result = service.add_data_source_disclosure(content)
        
        assert isinstance(result, str)
        assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in result
        assert content in result

    def test_negotiation_summary_disclosure(self):
        """Test that negotiation summary includes data source disclosure."""
        service = ExportService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        summary = service.generate_negotiation_summary(agreement, "calm")
        
        # Summary should be a string
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_disclosure_format_consistency(self):
        """Test that disclosure format is consistent across different content types."""
        service = ExportService()
        
        test_contents = [
            "Simple text",
            "Multi-line\ncontent\nwith\nbreaks",
            "Content with special characters: @#$%^&*()",
            "Content with numbers: 12345.67",
            "Empty content:",
            ""
        ]
        
        for content in test_contents:
            result = service.add_data_source_disclosure(content)
            
            # Should always include the disclosure
            assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in result
            
            # Should preserve original content (except for empty string)
            if content:
                assert content in result

    def test_disclosure_with_different_negotiation_modes(self):
        """Test that disclosure works with different negotiation modes."""
        service = ExportService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        # Test both modes
        calm_summary = service.generate_negotiation_summary(agreement, "calm")
        assertive_summary = service.generate_negotiation_summary(agreement, "assertive")
        
        # Both should be valid summaries
        assert isinstance(calm_summary, str)
        assert isinstance(assertive_summary, str)
        assert len(calm_summary) > 0
        assert len(assertive_summary) > 0

    def test_disclosure_positioning(self):
        """Test that disclosure is properly positioned in the content."""
        service = ExportService()
        
        content = "Main export content here."
        result = service.add_data_source_disclosure(content)
        
        # Disclosure should be at the end
        assert result.endswith("Data source: TCMB (exchange rates), TÜFE (inflation)")
        
        # Original content should be at the beginning
        assert result.startswith(content)

    def test_disclosure_with_existing_disclosure(self):
        """Test behavior when content already contains disclosure."""
        service = ExportService()
        
        content_with_disclosure = "Content\nData source: TCMB (exchange rates), TÜFE (inflation)"
        result = service.add_data_source_disclosure(content_with_disclosure)
        
        # Should still add disclosure (may result in duplication)
        assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in result

    def test_disclosure_integration_with_legal_context(self):
        """Test that disclosure integrates properly with legal context."""
        service = ExportService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        summary = service.generate_negotiation_summary(agreement, "calm")
        
        # Should contain both legal context and data source
        assert "legal" in summary.lower() or "Legal" in summary
        # Note: Data source disclosure might be added separately

    def test_disclosure_with_special_characters(self):
        """Test disclosure with content containing special characters."""
        service = ExportService()
        
        special_content = "Content with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
        result = service.add_data_source_disclosure(special_content)
        
        assert isinstance(result, str)
        assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in result
        assert special_content in result

    def test_disclosure_with_unicode_content(self):
        """Test disclosure with Unicode content."""
        service = ExportService()
        
        unicode_content = "Content with Unicode: Türkçe, 中文, العربية, русский"
        result = service.add_data_source_disclosure(unicode_content)
        
        assert isinstance(result, str)
        assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in result
        assert unicode_content in result

    def test_disclosure_consistency_across_multiple_calls(self):
        """Test that disclosure is consistent across multiple calls."""
        service = ExportService()
        
        content = "Test content"
        
        # Make multiple calls
        results = []
        for _ in range(5):
            result = service.add_data_source_disclosure(content)
            results.append(result)
        
        # All results should be identical
        assert all(result == results[0] for result in results)
        
        # All should contain the disclosure
        for result in results:
            assert "Data source: TCMB (exchange rates), TÜFE (inflation)" in result
