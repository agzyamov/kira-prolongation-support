"""
Integration test for legal rule determination.
Tests the complete flow of determining legal rules for different dates.
"""

import pytest
from datetime import datetime
from src.services.calculation_service import CalculationService
from src.services.legal_rule_service import LegalRuleService
from src.models.rental_agreement import RentalAgreement
from decimal import Decimal


class TestLegalRuleDetermination:
    """Integration tests for legal rule determination."""

    def test_legal_rule_determination_flow(self):
        """Test the complete flow of legal rule determination."""
        calculation_service = CalculationService()
        legal_rule_service = LegalRuleService()
        
        # Test pre-July 2024 date
        pre_july_date = datetime(2024, 6, 30)
        
        # Get rule from calculation service
        rule_type = calculation_service.get_legal_rule_for_date(pre_july_date)
        assert rule_type == "25%_cap"
        
        # Get rule from legal rule service
        rule = legal_rule_service.get_applicable_rule(pre_july_date)
        assert rule.rule_type == "25%_cap"
        
        # Verify consistency
        assert rule_type == rule.rule_type

    def test_legal_rule_determination_post_july_2024(self):
        """Test legal rule determination for post-July 2024 dates."""
        calculation_service = CalculationService()
        legal_rule_service = LegalRuleService()
        
        # Test post-July 2024 date
        post_july_date = datetime(2024, 7, 1)
        
        # Get rule from calculation service
        rule_type = calculation_service.get_legal_rule_for_date(post_july_date)
        assert rule_type == "cpi_based"
        
        # Get rule from legal rule service
        rule = legal_rule_service.get_applicable_rule(post_july_date)
        assert rule.rule_type == "cpi_based"
        
        # Verify consistency
        assert rule_type == rule.rule_type

    def test_legal_rule_labels_consistency(self):
        """Test that legal rule labels are consistent across services."""
        calculation_service = CalculationService()
        legal_rule_service = LegalRuleService()
        
        # Test pre-July 2024
        pre_july_date = datetime(2024, 6, 30)
        
        calc_label = calculation_service.get_legal_rule_label(pre_july_date)
        rule = legal_rule_service.get_applicable_rule(pre_july_date)
        
        assert "+25% (limit until July 2024)" in calc_label
        assert "+25% (limit until July 2024)" in rule.label
        
        # Test post-July 2024
        post_july_date = datetime(2024, 7, 1)
        
        calc_label = calculation_service.get_legal_rule_label(post_july_date)
        rule = legal_rule_service.get_applicable_rule(post_july_date)
        
        assert "+CPI (Yearly TÜFE)" in calc_label
        assert "+CPI (Yearly TÜFE)" in rule.label

    def test_legal_max_increase_calculation(self):
        """Test legal maximum increase calculation with different rules."""
        calculation_service = CalculationService()
        
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        # Test 25% cap calculation
        pre_july_date = datetime(2024, 6, 30)
        pre_july_increase = calculation_service.calculate_legal_max_increase(agreement, pre_july_date)
        
        # Should be 25% of base amount
        expected_increase = agreement.base_amount_tl * Decimal("0.25")
        assert pre_july_increase == expected_increase
        
        # Test CPI-based calculation (should be different)
        post_july_date = datetime(2024, 7, 1)
        post_july_increase = calculation_service.calculate_legal_max_increase(agreement, post_july_date)
        
        # Should be different from 25% cap (unless CPI happens to be 25%)
        # Note: This test assumes CPI is not exactly 25%
        assert isinstance(post_july_increase, Decimal)
        assert post_july_increase > 0

    def test_edge_case_july_1_2024(self):
        """Test edge case for exactly July 1, 2024."""
        calculation_service = CalculationService()
        legal_rule_service = LegalRuleService()
        
        # Test exactly July 1, 2024
        july_1_date = datetime(2024, 7, 1)
        
        # Should use CPI-based rule
        rule_type = calculation_service.get_legal_rule_for_date(july_1_date)
        assert rule_type == "cpi_based"
        
        rule = legal_rule_service.get_applicable_rule(july_1_date)
        assert rule.rule_type == "cpi_based"
        
        label = calculation_service.get_legal_rule_label(july_1_date)
        assert "+CPI (Yearly TÜFE)" in label

    def test_agreement_with_multiple_periods(self):
        """Test agreement spanning both pre and post July 2024 periods."""
        calculation_service = CalculationService()
        
        # Agreement spanning both periods
        agreement = RentalAgreement(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            base_amount_tl=Decimal("10000.00")
        )
        
        # Test different dates within the agreement
        dates_to_test = [
            datetime(2024, 3, 15),  # Pre-July
            datetime(2024, 6, 30),  # Last day of 25% cap
            datetime(2024, 7, 1),   # First day of CPI-based
            datetime(2024, 9, 15),  # Post-July
        ]
        
        for date in dates_to_test:
            rule_type = calculation_service.get_legal_rule_for_date(date)
            max_increase = calculation_service.calculate_legal_max_increase(agreement, date)
            
            if date <= datetime(2024, 6, 30):
                assert rule_type == "25%_cap"
            else:
                assert rule_type == "cpi_based"
            
            assert isinstance(max_increase, Decimal)
            assert max_increase > 0
