"""
Contract tests for extended CalculationService.
Tests the new legal rule methods before implementation.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from src.services.calculation_service import CalculationService
from src.models.rental_agreement import RentalAgreement


class TestCalculationServiceExtensions:
    """Contract tests for CalculationService extensions."""

    def test_get_legal_rule_for_date_returns_string(self):
        """Test that get_legal_rule_for_date returns a string."""
        service = CalculationService()
        
        # Test with date before July 1, 2024
        test_date = datetime(2024, 6, 30)
        rule = service.get_legal_rule_for_date(test_date)
        assert isinstance(rule, str)
        assert rule == "25%_cap"

    def test_get_legal_rule_for_date_handles_post_july_2024(self):
        """Test that get_legal_rule_for_date handles dates after July 1, 2024."""
        service = CalculationService()
        
        # Test with date after July 1, 2024
        test_date = datetime(2024, 7, 1)
        rule = service.get_legal_rule_for_date(test_date)
        assert isinstance(rule, str)
        assert rule == "cpi_based"

    def test_get_legal_rule_label_returns_string(self):
        """Test that get_legal_rule_label returns a human-readable string."""
        service = CalculationService()
        
        # Test with date before July 1, 2024
        test_date = datetime(2024, 6, 30)
        label = service.get_legal_rule_label(test_date)
        assert isinstance(label, str)
        assert "+25% (limit until July 2024)" in label

    def test_get_legal_rule_label_handles_post_july_2024(self):
        """Test that get_legal_rule_label handles dates after July 1, 2024."""
        service = CalculationService()
        
        # Test with date after July 1, 2024
        test_date = datetime(2024, 7, 1)
        label = service.get_legal_rule_label(test_date)
        assert isinstance(label, str)
        assert "+CPI (Yearly TÜFE)" in label

    def test_calculate_legal_max_increase_returns_decimal(self):
        """Test that calculate_legal_max_increase returns a Decimal."""
        service = CalculationService()
        
        # Create test agreement
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        test_date = datetime(2024, 6, 30)
        max_increase = service.calculate_legal_max_increase(agreement, test_date)
        assert isinstance(max_increase, Decimal)
        assert max_increase > 0

    def test_calculate_legal_max_increase_handles_different_dates(self):
        """Test that calculate_legal_max_increase handles different dates correctly."""
        service = CalculationService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        # Test 25% cap period
        pre_july_date = datetime(2024, 6, 30)
        pre_july_increase = service.calculate_legal_max_increase(agreement, pre_july_date)
        
        # Test CPI-based period
        post_july_date = datetime(2024, 7, 1)
        post_july_increase = service.calculate_legal_max_increase(agreement, post_july_date)
        
        # Both should be positive
        assert pre_july_increase > 0
        assert post_july_increase > 0

    def test_edge_case_july_1_2024(self):
        """Test edge case for exactly July 1, 2024."""
        service = CalculationService()
        
        # Test exactly July 1, 2024
        test_date = datetime(2024, 7, 1)
        rule = service.get_legal_rule_for_date(test_date)
        assert rule == "cpi_based"
        
        label = service.get_legal_rule_label(test_date)
        assert "+CPI (Yearly TÜFE)" in label
