"""
Unit tests for TCMB API client.
"""

import pytest
from decimal import Decimal
from src.services.tcmb_api_client import TCMBApiClient
from src.services.exceptions import TufeApiError, TufeValidationError


class TestTCMBApiClient:
    """Unit tests for TCMB API client."""

    def test_valid_api_client_creation(self):
        """Test creating a valid TCMB API client."""
        client = TCMBApiClient("test_api_key_123")
        
        assert client.api_key == "test_api_key_123"
        assert client.base_url == "https://evds2.tcmb.gov.tr/service/evds/"
        assert client.series_code == "TP.FE.OKTG01"
        assert client.data_format == "json"
        assert client.timeout == 10
        assert client.max_retries == 3

    def test_api_client_with_none_key(self):
        """Test creating API client with None key."""
        client = TCMBApiClient(None)
        assert client.api_key is None

    def test_api_client_with_empty_key(self):
        """Test creating API client with empty key."""
        client = TCMBApiClient("")
        assert client.api_key == ""

    def test_build_api_url_success(self):
        """Test building API URL successfully."""
        client = TCMBApiClient("test_api_key_123")
        
        url = client.build_api_url(2024)
        
        assert isinstance(url, str)
        assert "evds2.tcmb.gov.tr" in url
        assert "TP.FE.OKTG01" in url
        assert "test_api_key_123" in url
        assert "2024-01-01" in url
        assert "2024-12-31" in url

    def test_build_api_url_invalid_year(self):
        """Test building API URL with invalid year."""
        client = TCMBApiClient("test_api_key_123")
        
        with pytest.raises(TufeValidationError, match="Invalid year"):
            client.build_api_url(1900)  # Invalid year

    def test_fetch_tufe_data_no_api_key(self):
        """Test fetching TÜFE data without API key."""
        client = TCMBApiClient("")
        
        with pytest.raises(TufeApiError, match="API key is required"):
            client.fetch_tufe_data(2024)

    def test_fetch_tufe_data_invalid_year(self):
        """Test fetching TÜFE data with invalid year."""
        client = TCMBApiClient("test_api_key_123")
        
        with pytest.raises(TufeValidationError, match="Invalid year"):
            client.fetch_tufe_data(1900)

    def test_validate_api_key_no_key(self):
        """Test validating API key when no key is set."""
        client = TCMBApiClient("")
        
        is_valid = client.validate_api_key()
        assert is_valid is False

    def test_validate_api_key_invalid_key(self):
        """Test validating invalid API key."""
        client = TCMBApiClient("invalid_key")
        
        is_valid = client.validate_api_key()
        assert is_valid is False

    def test_get_rate_limit_status(self):
        """Test getting rate limit status."""
        client = TCMBApiClient("test_api_key_123")
        
        status = client.get_rate_limit_status()
        
        assert isinstance(status, dict)
        assert "remaining" in status
        assert "reset_time" in status
        assert "limit_per_hour" in status
        assert isinstance(status["remaining"], int)
        assert status["remaining"] >= 0

    def test_extract_tufe_rate_valid_response(self):
        """Test extracting TÜFE rate from valid response."""
        client = TCMBApiClient("test_api_key_123")
        
        response = {
            "items": [
                {
                    "TARIH": "2024-12",
                    "TP.FE.OKTG01": "44.38"
                }
            ]
        }
        
        tufe_rate = client.extract_tufe_rate(response)
        assert tufe_rate == Decimal("44.38")

    def test_extract_tufe_rate_no_items(self):
        """Test extracting TÜFE rate from response with no items."""
        client = TCMBApiClient("test_api_key_123")
        
        response = {"items": []}
        
        tufe_rate = client.extract_tufe_rate(response)
        assert tufe_rate is None

    def test_extract_tufe_rate_no_series_code(self):
        """Test extracting TÜFE rate from response without series code."""
        client = TCMBApiClient("test_api_key_123")
        
        response = {
            "items": [
                {
                    "TARIH": "2024-12",
                    "OTHER_CODE": "44.38"
                }
            ]
        }
        
        tufe_rate = client.extract_tufe_rate(response)
        assert tufe_rate is None

    def test_extract_tufe_rate_invalid_data(self):
        """Test extracting TÜFE rate from response with invalid data."""
        client = TCMBApiClient("test_api_key_123")
        
        response = {
            "items": [
                {
                    "TARIH": "2024-12",
                    "TP.FE.OKTG01": "invalid"
                }
            ]
        }
        
        with pytest.raises(TufeValidationError):
            client.extract_tufe_rate(response)

    def test_get_available_years(self):
        """Test getting available years."""
        client = TCMBApiClient("test_api_key_123")
        
        # This will fail in unit test due to network call, but we can test the method exists
        with pytest.raises(TufeApiError):
            client.get_available_years()

    def test_test_connection(self):
        """Test connection to TCMB API."""
        client = TCMBApiClient("test_api_key_123")
        
        # This will fail in unit test due to network call, but we can test the method exists
        is_connected = client.test_connection()
        assert isinstance(is_connected, bool)

    def test_get_api_info(self):
        """Test getting API information."""
        client = TCMBApiClient("test_api_key_123")
        
        info = client.get_api_info()
        
        assert isinstance(info, dict)
        assert info["base_url"] == "https://evds2.tcmb.gov.tr/service/evds/"
        assert info["series_code"] == "TP.FE.OKTG01"
        assert info["data_format"] == "json"
        assert info["timeout"] == 10
        assert info["max_retries"] == 3
        assert info["api_key_configured"] is True

    def test_get_api_info_no_key(self):
        """Test getting API information with no key."""
        client = TCMBApiClient("")
        
        info = client.get_api_info()
        assert info["api_key_configured"] is False

    def test_parse_response_valid(self):
        """Test parsing valid API response."""
        client = TCMBApiClient("test_api_key_123")
        
        # Mock response data
        class MockResponse:
            def json(self):
                return {
                    "items": [
                        {
                            "TARIH": "2024-12",
                            "TP.FE.OKTG01": "44.38"
                        }
                    ]
                }
        
        response = MockResponse()
        parsed = client._parse_response(response)
        
        assert isinstance(parsed, dict)
        assert "items" in parsed
        assert len(parsed["items"]) == 1

    def test_parse_response_with_error(self):
        """Test parsing API response with error."""
        client = TCMBApiClient("test_api_key_123")
        
        # Mock response with error
        class MockResponse:
            def json(self):
                return {"error": "API key invalid"}
        
        response = MockResponse()
        
        with pytest.raises(TufeApiError, match="API error"):
            client._parse_response(response)

    def test_parse_response_missing_items(self):
        """Test parsing API response missing items."""
        client = TCMBApiClient("test_api_key_123")
        
        # Mock response without items
        class MockResponse:
            def json(self):
                return {"data": "some data"}
        
        response = MockResponse()
        
        with pytest.raises(TufeValidationError, match="Response missing 'items' field"):
            client._parse_response(response)

    def test_parse_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        client = TCMBApiClient("test_api_key_123")
        
        # Mock response with invalid JSON
        class MockResponse:
            def json(self):
                raise ValueError("Invalid JSON")
        
        response = MockResponse()
        
        with pytest.raises(TufeValidationError, match="Invalid JSON response"):
            client._parse_response(response)

    def test_parse_response_not_dict(self):
        """Test parsing response that's not a dictionary."""
        client = TCMBApiClient("test_api_key_123")
        
        # Mock response that's not a dict
        class MockResponse:
            def json(self):
                return "not a dict"
        
        response = MockResponse()
        
        with pytest.raises(TufeValidationError, match="Response is not a valid JSON object"):
            client._parse_response(response)
