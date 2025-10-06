"""
Rate Limit Handler for OECD API

This service manages API rate limiting and backoff logic to ensure respectful
usage of the OECD API and handle rate limit responses appropriately.
"""

import time
import random
from typing import Dict, Any
import requests

from src.config.oecd_config import RATE_LIMIT_CONFIG, ERROR_CONFIG
from src.services.exceptions import TufeApiError


class RateLimitHandler:
    """
    Handles rate limiting and backoff logic for API requests.
    
    Provides methods to determine retry behavior, calculate delays,
    and manage rate limit responses.
    """
    
    def __init__(self, max_retries: int = None, base_delay: float = None, 
                 backoff_factor: float = None, max_delay: float = None,
                 jitter_range: float = None):
        """
        Initialize rate limit handler.
        
        Args:
            max_retries: Maximum number of retry attempts (default from config)
            base_delay: Base delay in seconds for exponential backoff (default from config)
            backoff_factor: Factor for exponential backoff (default from config)
            max_delay: Maximum delay in seconds (default from config)
            jitter_range: Range for jitter randomization (default from config)
        """
        self.max_retries = max_retries or RATE_LIMIT_CONFIG["max_retries"]
        self.base_delay = base_delay or RATE_LIMIT_CONFIG["base_delay_seconds"]
        self.backoff_factor = backoff_factor or RATE_LIMIT_CONFIG["backoff_factor"]
        self.max_delay = max_delay or RATE_LIMIT_CONFIG["max_delay_seconds"]
        self.jitter_range = jitter_range or RATE_LIMIT_CONFIG["jitter_range"]
        
        # Rate limit tracking
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset_time = 0
    
    def should_retry(self, attempt: int, response: requests.Response) -> bool:
        """
        Determine if request should be retried.
        
        Args:
            attempt: Current attempt number (0-based)
            response: HTTP response object
        
        Returns:
            True if request should be retried, False otherwise
        """
        # Don't retry if we've exceeded max retries
        if attempt >= self.max_retries:
            return False
        
        # Check if response indicates retryable error
        status_code = response.status_code
        
        # Always retry rate limit errors
        if status_code == 429:
            return True
        
        # Retry server errors
        if status_code in ERROR_CONFIG["retryable_status_codes"]:
            return True
        
        # Don't retry client errors
        if status_code in ERROR_CONFIG["non_retryable_status_codes"]:
            return False
        
        # Default to not retrying for unknown status codes
        return False
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt.
        
        Args:
            attempt: Current attempt number (0-based)
        
        Returns:
            Delay in seconds
        """
        # Calculate exponential backoff delay
        delay = self.base_delay * (self.backoff_factor ** attempt)
        
        # Cap at maximum delay
        return min(delay, self.max_delay)
    
    def add_jitter(self, delay: float) -> float:
        """
        Add randomization to delay to avoid thundering herd.
        
        Args:
            delay: Base delay in seconds
        
        Returns:
            Jittered delay in seconds
        """
        # Add random jitter within the specified range
        jitter = random.uniform(-self.jitter_range, self.jitter_range)
        return delay * (1 + jitter)
    
    def is_rate_limited(self, response: requests.Response) -> bool:
        """
        Check if response indicates rate limiting.
        
        Args:
            response: HTTP response object
        
        Returns:
            True if rate limited, False otherwise
        """
        return response.status_code == 429
    
    def get_retry_after_delay(self, response: requests.Response) -> float:
        """
        Get retry delay from Retry-After header.
        
        Args:
            response: HTTP response object
        
        Returns:
            Retry delay in seconds, or None if not specified
        """
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                # Retry-After can be either seconds or HTTP date
                if retry_after.isdigit():
                    return float(retry_after)
                else:
                    # Parse HTTP date (simplified - in practice you'd use proper date parsing)
                    return 60.0  # Default to 60 seconds for HTTP dates
            except (ValueError, TypeError):
                return None
        return None
    
    def update_rate_limit_info(self, response: requests.Response) -> None:
        """
        Update rate limit tracking information from response headers.
        
        Args:
            response: HTTP response object
        """
        headers = response.headers
        
        # Update rate limit remaining
        remaining = headers.get('X-RateLimit-Remaining')
        if remaining:
            try:
                self.rate_limit_remaining = int(remaining)
            except (ValueError, TypeError):
                pass
        
        # Update rate limit reset time
        reset = headers.get('X-RateLimit-Reset')
        if reset:
            try:
                self.rate_limit_reset_time = int(reset)
            except (ValueError, TypeError):
                pass
        
        # Update request count
        self.request_count += 1
        self.last_request_time = time.time()
    
    def wait_for_rate_limit_reset(self, response: requests.Response) -> float:
        """
        Calculate wait time for rate limit reset.
        
        Args:
            response: HTTP response object
        
        Returns:
            Wait time in seconds
        """
        if not self.is_rate_limited(response):
            return 0.0
        
        # Check Retry-After header first
        retry_after = self.get_retry_after_delay(response)
        if retry_after:
            return retry_after
        
        # Check X-RateLimit-Reset header
        reset_time = response.headers.get('X-RateLimit-Reset')
        if reset_time:
            try:
                reset_timestamp = int(reset_time)
                current_time = time.time()
                wait_time = max(0, reset_timestamp - current_time)
                return min(wait_time, self.max_delay)  # Cap at max delay
            except (ValueError, TypeError):
                pass
        
        # Default to exponential backoff
        return self.get_delay(0)
    
    def can_make_request(self) -> bool:
        """
        Check if we can make a request based on rate limit tracking.
        
        Returns:
            True if request can be made, False otherwise
        """
        current_time = time.time()
        
        # Check if we're within rate limit reset period
        if self.rate_limit_reset_time > 0:
            if current_time < self.rate_limit_reset_time:
                return False
        
        # Check if we have remaining requests
        if hasattr(self, 'rate_limit_remaining') and self.rate_limit_remaining is not None:
            if self.rate_limit_remaining <= 0:
                return False
        
        return True
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit status information
        """
        current_time = time.time()
        
        return {
            'can_make_request': self.can_make_request(),
            'request_count': self.request_count,
            'last_request_time': self.last_request_time,
            'rate_limit_remaining': getattr(self, 'rate_limit_remaining', None),
            'rate_limit_reset_time': self.rate_limit_reset_time,
            'time_until_reset': max(0, self.rate_limit_reset_time - current_time) if self.rate_limit_reset_time > 0 else 0
        }
    
    def reset_rate_limit_tracking(self) -> None:
        """Reset rate limit tracking information."""
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_reset_time = 0
        if hasattr(self, 'rate_limit_remaining'):
            delattr(self, 'rate_limit_remaining')
    
    def handle_rate_limit_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle rate limit response and return retry information.
        
        Args:
            response: HTTP response object
        
        Returns:
            Dictionary with retry information
        """
        if not self.is_rate_limited(response):
            return {'should_retry': False, 'delay': 0}
        
        # Update rate limit info
        self.update_rate_limit_info(response)
        
        # Calculate wait time
        wait_time = self.wait_for_rate_limit_reset(response)
        
        return {
            'should_retry': True,
            'delay': wait_time,
            'retry_after': self.get_retry_after_delay(response),
            'rate_limit_remaining': getattr(self, 'rate_limit_remaining', None),
            'rate_limit_reset_time': self.rate_limit_reset_time
        }
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get rate limit handler configuration.
        
        Returns:
            Dictionary with configuration information
        """
        return {
            'max_retries': self.max_retries,
            'base_delay': self.base_delay,
            'backoff_factor': self.backoff_factor,
            'max_delay': self.max_delay,
            'jitter_range': self.jitter_range
        }
