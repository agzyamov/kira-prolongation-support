"""
Tests for data validation utilities.
These tests should FAIL initially (TDD approach).
"""
import pytest
from decimal import Decimal
from datetime import date


class TestDateValidation:
    """Test date validation logic"""
    
    def test_validate_date_range_start_before_end(self):
        """Test valid date range where start < end"""
        # Arrange
        start_date = date(2022, 11, 1)
        end_date = date(2023, 10, 31)
        
        # Act
        from src.utils.validators import validate_date_range
        result = validate_date_range(start_date, end_date)
        
        # Assert
        assert result is True
    
    def test_validate_date_range_start_after_end_raises_error(self):
        """Test that start > end raises ValidationError"""
        # Arrange
        start_date = date(2023, 10, 31)
        end_date = date(2022, 11, 1)
        
        # Act & Assert
        from src.utils.validators import validate_date_range, ValidationError
        
        with pytest.raises(ValidationError):
            validate_date_range(start_date, end_date)
    
    def test_validate_date_range_same_date(self):
        """Test validation when start equals end"""
        # Arrange
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 1)
        
        # Act
        from src.utils.validators import validate_date_range
        result = validate_date_range(start_date, end_date)
        
        # Assert - same date should be valid
        assert result is True
    
    def test_validate_date_range_end_none_is_valid(self):
        """Test that end_date=None (ongoing) is valid"""
        # Arrange
        start_date = date(2024, 12, 1)
        end_date = None
        
        # Act
        from src.utils.validators import validate_date_range
        result = validate_date_range(start_date, end_date)
        
        # Assert
        assert result is True


class TestAmountValidation:
    """Test monetary amount validation"""
    
    def test_validate_amount_positive_is_valid(self):
        """Test that positive amount is valid"""
        # Arrange
        amount = Decimal("15000")
        
        # Act
        from src.utils.validators import validate_amount
        result = validate_amount(amount)
        
        # Assert
        assert result is True
    
    def test_validate_amount_zero_raises_error(self):
        """Test that zero amount raises ValidationError"""
        # Arrange
        amount = Decimal("0")
        
        # Act & Assert
        from src.utils.validators import validate_amount, ValidationError
        
        with pytest.raises(ValidationError):
            validate_amount(amount)
    
    def test_validate_amount_negative_raises_error(self):
        """Test that negative amount raises ValidationError"""
        # Arrange
        amount = Decimal("-1000")
        
        # Act & Assert
        from src.utils.validators import validate_amount, ValidationError
        
        with pytest.raises(ValidationError):
            validate_amount(amount)
    
    def test_validate_amount_very_large_is_valid(self):
        """Test that very large amount is valid"""
        # Arrange
        amount = Decimal("1000000")
        
        # Act
        from src.utils.validators import validate_amount
        result = validate_amount(amount)
        
        # Assert
        assert result is True


class TestExchangeRateValidation:
    """Test exchange rate validation"""
    
    def test_validate_exchange_rate_positive_is_valid(self):
        """Test that positive rate is valid"""
        # Arrange
        rate = Decimal("18.65")
        
        # Act
        from src.utils.validators import validate_exchange_rate
        result = validate_exchange_rate(rate)
        
        # Assert
        assert result is True
    
    def test_validate_exchange_rate_zero_raises_error(self):
        """Test that zero rate raises ValidationError"""
        # Arrange
        rate = Decimal("0")
        
        # Act & Assert
        from src.utils.validators import validate_exchange_rate, ValidationError
        
        with pytest.raises(ValidationError):
            validate_exchange_rate(rate)
    
    def test_validate_exchange_rate_negative_raises_error(self):
        """Test that negative rate raises ValidationError"""
        # Arrange
        rate = Decimal("-5.0")
        
        # Act & Assert
        from src.utils.validators import validate_exchange_rate, ValidationError
        
        with pytest.raises(ValidationError):
            validate_exchange_rate(rate)


class TestMonthYearValidation:
    """Test month and year validation"""
    
    def test_validate_month_valid_range(self):
        """Test valid months 1-12"""
        from src.utils.validators import validate_month
        
        for month in range(1, 13):
            assert validate_month(month) is True
    
    def test_validate_month_zero_raises_error(self):
        """Test that month 0 raises ValidationError"""
        from src.utils.validators import validate_month, ValidationError
        
        with pytest.raises(ValidationError):
            validate_month(0)
    
    def test_validate_month_13_raises_error(self):
        """Test that month 13 raises ValidationError"""
        from src.utils.validators import validate_month, ValidationError
        
        with pytest.raises(ValidationError):
            validate_month(13)
    
    def test_validate_month_negative_raises_error(self):
        """Test that negative month raises ValidationError"""
        from src.utils.validators import validate_month, ValidationError
        
        with pytest.raises(ValidationError):
            validate_month(-1)
    
    def test_validate_year_reasonable_range(self):
        """Test that reasonable years are valid"""
        from src.utils.validators import validate_year
        
        assert validate_year(2020) is True
        assert validate_year(2024) is True
        assert validate_year(2025) is True
    
    def test_validate_year_too_old_raises_error(self):
        """Test that very old year raises ValidationError"""
        from src.utils.validators import validate_year, ValidationError
        
        with pytest.raises(ValidationError):
            validate_year(1900)
    
    def test_validate_year_future_is_valid(self):
        """Test that near-future years are valid"""
        from src.utils.validators import validate_year
        
        assert validate_year(2030) is True


class TestConfidenceScoreValidation:
    """Test OCR confidence score validation"""
    
    def test_validate_confidence_valid_range(self):
        """Test valid confidence scores 0.0-1.0"""
        from src.utils.validators import validate_confidence
        
        assert validate_confidence(0.0) is True
        assert validate_confidence(0.5) is True
        assert validate_confidence(0.95) is True
        assert validate_confidence(1.0) is True
    
    def test_validate_confidence_below_zero_raises_error(self):
        """Test that confidence < 0 raises ValidationError"""
        from src.utils.validators import validate_confidence, ValidationError
        
        with pytest.raises(ValidationError):
            validate_confidence(-0.1)
    
    def test_validate_confidence_above_one_raises_error(self):
        """Test that confidence > 1 raises ValidationError"""
        from src.utils.validators import validate_confidence, ValidationError
        
        with pytest.raises(ValidationError):
            validate_confidence(1.5)


class TestValidationError:
    """Test ValidationError exception"""
    
    def test_validation_error_has_message(self):
        """Test that ValidationError carries a message"""
        from src.utils.validators import ValidationError
        
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
    
    def test_validation_error_is_exception(self):
        """Test that ValidationError is an Exception"""
        from src.utils.validators import ValidationError
        
        assert issubclass(ValidationError, Exception)

