"""
Contract tests for LegalRuleService.
Tests the service interface before implementation.
"""

import pytest
from datetime import datetime, date
from src.services.legal_rule_service import LegalRuleService
from src.models.legal_rule import LegalRule


class TestLegalRuleService:
    """Contract tests for LegalRuleService."""

    def test_get_applicable_rule_returns_legal_rule(self):
        """Test that get_applicable_rule returns a LegalRule object."""
        service = LegalRuleService()
        
        # Test with date before July 1, 2024
        test_date = datetime(2024, 6, 30)
        rule = service.get_applicable_rule(test_date)
        assert isinstance(rule, LegalRule)
        assert rule.rule_type == "25%_cap"

    def test_get_applicable_rule_handles_post_july_2024(self):
        """Test that get_applicable_rule handles dates after July 1, 2024."""
        service = LegalRuleService()
        
        # Test with date after July 1, 2024
        test_date = datetime(2024, 7, 1)
        rule = service.get_applicable_rule(test_date)
        assert isinstance(rule, LegalRule)
        assert rule.rule_type == "cpi_based"

    def test_get_all_rules_returns_list(self):
        """Test that get_all_rules returns a list of LegalRule objects."""
        service = LegalRuleService()
        rules = service.get_all_rules()
        assert isinstance(rules, list)
        assert all(isinstance(rule, LegalRule) for rule in rules)
        assert len(rules) >= 2  # Should have at least 25% cap and CPI-based rules

    def test_initialize_default_rules_creates_rules(self):
        """Test that initialize_default_rules creates default rules."""
        service = LegalRuleService()
        service.initialize_default_rules()
        
        rules = service.get_all_rules()
        rule_types = [rule.rule_type for rule in rules]
        assert "25%_cap" in rule_types
        assert "cpi_based" in rule_types

    def test_rule_effective_dates(self):
        """Test that rules have correct effective dates."""
        service = LegalRuleService()
        rules = service.get_all_rules()
        
        for rule in rules:
            assert isinstance(rule.effective_start, date)
            if rule.effective_end:
                assert isinstance(rule.effective_end, date)
                assert rule.effective_start <= rule.effective_end

    def test_rule_labels_are_non_empty(self):
        """Test that all rules have non-empty labels."""
        service = LegalRuleService()
        rules = service.get_all_rules()
        
        for rule in rules:
            assert isinstance(rule.label, str)
            assert len(rule.label.strip()) > 0
