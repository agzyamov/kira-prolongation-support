"""
OECD API Client for TÜFE Data Fetching

This service provides a dedicated client for interacting with the OECD SDMX API
to fetch Turkish inflation (TÜFE) data with proper error handling and rate limiting.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from src.config.oecd_config import (
    OECD_FULL_ENDPOINT, RATE_LIMIT_CONFIG, SDMX_CONFIG, 
    ERROR_CONFIG, PERFORMANCE_CONFIG
)
from src.services.exceptions import TufeApiError, TufeValidationError


class OECDApiClient:
    """
    Client for OECD SDMX API integration.
    
    Provides methods to fetch TÜFE data from OECD API with proper error handling,
    rate limiting, and data validation.
    """
    
    def __init__(self, timeout: int = None, max_retries: int = None):
        """
        Initialize OECD API client.
        
        Args:
            timeout: Request timeout in seconds (default from config)
            max_retries: Maximum number of retry attempts (default from config)
        """
        self.timeout = timeout or RATE_LIMIT_CONFIG["timeout_seconds"]
        self.max_retries = max_retries or RATE_LIMIT_CONFIG["max_retries"]
        self.base_url = OECD_FULL_ENDPOINT
        self.namespaces = SDMX_CONFIG["namespaces"]
        
    def fetch_tufe_data(self, start_year: int, end_year: int) -> Dict[str, Any]:
        """
        Fetch TÜFE data from OECD API for specified year range.
        
        Args:
            start_year: Starting year (2000-2025)
            end_year: Ending year (2000-2025)
        
        Returns:
            Dictionary with raw API response data
        
        Raises:
            TufeApiError: If API request fails
            TufeValidationError: If response validation fails
        """
        # Validate input parameters
        if not (2000 <= start_year <= 2025):
            raise TufeValidationError(f"Invalid start_year: {start_year}. Must be between 2000 and 2025")
        if not (2000 <= end_year <= 2025):
            raise TufeValidationError(f"Invalid end_year: {end_year}. Must be between 2000 and 2025")
        if start_year > end_year:
            raise TufeValidationError(f"start_year ({start_year}) cannot be greater than end_year ({end_year})")
        
        # Construct API URL with date range
        start_date = f"{start_year}-01"
        end_date = f"{end_year}-12"
        url = f"{self.base_url}?startTime={start_date}&endTime={end_date}"
        
        # Make API request with retry logic
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout)
                
                # Validate response
                self.validate_response(response)
                
                # Parse and return data
                parsed_data = self.parse_sdmx_response(response.text)
                
                return {
                    'items': parsed_data,
                    'source': 'OECD SDMX API',
                    'fetch_time': datetime.now().isoformat(),
                    'year_range': f"{start_year}-{end_year}",
                    'total_items': len(parsed_data)
                }
                
            except requests.exceptions.Timeout as e:
                if attempt < self.max_retries:
                    time.sleep(self._get_retry_delay(attempt))
                    continue
                raise TufeApiError(f"Request timeout after {self.max_retries} retries: {e}")
                
            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries:
                    time.sleep(self._get_retry_delay(attempt))
                    continue
                raise TufeApiError(f"Connection error after {self.max_retries} retries: {e}")
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in ERROR_CONFIG["retryable_status_codes"] and attempt < self.max_retries:
                    time.sleep(self._get_retry_delay(attempt))
                    continue
                raise TufeApiError(f"HTTP error {e.response.status_code}: {e}")
                
            except Exception as e:
                raise TufeApiError(f"Unexpected error: {e}")
        
        raise TufeApiError(f"Failed after {self.max_retries} retries")
    
    def parse_sdmx_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Parse SDMX XML response into structured data.
        
        Args:
            xml_content: Raw XML response from OECD API
        
        Returns:
            List of dictionaries with parsed TÜFE data
        
        Raises:
            TufeValidationError: If XML parsing fails
        """
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise TufeValidationError(f"Invalid XML response: {e}")
        
        data_points = []
        
        # Find all observation elements
        for obs in root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs'):
            try:
                # Extract dimensions from ObsKey
                obs_key = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsKey')
                if obs_key is None:
                    continue
                
                dimensions = {}
                for value in obs_key.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value'):
                    dim_id = value.get('id')
                    dim_value = value.get('value')
                    if dim_id and dim_value:
                        dimensions[dim_id] = dim_value
                
                # Debug: Log dimensions for first few observations to understand the structure
                if len(data_points) < 3:
                    print(f"DEBUG: Observed dimensions: {dimensions}")
                
                # Check if this is Turkey annual CPI data (TÜFE - Yıllık % Değişim)
                # We want only the main Turkey CPI series, not sub-components
                if (dimensions.get('REF_AREA') == 'TUR' and 
                    dimensions.get('MEASURE') == 'CPALTT01' and
                    dimensions.get('FREQ') == 'M' and
                    dimensions.get('UNIT_MEASURE') == 'PA'):
                    
                    # Extract observation value
                    obs_value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                    if obs_value is not None:
                        value = obs_value.get('value')
                        if value:
                            try:
                                # Parse time period
                                time_period = dimensions.get('TIME_PERIOD', '')
                                if time_period and len(time_period) == 7:  # YYYY-MM format
                                    year = int(time_period[:4])
                                    month = int(time_period[5:7])
                                    
                                    data_points.append({
                                        'time_period': time_period,
                                        'year': year,
                                        'month': month,
                                        'value': float(value),
                                        'country': dimensions.get('REF_AREA'),
                                        'measure': dimensions.get('MEASURE'),
                                        'unit': dimensions.get('UNIT_MEASURE')
                                    })
                            except (ValueError, IndexError) as e:
                                # Skip invalid data points
                                continue
                                
            except Exception as e:
                # Skip problematic observations
                continue
        
        return data_points
    
    def validate_response(self, response: requests.Response) -> None:
        """
        Validate API response.
        
        Args:
            response: HTTP response object
        
        Raises:
            TufeApiError: If response is invalid
        """
        if response.status_code not in [200, 201]:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            
            if response.status_code in ERROR_CONFIG["retryable_status_codes"]:
                raise TufeApiError(f"Retryable error - {error_msg}")
            else:
                raise TufeApiError(f"Non-retryable error - {error_msg}")
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'xml' not in content_type.lower() and 'text' not in content_type.lower():
            raise TufeApiError(f"Unexpected content type: {content_type}")
    
    def get_rate_limit_info(self, response: requests.Response) -> Dict[str, Any]:
        """
        Extract rate limit information from response headers.
        
        Args:
            response: HTTP response object
        
        Returns:
            Dictionary with rate limit information
        """
        headers = response.headers
        
        return {
            'remaining': headers.get('X-RateLimit-Remaining'),
            'reset': headers.get('X-RateLimit-Reset'),
            'limit': headers.get('X-RateLimit-Limit'),
            'retry_after': headers.get('Retry-After')
        }
    
    def _get_retry_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt with exponential backoff.
        
        Args:
            attempt: Current attempt number (0-based)
        
        Returns:
            Delay in seconds
        """
        delay = RATE_LIMIT_CONFIG["base_delay_seconds"] * (RATE_LIMIT_CONFIG["backoff_factor"] ** attempt)
        return min(delay, RATE_LIMIT_CONFIG["max_delay_seconds"])
    
    def _add_jitter(self, delay: float) -> float:
        """
        Add randomization to delay to avoid thundering herd.
        
        Args:
            delay: Base delay in seconds
        
        Returns:
            Jittered delay in seconds
        """
        import random
        jitter_range = RATE_LIMIT_CONFIG["jitter_range"]
        jitter = random.uniform(-jitter_range, jitter_range)
        return delay * (1 + jitter)
    
    def is_healthy(self) -> bool:
        """
        Check if the OECD API is healthy by making a simple request.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Make a simple request to check API health
            test_url = f"{self.base_url}?startTime=2024-01&endTime=2024-01"
            response = requests.get(test_url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get information about the OECD API client.
        
        Returns:
            Dictionary with API client information
        """
        return {
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'target_country': SDMX_CONFIG["target_country"],
            'target_measure': SDMX_CONFIG["target_measure"],
            'target_unit': SDMX_CONFIG["target_unit"]
        }
