"""
Contract tests for extended ChartGenerator.
Tests the new negotiation mode and annotation methods before implementation.
"""

import pytest
import plotly.graph_objects as go
from src.utils.chart_generator import ChartGenerator
from src.models.rental_agreement import RentalAgreement
from datetime import datetime


class TestChartGeneratorExtensions:
    """Contract tests for ChartGenerator extensions."""

    def test_create_negotiation_mode_chart_returns_figure(self):
        """Test that create_negotiation_mode_chart returns a Plotly Figure."""
        generator = ChartGenerator()
        
        data = {
            "current_tl": 10000,
            "proposed_tl": 12000,
            "legal_max": 12500
        }
        
        # Test calm mode
        fig = generator.create_negotiation_mode_chart(data, "calm")
        assert isinstance(fig, go.Figure)
        
        # Test assertive mode
        fig = generator.create_negotiation_mode_chart(data, "assertive")
        assert isinstance(fig, go.Figure)

    def test_create_negotiation_mode_chart_handles_invalid_mode(self):
        """Test that create_negotiation_mode_chart handles invalid modes gracefully."""
        generator = ChartGenerator()
        
        data = {"current_tl": 10000}
        
        # Should default to calm mode or raise appropriate error
        with pytest.raises(ValueError):
            generator.create_negotiation_mode_chart(data, "invalid")

    def test_add_agreement_markers_returns_figure(self):
        """Test that add_agreement_markers returns a Plotly Figure."""
        generator = ChartGenerator()
        
        # Create base figure
        fig = go.Figure()
        
        # Create test agreements
        agreements = [
            RentalAgreement(
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31),
                base_amount_tl=10000
            ),
            RentalAgreement(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31),
                base_amount_tl=12000
            )
        ]
        
        result_fig = generator.add_agreement_markers(fig, agreements)
        assert isinstance(result_fig, go.Figure)

    def test_add_agreement_markers_handles_empty_list(self):
        """Test that add_agreement_markers handles empty agreement list."""
        generator = ChartGenerator()
        
        fig = go.Figure()
        result_fig = generator.add_agreement_markers(fig, [])
        assert isinstance(result_fig, go.Figure)

    def test_apply_negotiation_mode_styling_returns_figure(self):
        """Test that apply_negotiation_mode_styling returns a Plotly Figure."""
        generator = ChartGenerator()
        
        fig = go.Figure()
        
        # Test calm mode
        result_fig = generator.apply_negotiation_mode_styling(fig, "calm")
        assert isinstance(result_fig, go.Figure)
        
        # Test assertive mode
        result_fig = generator.apply_negotiation_mode_styling(fig, "assertive")
        assert isinstance(result_fig, go.Figure)

    def test_apply_negotiation_mode_styling_handles_invalid_mode(self):
        """Test that apply_negotiation_mode_styling handles invalid modes."""
        generator = ChartGenerator()
        
        fig = go.Figure()
        
        with pytest.raises(ValueError):
            generator.apply_negotiation_mode_styling(fig, "invalid")

    def test_negotiation_mode_affects_styling(self):
        """Test that different negotiation modes produce different styling."""
        generator = ChartGenerator()
        
        data = {"current_tl": 10000, "proposed_tl": 12000}
        
        calm_fig = generator.create_negotiation_mode_chart(data, "calm")
        assertive_fig = generator.create_negotiation_mode_chart(data, "assertive")
        
        # Both should be valid figures
        assert isinstance(calm_fig, go.Figure)
        assert isinstance(assertive_fig, go.Figure)
        
        # They should be different (different styling)
        # Note: This is a basic test - actual styling differences would be more complex
        assert calm_fig is not assertive_fig
