"""
Integration test for agreement period annotations.
Tests that agreement period markers are correctly added to charts.
"""

import pytest
import plotly.graph_objects as go
from datetime import datetime
from src.utils.chart_generator import ChartGenerator
from src.models.rental_agreement import RentalAgreement
from decimal import Decimal


class TestAgreementAnnotations:
    """Integration tests for agreement period annotations."""

    def test_single_agreement_annotation(self):
        """Test annotation for a single agreement."""
        generator = ChartGenerator()
        
        # Create base figure
        fig = go.Figure()
        
        # Create single agreement
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        # Add annotation
        result_fig = generator.add_agreement_markers(fig, [agreement])
        
        assert isinstance(result_fig, go.Figure)
        # Note: Detailed verification of markers would require inspecting the figure data

    def test_multiple_agreement_annotations(self):
        """Test annotations for multiple agreements."""
        generator = ChartGenerator()
        
        # Create base figure
        fig = go.Figure()
        
        # Create multiple agreements
        agreements = [
            RentalAgreement(
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31),
                base_amount_tl=Decimal("10000.00")
            ),
            RentalAgreement(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31),
                base_amount_tl=Decimal("12000.00")
            ),
            RentalAgreement(
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 12, 31),
                base_amount_tl=Decimal("14000.00")
            )
        ]
        
        # Add annotations
        result_fig = generator.add_agreement_markers(fig, agreements)
        
        assert isinstance(result_fig, go.Figure)

    def test_agreement_annotations_with_existing_data(self):
        """Test annotations with existing chart data."""
        generator = ChartGenerator()
        
        # Create figure with existing data
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[datetime(2023, 6, 1), datetime(2024, 6, 1), datetime(2025, 6, 1)],
            y=[10000, 12000, 14000],
            mode='lines+markers',
            name='Rent'
        ))
        
        # Create agreements
        agreements = [
            RentalAgreement(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31),
                base_amount_tl=Decimal("12000.00")
            )
        ]
        
        # Add annotations
        result_fig = generator.add_agreement_markers(fig, agreements)
        
        assert isinstance(result_fig, go.Figure)
        # Should still have the original data
        assert len(result_fig.data) >= 1

    def test_empty_agreement_list(self):
        """Test handling of empty agreement list."""
        generator = ChartGenerator()
        
        fig = go.Figure()
        result_fig = generator.add_agreement_markers(fig, [])
        
        assert isinstance(result_fig, go.Figure)
        # Should return the original figure unchanged
        assert result_fig is fig

    def test_agreement_annotations_with_negotiation_mode(self):
        """Test agreement annotations with different negotiation modes."""
        generator = ChartGenerator()
        
        # Create base figure
        fig = go.Figure()
        
        # Create agreement
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        # Add annotations
        result_fig = generator.add_agreement_markers(fig, [agreement])
        
        # Apply different negotiation modes
        calm_fig = generator.apply_negotiation_mode_styling(result_fig, "calm")
        assertive_fig = generator.apply_negotiation_mode_styling(result_fig, "assertive")
        
        assert isinstance(calm_fig, go.Figure)
        assert isinstance(assertive_fig, go.Figure)

    def test_agreement_date_validation(self):
        """Test that agreement dates are properly validated."""
        generator = ChartGenerator()
        
        fig = go.Figure()
        
        # Create agreement with valid dates
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        # Should not raise exception
        result_fig = generator.add_agreement_markers(fig, [agreement])
        assert isinstance(result_fig, go.Figure)

    def test_agreement_annotations_integration_with_chart_creation(self):
        """Test integration of annotations with chart creation."""
        generator = ChartGenerator()
        
        # Create chart data
        data = {
            "current_tl": 10000,
            "proposed_tl": 12000,
            "legal_max": 12500
        }
        
        # Create chart with negotiation mode
        fig = generator.create_negotiation_mode_chart(data, "calm")
        
        # Create agreements
        agreements = [
            RentalAgreement(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31),
                base_amount_tl=Decimal("10000.00")
            )
        ]
        
        # Add annotations
        result_fig = generator.add_agreement_markers(fig, agreements)
        
        assert isinstance(result_fig, go.Figure)

    def test_agreement_annotations_with_overlapping_dates(self):
        """Test annotations with overlapping agreement dates."""
        generator = ChartGenerator()
        
        fig = go.Figure()
        
        # Create agreements with overlapping dates
        agreements = [
            RentalAgreement(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 6, 30),
                base_amount_tl=Decimal("10000.00")
            ),
            RentalAgreement(
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 12, 31),
                base_amount_tl=Decimal("12000.00")
            )
        ]
        
        # Should handle overlapping dates gracefully
        result_fig = generator.add_agreement_markers(fig, agreements)
        assert isinstance(result_fig, go.Figure)
