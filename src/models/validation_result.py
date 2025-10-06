"""
ValidationResult DTO for representing the result of TÜFE data validation.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Data Transfer Object for TÜFE data validation results."""
    
    valid: bool
    quality_score: float  # 0.0-1.0
    warnings: List[str] = None
    errors: List[str] = None
    validation_details: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize the validation result."""
        if self.warnings is None:
            self.warnings = []
        
        if self.errors is None:
            self.errors = []
        
        if self.validation_details is None:
            self.validation_details = {}
        
        # Ensure quality score is within bounds
        if not (0.0 <= self.quality_score <= 1.0):
            raise ValueError("quality_score must be between 0.0 and 1.0")
    
    def to_dict(self) -> dict:
        """Convert the validation result to a dictionary."""
        return {
            'valid': self.valid,
            'quality_score': self.quality_score,
            'warnings': self.warnings,
            'errors': self.errors,
            'validation_details': self.validation_details
        }
    
    def add_warning(self, warning: str):
        """Add a validation warning."""
        if warning and warning not in self.warnings:
            self.warnings.append(warning)
    
    def add_error(self, error: str):
        """Add a validation error."""
        if error and error not in self.errors:
            self.errors.append(error)
    
    def add_validation_detail(self, key: str, value: Any):
        """Add a validation detail."""
        self.validation_details[key] = value
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def is_high_quality(self) -> bool:
        """Check if the data is high quality (score > 0.8)."""
        return self.quality_score > 0.8
    
    def is_medium_quality(self) -> bool:
        """Check if the data is medium quality (score 0.5-0.8)."""
        return 0.5 <= self.quality_score <= 0.8
    
    def is_low_quality(self) -> bool:
        """Check if the data is low quality (score < 0.5)."""
        return self.quality_score < 0.5
    
    def get_quality_level(self) -> str:
        """Get the quality level as a string."""
        if self.is_high_quality():
            return "high"
        elif self.is_medium_quality():
            return "medium"
        else:
            return "low"
    
    def get_summary(self) -> str:
        """Get a summary of the validation result."""
        quality_level = self.get_quality_level()
        status = "Valid" if self.valid else "Invalid"
        
        summary_parts = [f"{status} ({quality_level} quality)"]
        
        if self.has_errors():
            summary_parts.append(f"{len(self.errors)} errors")
        
        if self.has_warnings():
            summary_parts.append(f"{len(self.warnings)} warnings")
        
        return ", ".join(summary_parts)
    
    def __str__(self) -> str:
        """String representation of the validation result."""
        return f"ValidationResult({self.get_summary()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the validation result."""
        return (f"ValidationResult(valid={self.valid}, "
                f"quality_score={self.quality_score}, "
                f"warnings_count={len(self.warnings)}, "
                f"errors_count={len(self.errors)})")
