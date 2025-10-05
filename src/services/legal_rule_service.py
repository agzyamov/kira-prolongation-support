"""
LegalRuleService for managing legal rent increase rules.
"""

from datetime import datetime, date
from typing import List, Optional
from src.models.legal_rule import LegalRule
from src.services.exceptions import ServiceError
from src.storage.data_store import DataStore


class LegalRuleError(ServiceError):
    """Raised when legal rule cannot be determined."""
    pass


class LegalRuleService:
    """Service for managing legal rent increase rules."""
    
    def __init__(self, data_store: Optional[DataStore] = None):
        """
        Initialize the legal rule service.
        
        Args:
            data_store: DataStore instance for database operations
        """
        self.data_store = data_store or DataStore()
    
    def get_applicable_rule(self, check_date: date) -> LegalRule:
        """
        Get applicable legal rule for given date.
        
        Args:
            check_date: Date to check
            
        Returns:
            Applicable LegalRule object
            
        Raises:
            LegalRuleError: If no applicable rule is found
        """
        if not isinstance(check_date, date):
            raise ValueError("check_date must be a date object")
        
        # Get all rules from database
        rules = self.get_all_rules()
        
        # Find applicable rule
        for rule in rules:
            if rule.is_applicable_for_date(check_date):
                return rule
        
        # If no rule found, determine based on date
        if check_date <= date(2024, 6, 30):
            return LegalRule.create_25_percent_cap(
                effective_start=date(2020, 1, 1),
                effective_end=date(2024, 6, 30)
            )
        else:
            return LegalRule.create_cpi_based(
                effective_start=date(2024, 7, 1)
            )
    
    def get_all_rules(self) -> List[LegalRule]:
        """
        Get all legal rules from database.
        
        Returns:
            List of all LegalRule objects
        """
        try:
            # Try to get from database first
            rules = self.data_store.get_legal_rules()
            if rules:
                return rules
        except Exception:
            # If database fails, return default rules
            pass
        
        # Return default rules
        return [
            LegalRule.create_25_percent_cap(
                effective_start=date(2020, 1, 1),
                effective_end=date(2024, 6, 30)
            ),
            LegalRule.create_cpi_based(
                effective_start=date(2024, 7, 1)
            )
        ]
    
    def initialize_default_rules(self) -> None:
        """
        Initialize default legal rules in database.
        """
        try:
            # Check if rules already exist
            existing_rules = self.data_store.get_legal_rules()
            if existing_rules:
                return  # Rules already exist
            
            # Create default rules
            default_rules = [
                LegalRule.create_25_percent_cap(
                    effective_start=date(2020, 1, 1),
                    effective_end=date(2024, 6, 30)
                ),
                LegalRule.create_cpi_based(
                    effective_start=date(2024, 7, 1)
                )
            ]
            
            # Save to database
            for rule in default_rules:
                self.data_store.save_legal_rule(rule)
                
        except Exception as e:
            # If database operations fail, that's okay
            # The service will use default rules
            pass
    
    def get_rule_for_date(self, check_date: date) -> LegalRule:
        """
        Get rule for specific date (alias for get_applicable_rule).
        
        Args:
            check_date: Date to check
            
        Returns:
            Applicable LegalRule object
        """
        return self.get_applicable_rule(check_date)
    
    def is_25_percent_cap_period(self, check_date: date) -> bool:
        """
        Check if the given date falls within the 25% cap period.
        
        Args:
            check_date: Date to check
            
        Returns:
            True if date is within 25% cap period
        """
        rule = self.get_applicable_rule(check_date)
        return rule.is_25_percent_cap()
    
    def is_cpi_based_period(self, check_date: date) -> bool:
        """
        Check if the given date falls within the CPI-based period.
        
        Args:
            check_date: Date to check
            
        Returns:
            True if date is within CPI-based period
        """
        rule = self.get_applicable_rule(check_date)
        return rule.is_cpi_based()
    
    def get_rule_label(self, check_date: date) -> str:
        """
        Get human-readable label for rule applicable to given date.
        
        Args:
            check_date: Date to check
            
        Returns:
            Human-readable rule label
        """
        rule = self.get_applicable_rule(check_date)
        return rule.get_display_label()
