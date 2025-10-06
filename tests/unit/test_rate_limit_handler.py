"""
Unit tests for RateLimitHandler service.

Tests the rate limiting functionality including retry logic,
exponential backoff, jitter, and rate limit detection.
"""

import pytest
from unittest.mock import Mock
import time

from src.services.rate_limit_handler import RateLimitHandler
from src.services.exceptions import TufeApiError


class TestRateLimitHandler:
    """Unit tests for RateLimitHandler."""
    
    def test_initialization_default_params(self):
        """Test RateLimitHandler initialization with default parameters."""
        handler = RateLimitHandler()
        
        assert handler.max_retries == 3  # Default from config
        assert handler.base_delay == 1.0  # Default from config
        assert handler.backoff_factor == 2.0  # Default from config
        assert handler.max_delay == 60.0  # Default from config
        assert handler.jitter_range == 0.25  # Default from config
    
    def test_initialization_custom_params(self):
        """Test RateLimitHandler initialization with custom parameters."""
        handler = RateLimitHandler(
            max_retries=5,
            base_delay=2.0,
            backoff_factor=3.0,
            max_delay=120.0,
            jitter_range=0.5
        )
        
        assert handler.max_retries == 5
        assert handler.base_delay == 2.0
        assert handler.backoff_factor == 3.0
        assert handler.max_delay == 120.0
        assert handler.jitter_range == 0.5
    
    def test_should_retry_retryable_errors(self):
        """Test should_retry with retryable HTTP status codes."""
        handler = RateLimitHandler()
        
        retryable_codes = [429, 500, 502, 503, 504]
        
        for status_code in retryable_codes:
            mock_response = Mock()
            mock_response.status_code = status_code
            
            assert handler.should_retry(0, mock_response) is True
    
    def test_should_retry_non_retryable_errors(self):
        """Test should_retry with non-retryable HTTP status codes."""
        handler = RateLimitHandler()
        
        non_retryable_codes = [400, 401, 403, 404]
        
        for status_code in non_retryable_codes:
            mock_response = Mock()
            mock_response.status_code = status_code
            
            assert handler.should_retry(0, mock_response) is False
    
    def test_should_retry_max_retries_exceeded(self):
        """Test should_retry when max retries are exceeded."""
        handler = RateLimitHandler(max_retries=2)
        
        mock_response = Mock()
        mock_response.status_code = 500  # Retryable error
        
        # Should allow retries up to max_retries
        assert handler.should_retry(0, mock_response) is True
        assert handler.should_retry(1, mock_response) is True
        
        # Should not allow retry beyond max_retries
        assert handler.should_retry(2, mock_response) is False
        assert handler.should_retry(3, mock_response) is False
    
    def test_get_delay_exponential_backoff(self):
        """Test get_delay with exponential backoff."""
        handler = RateLimitHandler(base_delay=1.0, backoff_factor=2.0)
        
        delay_0 = handler.get_delay(0)
        delay_1 = handler.get_delay(1)
        delay_2 = handler.get_delay(2)
        delay_3 = handler.get_delay(3)
        
        # Verify exponential backoff
        assert delay_0 == 1.0  # 1.0 * (2.0 ** 0)
        assert delay_1 == 2.0  # 1.0 * (2.0 ** 1)
        assert delay_2 == 4.0  # 1.0 * (2.0 ** 2)
        assert delay_3 == 8.0  # 1.0 * (2.0 ** 3)
        
        # Each attempt should have longer delay
        assert delay_0 < delay_1 < delay_2 < delay_3
    
    def test_get_delay_max_delay_respect(self):
        """Test get_delay respects maximum delay limit."""
        handler = RateLimitHandler(base_delay=1.0, backoff_factor=2.0, max_delay=10.0)
        
        # Test high attempt number
        delay = handler.get_delay(10)
        assert delay <= 10.0
        
        # Test very high attempt number
        delay = handler.get_delay(100)
        assert delay <= 10.0
    
    def test_add_jitter_randomization(self):
        """Test add_jitter adds appropriate randomization."""
        handler = RateLimitHandler(jitter_range=0.25)
        
        base_delay = 1.0
        jittered_delays = []
        
        # Test multiple times to ensure randomization
        for _ in range(100):
            jittered_delay = handler.add_jitter(base_delay)
            jittered_delays.append(jittered_delay)
        
        # All delays should be within jitter range
        min_expected = base_delay * (1 - 0.25)  # 0.75
        max_expected = base_delay * (1 + 0.25)  # 1.25
        
        for delay in jittered_delays:
            assert min_expected <= delay <= max_expected
        
        # Should have some variation (not all the same)
        unique_delays = set(jittered_delays)
        assert len(unique_delays) > 1
    
    def test_is_rate_limited_detection(self):
        """Test rate limit detection."""
        handler = RateLimitHandler()
        
        # Test 429 status code
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        assert handler.is_rate_limited(mock_response_429) is True
        
        # Test other status codes
        for status_code in [200, 400, 401, 403, 404, 500, 502, 503, 504]:
            mock_response = Mock()
            mock_response.status_code = status_code
            
            if status_code == 429:
                assert handler.is_rate_limited(mock_response) is True
            else:
                assert handler.is_rate_limited(mock_response) is False
    
    def test_get_retry_after_delay_with_header(self):
        """Test get_retry_after_delay with Retry-After header."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.headers = {'Retry-After': '60'}
        
        delay = handler.get_retry_after_delay(mock_response)
        
        assert delay == 60.0
    
    def test_get_retry_after_delay_without_header(self):
        """Test get_retry_after_delay without Retry-After header."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.headers = {}
        
        delay = handler.get_retry_after_delay(mock_response)
        
        assert delay is None
    
    def test_get_retry_after_delay_invalid_header(self):
        """Test get_retry_after_delay with invalid Retry-After header."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.headers = {'Retry-After': 'invalid'}
        
        delay = handler.get_retry_after_delay(mock_response)
        
        assert delay is None
    
    def test_update_rate_limit_info(self):
        """Test rate limit info update."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.headers = {
            'X-RateLimit-Remaining': '95',
            'X-RateLimit-Reset': '1640995200'
        }
        
        handler.update_rate_limit_info(mock_response)
        
        assert handler.rate_limit_remaining == 95
        assert handler.rate_limit_reset_time == 1640995200
        assert handler.request_count == 1
    
    def test_wait_for_rate_limit_reset_with_retry_after(self):
        """Test wait_for_rate_limit_reset with Retry-After header."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        
        wait_time = handler.wait_for_rate_limit_reset(mock_response)
        
        assert wait_time == 60.0
    
    def test_wait_for_rate_limit_reset_with_reset_header(self):
        """Test wait_for_rate_limit_reset with X-RateLimit-Reset header."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'X-RateLimit-Reset': str(int(time.time()) + 60)}
        
        wait_time = handler.wait_for_rate_limit_reset(mock_response)
        
        assert 0 <= wait_time <= 60.0
    
    def test_wait_for_rate_limit_reset_default_backoff(self):
        """Test wait_for_rate_limit_reset with default exponential backoff."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        
        wait_time = handler.wait_for_rate_limit_reset(mock_response)
        
        assert wait_time == handler.get_delay(0)
    
    def test_can_make_request_without_limits(self):
        """Test can_make_request without rate limits."""
        handler = RateLimitHandler()
        
        assert handler.can_make_request() is True
    
    def test_can_make_request_with_rate_limit_reset(self):
        """Test can_make_request with rate limit reset time."""
        handler = RateLimitHandler()
        
        # Set rate limit reset time in the future
        handler.rate_limit_reset_time = time.time() + 60
        
        assert handler.can_make_request() is False
    
    def test_can_make_request_with_rate_limit_remaining(self):
        """Test can_make_request with rate limit remaining."""
        handler = RateLimitHandler()
        
        # Set rate limit remaining to 0
        handler.rate_limit_remaining = 0
        
        assert handler.can_make_request() is False
    
    def test_get_rate_limit_status(self):
        """Test rate limit status retrieval."""
        handler = RateLimitHandler()
        
        status = handler.get_rate_limit_status()
        
        assert isinstance(status, dict)
        assert 'can_make_request' in status
        assert 'request_count' in status
        assert 'last_request_time' in status
        assert 'rate_limit_remaining' in status
        assert 'rate_limit_reset_time' in status
        assert 'time_until_reset' in status
    
    def test_reset_rate_limit_tracking(self):
        """Test rate limit tracking reset."""
        handler = RateLimitHandler()
        
        # Set some values
        handler.request_count = 5
        handler.last_request_time = time.time()
        handler.rate_limit_reset_time = time.time() + 60
        handler.rate_limit_remaining = 50
        
        # Reset tracking
        handler.reset_rate_limit_tracking()
        
        assert handler.request_count == 0
        assert handler.last_request_time == 0
        assert handler.rate_limit_reset_time == 0
        assert not hasattr(handler, 'rate_limit_remaining')
    
    def test_handle_rate_limit_response_success(self):
        """Test rate limit response handling."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        
        result = handler.handle_rate_limit_response(mock_response)
        
        assert isinstance(result, dict)
        assert result['should_retry'] is True
        assert result['delay'] == 60.0
        assert result['retry_after'] == 60.0
    
    def test_handle_rate_limit_response_non_rate_limited(self):
        """Test rate limit response handling for non-rate-limited response."""
        handler = RateLimitHandler()
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        result = handler.handle_rate_limit_response(mock_response)
        
        assert isinstance(result, dict)
        assert result['should_retry'] is False
        assert result['delay'] == 0
    
    def test_get_configuration(self):
        """Test configuration retrieval."""
        handler = RateLimitHandler(
            max_retries=5,
            base_delay=2.0,
            backoff_factor=3.0,
            max_delay=120.0,
            jitter_range=0.5
        )
        
        config = handler.get_configuration()
        
        assert isinstance(config, dict)
        assert config['max_retries'] == 5
        assert config['base_delay'] == 2.0
        assert config['backoff_factor'] == 3.0
        assert config['max_delay'] == 120.0
        assert config['jitter_range'] == 0.5
    
    def test_retry_flow_simulation(self):
        """Test complete retry flow simulation."""
        handler = RateLimitHandler(max_retries=3, base_delay=0.1)  # Fast for testing
        
        mock_response = Mock()
        mock_response.status_code = 500  # Retryable error
        
        # Simulate retry flow
        attempt = 0
        while handler.should_retry(attempt, mock_response):
            delay = handler.get_delay(attempt)
            jittered_delay = handler.add_jitter(delay)
            
            assert isinstance(delay, float)
            assert isinstance(jittered_delay, float)
            assert delay >= 0
            assert jittered_delay >= 0
            
            attempt += 1
        
        # Should have made exactly max_retries attempts
        assert attempt == 3
    
    def test_rate_limit_detection_flow(self):
        """Test rate limit detection and handling flow."""
        handler = RateLimitHandler()
        
        # Simulate rate limited response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        
        # Should detect rate limiting
        assert handler.is_rate_limited(mock_response) is True
        
        # Should suggest retry
        assert handler.should_retry(0, mock_response) is True
        
        # Should provide delay
        delay = handler.get_delay(0)
        assert delay > 0
        
        # Should add jitter to delay
        jittered_delay = handler.add_jitter(delay)
        assert jittered_delay >= 0


if __name__ == "__main__":
    pytest.main([__file__])
