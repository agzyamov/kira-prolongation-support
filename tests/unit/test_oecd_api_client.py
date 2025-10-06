"""
Unit tests for OECDApiClient service.

Tests the OECD API client functionality including data fetching,
XML parsing, error handling, and rate limiting.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from src.services.oecd_api_client import OECDApiClient
from src.services.exceptions import TufeApiError, TufeValidationError


class TestOECDApiClient:
    """Unit tests for OECDApiClient."""
    
    def test_initialization_default_params(self):
        """Test OECDApiClient initialization with default parameters."""
        client = OECDApiClient()
        
        assert client.timeout == 30  # Default from config
        assert client.max_retries == 3  # Default from config
        assert client.base_url is not None
        assert client.namespaces is not None
    
    def test_initialization_custom_params(self):
        """Test OECDApiClient initialization with custom parameters."""
        client = OECDApiClient(timeout=60, max_retries=5)
        
        assert client.timeout == 60
        assert client.max_retries == 5
    
    def test_fetch_tufe_data_success(self):
        """Test successful TÜFE data fetching."""
        client = OECDApiClient()
        
        # Mock successful response
        mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
        <message:MessageGroup xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">
            <generic:DataSet xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
                <generic:Series>
                    <generic:Obs>
                        <generic:ObsKey>
                            <generic:Value id="TIME_PERIOD" value="2024-01"/>
                            <generic:Value id="REF_AREA" value="TUR"/>
                            <generic:Value id="MEASURE" value="CPI"/>
                            <generic:Value id="UNIT_MEASURE" value="PA"/>
                        </generic:ObsKey>
                        <generic:ObsValue value="42.5"/>
                    </generic:Obs>
                </generic:Series>
            </generic:DataSet>
        </message:MessageGroup>'''
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_xml_response
            mock_response.headers = {'Content-Type': 'application/xml'}
            mock_get.return_value = mock_response
            
            result = client.fetch_tufe_data(2024, 2024)
            
            assert isinstance(result, dict)
            assert 'items' in result
            assert 'source' in result
            assert 'fetch_time' in result
            assert 'year_range' in result
            assert 'total_items' in result
            assert result['source'] == 'OECD SDMX API'
            assert result['year_range'] == '2024-2024'
            assert result['total_items'] == 1
    
    def test_fetch_tufe_data_invalid_year_range(self):
        """Test TÜFE data fetching with invalid year range."""
        client = OECDApiClient()
        
        # Test start year > end year
        with pytest.raises(TufeValidationError):
            client.fetch_tufe_data(2025, 2024)
        
        # Test invalid start year
        with pytest.raises(TufeValidationError):
            client.fetch_tufe_data(1999, 2024)
        
        # Test invalid end year
        with pytest.raises(TufeValidationError):
            client.fetch_tufe_data(2024, 2030)
    
    def test_fetch_tufe_data_http_error(self):
        """Test TÜFE data fetching with HTTP error."""
        client = OECDApiClient()
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_response.headers = {}
            mock_get.return_value = mock_response
            
            with pytest.raises(TufeApiError) as exc_info:
                client.fetch_tufe_data(2024, 2024)
            
            assert "404" in str(exc_info.value)
    
    def test_fetch_tufe_data_network_error(self):
        """Test TÜFE data fetching with network error."""
        client = OECDApiClient()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            with pytest.raises(TufeApiError) as exc_info:
                client.fetch_tufe_data(2024, 2024)
            
            assert "Connection error" in str(exc_info.value)
    
    def test_fetch_tufe_data_timeout_error(self):
        """Test TÜFE data fetching with timeout error."""
        client = OECDApiClient()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            
            with pytest.raises(TufeApiError) as exc_info:
                client.fetch_tufe_data(2024, 2024)
            
            assert "timeout" in str(exc_info.value)
    
    def test_parse_sdmx_response_success(self):
        """Test successful SDMX response parsing."""
        client = OECDApiClient()
        
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <message:MessageGroup xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">
            <generic:DataSet xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
                <generic:Series>
                    <generic:Obs>
                        <generic:ObsKey>
                            <generic:Value id="TIME_PERIOD" value="2024-01"/>
                            <generic:Value id="REF_AREA" value="TUR"/>
                            <generic:Value id="MEASURE" value="CPI"/>
                            <generic:Value id="UNIT_MEASURE" value="PA"/>
                        </generic:ObsKey>
                        <generic:ObsValue value="42.5"/>
                    </generic:Obs>
                </generic:Series>
            </generic:DataSet>
        </message:MessageGroup>'''
        
        result = client.parse_sdmx_response(xml_content)
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        item = result[0]
        assert item['time_period'] == '2024-01'
        assert item['year'] == 2024
        assert item['month'] == 1
        assert item['value'] == 42.5
        assert item['country'] == 'TUR'
        assert item['measure'] == 'CPI'
        assert item['unit'] == 'PA'
    
    def test_parse_sdmx_response_invalid_xml(self):
        """Test SDMX response parsing with invalid XML."""
        client = OECDApiClient()
        
        invalid_xml = "This is not valid XML"
        
        with pytest.raises(TufeValidationError) as exc_info:
            client.parse_sdmx_response(invalid_xml)
        
        assert "Invalid XML" in str(exc_info.value)
    
    def test_parse_sdmx_response_no_turkey_data(self):
        """Test SDMX response parsing with no Turkey data."""
        client = OECDApiClient()
        
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <message:MessageGroup xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">
            <generic:DataSet xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
                <generic:Series>
                    <generic:Obs>
                        <generic:ObsKey>
                            <generic:Value id="TIME_PERIOD" value="2024-01"/>
                            <generic:Value id="REF_AREA" value="USA"/>
                            <generic:Value id="MEASURE" value="CPI"/>
                            <generic:Value id="UNIT_MEASURE" value="PA"/>
                        </generic:ObsKey>
                        <generic:ObsValue value="3.2"/>
                    </generic:Obs>
                </generic:Series>
            </generic:DataSet>
        </message:MessageGroup>'''
        
        result = client.parse_sdmx_response(xml_content)
        
        assert isinstance(result, list)
        assert len(result) == 0  # No Turkey data
    
    def test_validate_response_success(self):
        """Test successful response validation."""
        client = OECDApiClient()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/xml'}
        
        # Should not raise an exception
        client.validate_response(mock_response)
    
    def test_validate_response_http_error(self):
        """Test response validation with HTTP error."""
        client = OECDApiClient()
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}
        
        with pytest.raises(TufeApiError) as exc_info:
            client.validate_response(mock_response)
        
        assert "404" in str(exc_info.value)
    
    def test_validate_response_invalid_content_type(self):
        """Test response validation with invalid content type."""
        client = OECDApiClient()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        
        with pytest.raises(TufeApiError) as exc_info:
            client.validate_response(mock_response)
        
        assert "content type" in str(exc_info.value)
    
    def test_get_rate_limit_info_with_headers(self):
        """Test rate limit info extraction with headers."""
        client = OECDApiClient()
        
        mock_response = Mock()
        mock_response.headers = {
            'X-RateLimit-Remaining': '95',
            'X-RateLimit-Reset': '1640995200',
            'X-RateLimit-Limit': '100',
            'Retry-After': '60'
        }
        
        result = client.get_rate_limit_info(mock_response)
        
        assert isinstance(result, dict)
        assert result['remaining'] == '95'
        assert result['reset'] == '1640995200'
        assert result['limit'] == '100'
        assert result['retry_after'] == '60'
    
    def test_get_rate_limit_info_no_headers(self):
        """Test rate limit info extraction without headers."""
        client = OECDApiClient()
        
        mock_response = Mock()
        mock_response.headers = {}
        
        result = client.get_rate_limit_info(mock_response)
        
        assert isinstance(result, dict)
        assert result['remaining'] is None
        assert result['reset'] is None
        assert result['limit'] is None
        assert result['retry_after'] is None
    
    def test_is_healthy_success(self):
        """Test API health check success."""
        client = OECDApiClient()
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = client.is_healthy()
            
            assert result is True
    
    def test_is_healthy_failure(self):
        """Test API health check failure."""
        client = OECDApiClient()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            result = client.is_healthy()
            
            assert result is False
    
    def test_get_api_info(self):
        """Test API info retrieval."""
        client = OECDApiClient()
        
        result = client.get_api_info()
        
        assert isinstance(result, dict)
        assert 'base_url' in result
        assert 'timeout' in result
        assert 'max_retries' in result
        assert 'target_country' in result
        assert 'target_measure' in result
        assert 'target_unit' in result
    
    def test_retry_delay_calculation(self):
        """Test retry delay calculation."""
        client = OECDApiClient()
        
        # Test exponential backoff
        delay_0 = client._get_retry_delay(0)
        delay_1 = client._get_retry_delay(1)
        delay_2 = client._get_retry_delay(2)
        
        assert delay_0 < delay_1 < delay_2
        assert delay_0 > 0
        assert delay_1 > delay_0
        assert delay_2 > delay_1
    
    def test_jitter_addition(self):
        """Test jitter addition to delay."""
        client = OECDApiClient()
        
        base_delay = 1.0
        
        # Test multiple times to ensure jitter is applied
        jittered_delays = []
        for _ in range(10):
            jittered_delay = client._add_jitter(base_delay)
            jittered_delays.append(jittered_delay)
        
        # All delays should be positive
        for delay in jittered_delays:
            assert delay > 0
        
        # Should have some variation (not all the same)
        unique_delays = set(jittered_delays)
        assert len(unique_delays) > 1
    
    def test_fetch_tufe_data_retry_logic(self):
        """Test retry logic in fetch_tufe_data."""
        client = OECDApiClient(max_retries=2)
        
        with patch('requests.get') as mock_get:
            # First call fails, second call succeeds
            error_response = Mock()
            error_response.status_code = 500
            error_response.text = "Internal server error"
            error_response.headers = {}
            
            success_response = Mock()
            success_response.status_code = 200
            success_response.text = '''<?xml version="1.0" encoding="UTF-8"?>
            <message:MessageGroup xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">
                <generic:DataSet xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
                </generic:DataSet>
            </message:MessageGroup>'''
            success_response.headers = {'Content-Type': 'application/xml'}
            
            mock_get.side_effect = [error_response, success_response]
            
            result = client.fetch_tufe_data(2024, 2024)
            
            assert isinstance(result, dict)
            assert mock_get.call_count == 2  # Should have retried once
    
    def test_fetch_tufe_data_max_retries_exceeded(self):
        """Test fetch_tufe_data when max retries are exceeded."""
        client = OECDApiClient(max_retries=1)
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_response.headers = {}
            mock_get.return_value = mock_response
            
            with pytest.raises(TufeApiError) as exc_info:
                client.fetch_tufe_data(2024, 2024)
            
            assert "Failed after" in str(exc_info.value)
            assert mock_get.call_count == 2  # Initial call + 1 retry


if __name__ == "__main__":
    pytest.main([__file__])
