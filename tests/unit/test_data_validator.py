"""
Unit tests for DataValidator service.

Tests data validation functionality including TÜFE rate validation,
year/month validation, complete record validation, and batch validation.
"""

import pytest
from decimal import Decimal

from src.services.data_validator import DataValidator
from src.services.exceptions import TufeValidationError


class TestDataValidator:
    """Unit tests for DataValidator."""
    
    def test_initialization(self):
        """Test DataValidator initialization."""
        validator = DataValidator()
        
        assert validator.min_tufe_rate == 0.0
        assert validator.max_tufe_rate == 200.0
        assert validator.min_year == 2000
        assert validator.max_year == 2030
    
    def test_initialization_custom_params(self):
        """Test DataValidator initialization with custom parameters."""
        validator = DataValidator(
            min_tufe_rate=1.0,
            max_tufe_rate=150.0,
            min_year=1990,
            max_year=2025
        )
        
        assert validator.min_tufe_rate == 1.0
        assert validator.max_tufe_rate == 150.0
        assert validator.min_year == 1990
        assert validator.max_year == 2025
    
    def test_validate_tufe_rate_valid(self):
        """Test validate_tufe_rate with valid rates."""
        validator = DataValidator()
        
        valid_rates = [0.0, 10.5, 50.0, 100.0, 200.0]
        
        for rate in valid_rates:
            # Should not raise exception
            validator.validate_tufe_rate(rate)
    
    def test_validate_tufe_rate_invalid_type(self):
        """Test validate_tufe_rate with invalid types."""
        validator = DataValidator()
        
        invalid_values = ["10.5", None, [], {}, True]
        
        for value in invalid_values:
            with pytest.raises(TufeValidationError, match="TÜFE rate must be a number"):
                validator.validate_tufe_rate(value)
    
    def test_validate_tufe_rate_too_low(self):
        """Test validate_tufe_rate with rates below minimum."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="TÜFE rate -1.0% is below minimum"):
            validator.validate_tufe_rate(-1.0)
    
    def test_validate_tufe_rate_too_high(self):
        """Test validate_tufe_rate with rates above maximum."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="TÜFE rate 201.0% is above maximum"):
            validator.validate_tufe_rate(201.0)
    
    def test_validate_tufe_rate_custom_bounds(self):
        """Test validate_tufe_rate with custom bounds."""
        validator = DataValidator(min_tufe_rate=5.0, max_tufe_rate=100.0)
        
        # Valid rates
        validator.validate_tufe_rate(5.0)
        validator.validate_tufe_rate(50.0)
        validator.validate_tufe_rate(100.0)
        
        # Invalid rates
        with pytest.raises(TufeValidationError):
            validator.validate_tufe_rate(4.9)
        
        with pytest.raises(TufeValidationError):
            validator.validate_tufe_rate(100.1)
    
    def test_validate_year_month_valid(self):
        """Test validate_year_month with valid combinations."""
        validator = DataValidator()
        
        valid_combinations = [
            (2000, 1), (2000, 6), (2000, 12),
            (2020, 1), (2020, 6), (2020, 12),
            (2030, 1), (2030, 6), (2030, 12)
        ]
        
        for year, month in valid_combinations:
            # Should not raise exception
            validator.validate_year_month(year, month)
    
    def test_validate_year_month_invalid_year_type(self):
        """Test validate_year_month with invalid year type."""
        validator = DataValidator()
        
        invalid_years = ["2020", None, [], {}, True]
        
        for year in invalid_years:
            with pytest.raises(TufeValidationError, match="Year must be an integer"):
                validator.validate_year_month(year, 1)
    
    def test_validate_year_month_invalid_month_type(self):
        """Test validate_year_month with invalid month type."""
        validator = DataValidator()
        
        invalid_months = ["1", None, [], {}, True]
        
        for month in invalid_months:
            with pytest.raises(TufeValidationError, match="Month must be an integer"):
                validator.validate_year_month(2020, month)
    
    def test_validate_year_month_year_too_low(self):
        """Test validate_year_month with year below minimum."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Year 1999 is below minimum"):
            validator.validate_year_month(1999, 1)
    
    def test_validate_year_month_year_too_high(self):
        """Test validate_year_month with year above maximum."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Year 2031 is above maximum"):
            validator.validate_year_month(2031, 1)
    
    def test_validate_year_month_month_too_low(self):
        """Test validate_year_month with month below 1."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Month 0 is below minimum"):
            validator.validate_year_month(2020, 0)
    
    def test_validate_year_month_month_too_high(self):
        """Test validate_year_month with month above 12."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Month 13 is above maximum"):
            validator.validate_year_month(2020, 13)
    
    def test_validate_year_month_custom_bounds(self):
        """Test validate_year_month with custom bounds."""
        validator = DataValidator(min_year=1990, max_year=2025)
        
        # Valid combinations
        validator.validate_year_month(1990, 1)
        validator.validate_year_month(2025, 12)
        
        # Invalid years
        with pytest.raises(TufeValidationError):
            validator.validate_year_month(1989, 1)
        
        with pytest.raises(TufeValidationError):
            validator.validate_year_month(2026, 1)
    
    def test_validate_complete_record_valid(self):
        """Test validate_complete_record with valid data."""
        validator = DataValidator()
        
        valid_records = [
            (2020, 1, 10.5, "OECD SDMX API"),
            (2021, 6, 25.0, "TCMB EVDS API"),
            (2022, 12, 50.0, "Manual Entry")
        ]
        
        for year, month, tufe_rate, source in valid_records:
            # Should not raise exception
            validator.validate_complete_record(year, month, tufe_rate, source)
    
    def test_validate_complete_record_invalid_year(self):
        """Test validate_complete_record with invalid year."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Year 1999 is below minimum"):
            validator.validate_complete_record(1999, 1, 10.5, "OECD SDMX API")
    
    def test_validate_complete_record_invalid_month(self):
        """Test validate_complete_record with invalid month."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Month 13 is above maximum"):
            validator.validate_complete_record(2020, 13, 10.5, "OECD SDMX API")
    
    def test_validate_complete_record_invalid_tufe_rate(self):
        """Test validate_complete_record with invalid TÜFE rate."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="TÜFE rate 201.0% is above maximum"):
            validator.validate_complete_record(2020, 1, 201.0, "OECD SDMX API")
    
    def test_validate_complete_record_empty_source(self):
        """Test validate_complete_record with empty source."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Data source cannot be empty"):
            validator.validate_complete_record(2020, 1, 10.5, "")
    
    def test_validate_complete_record_none_source(self):
        """Test validate_complete_record with None source."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Data source cannot be empty"):
            validator.validate_complete_record(2020, 1, 10.5, None)
    
    def test_validate_complete_record_whitespace_source(self):
        """Test validate_complete_record with whitespace-only source."""
        validator = DataValidator()
        
        with pytest.raises(TufeValidationError, match="Data source cannot be empty"):
            validator.validate_complete_record(2020, 1, 10.5, "   ")
    
    def test_validate_batch_data_valid(self):
        """Test validate_batch_data with valid data."""
        validator = DataValidator()
        
        valid_data = [
            {"year": 2020, "month": 1, "value": 10.5, "source": "OECD SDMX API"},
            {"year": 2021, "month": 6, "value": 25.0, "source": "TCMB EVDS API"},
            {"year": 2022, "month": 12, "value": 50.0, "source": "Manual Entry"}
        ]
        
        result = validator.validate_batch_data(valid_data)
        
        assert len(result) == 3
        assert result == valid_data
    
    def test_validate_batch_data_mixed_valid_invalid(self):
        """Test validate_batch_data with mixed valid and invalid data."""
        validator = DataValidator()
        
        mixed_data = [
            {"year": 2020, "month": 1, "value": 10.5, "source": "OECD SDMX API"},  # Valid
            {"year": 1999, "month": 1, "value": 10.5, "source": "OECD SDMX API"},  # Invalid year
            {"year": 2021, "month": 6, "value": 25.0, "source": "TCMB EVDS API"},  # Valid
            {"year": 2022, "month": 13, "value": 50.0, "source": "Manual Entry"},  # Invalid month
            {"year": 2023, "month": 12, "value": 50.0, "source": "OECD SDMX API"}  # Valid
        ]
        
        result = validator.validate_batch_data(mixed_data)
        
        # Should return only valid records
        assert len(result) == 3
        assert result[0]["year"] == 2020
        assert result[1]["year"] == 2021
        assert result[2]["year"] == 2023
    
    def test_validate_batch_data_empty_list(self):
        """Test validate_batch_data with empty list."""
        validator = DataValidator()
        
        result = validator.validate_batch_data([])
        
        assert result == []
    
    def test_validate_batch_data_all_invalid(self):
        """Test validate_batch_data with all invalid data."""
        validator = DataValidator()
        
        invalid_data = [
            {"year": 1999, "month": 1, "value": 10.5, "source": "OECD SDMX API"},  # Invalid year
            {"year": 2020, "month": 13, "value": 10.5, "source": "OECD SDMX API"},  # Invalid month
            {"year": 2021, "month": 1, "value": 201.0, "source": "OECD SDMX API"},  # Invalid rate
            {"year": 2022, "month": 1, "value": 10.5, "source": ""}  # Invalid source
        ]
        
        result = validator.validate_batch_data(invalid_data)
        
        assert result == []
    
    def test_validate_batch_data_missing_fields(self):
        """Test validate_batch_data with missing required fields."""
        validator = DataValidator()
        
        incomplete_data = [
            {"year": 2020, "month": 1, "value": 10.5},  # Missing source
            {"year": 2021, "month": 6, "value": 25.0, "source": "OECD SDMX API"},  # Valid
            {"year": 2022, "value": 50.0, "source": "Manual Entry"}  # Missing month
        ]
        
        result = validator.validate_batch_data(incomplete_data)
        
        # Should return only valid records
        assert len(result) == 1
        assert result[0]["year"] == 2021
    
    def test_validate_batch_data_wrong_field_names(self):
        """Test validate_batch_data with wrong field names."""
        validator = DataValidator()
        
        wrong_field_data = [
            {"year": 2020, "month": 1, "tufe_rate": 10.5, "source": "OECD SDMX API"},  # Wrong field name
            {"year": 2021, "month": 6, "value": 25.0, "source": "OECD SDMX API"}  # Valid
        ]
        
        result = validator.validate_batch_data(wrong_field_data)
        
        # Should return only valid records
        assert len(result) == 1
        assert result[0]["year"] == 2021
    
    def test_validate_batch_data_none_values(self):
        """Test validate_batch_data with None values."""
        validator = DataValidator()
        
        none_data = [
            {"year": None, "month": 1, "value": 10.5, "source": "OECD SDMX API"},  # None year
            {"year": 2021, "month": None, "value": 25.0, "source": "OECD SDMX API"},  # None month
            {"year": 2022, "month": 1, "value": None, "source": "OECD SDMX API"},  # None value
            {"year": 2023, "month": 1, "value": 50.0, "source": "OECD SDMX API"}  # Valid
        ]
        
        result = validator.validate_batch_data(none_data)
        
        # Should return only valid records
        assert len(result) == 1
        assert result[0]["year"] == 2023
    
    def test_validate_batch_data_decimal_values(self):
        """Test validate_batch_data with Decimal values."""
        validator = DataValidator()
        
        decimal_data = [
            {"year": 2020, "month": 1, "value": Decimal("10.5"), "source": "OECD SDMX API"},
            {"year": 2021, "month": 6, "value": Decimal("25.0"), "source": "TCMB EVDS API"}
        ]
        
        result = validator.validate_batch_data(decimal_data)
        
        assert len(result) == 2
        assert result == decimal_data
    
    def test_validate_batch_data_float_values(self):
        """Test validate_batch_data with float values."""
        validator = DataValidator()
        
        float_data = [
            {"year": 2020, "month": 1, "value": 10.5, "source": "OECD SDMX API"},
            {"year": 2021, "month": 6, "value": 25.0, "source": "TCMB EVDS API"}
        ]
        
        result = validator.validate_batch_data(float_data)
        
        assert len(result) == 2
        assert result == float_data
    
    def test_validate_batch_data_int_values(self):
        """Test validate_batch_data with int values."""
        validator = DataValidator()
        
        int_data = [
            {"year": 2020, "month": 1, "value": 10, "source": "OECD SDMX API"},
            {"year": 2021, "month": 6, "value": 25, "source": "TCMB EVDS API"}
        ]
        
        result = validator.validate_batch_data(int_data)
        
        assert len(result) == 2
        assert result == int_data
    
    def test_validate_batch_data_large_dataset(self):
        """Test validate_batch_data with large dataset."""
        validator = DataValidator()
        
        # Generate large dataset
        large_data = []
        for year in range(2020, 2025):
            for month in range(1, 13):
                large_data.append({
                    "year": year,
                    "month": month,
                    "value": 10.0 + (year - 2020) * 5.0,
                    "source": "OECD SDMX API"
                })
        
        result = validator.validate_batch_data(large_data)
        
        # Should return all valid records
        assert len(result) == len(large_data)
        assert result == large_data
    
    def test_validate_batch_data_performance(self):
        """Test validate_batch_data performance with large dataset."""
        validator = DataValidator()
        
        # Generate very large dataset
        large_data = []
        for year in range(2000, 2031):
            for month in range(1, 13):
                large_data.append({
                    "year": year,
                    "month": month,
                    "value": 10.0 + (year - 2000) * 0.5,
                    "source": "OECD SDMX API"
                })
        
        # Should complete in reasonable time
        result = validator.validate_batch_data(large_data)
        
        assert len(result) == len(large_data)
    
    def test_validate_batch_data_edge_cases(self):
        """Test validate_batch_data with edge cases."""
        validator = DataValidator()
        
        edge_case_data = [
            {"year": 2000, "month": 1, "value": 0.0, "source": "OECD SDMX API"},  # Minimum year, minimum rate
            {"year": 2030, "month": 12, "value": 200.0, "source": "OECD SDMX API"},  # Maximum year, maximum rate
            {"year": 2020, "month": 6, "value": 50.0, "source": "A"},  # Minimum source length
            {"year": 2021, "month": 6, "value": 50.0, "source": "A" * 100}  # Long source name
        ]
        
        result = validator.validate_batch_data(edge_case_data)
        
        assert len(result) == 4
        assert result == edge_case_data


if __name__ == "__main__":
    pytest.main([__file__])
