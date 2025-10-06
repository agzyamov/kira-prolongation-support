"""
Performance tests for OECD API integration.

Tests API response times, memory usage, and performance characteristics
to ensure the system meets the <2s response time target.
"""

import pytest
import time
import psutil
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from decimal import Decimal

from src.services.inflation_service import InflationService
from src.services.oecd_api_client import OECDApiClient
from src.services.rate_limit_handler import RateLimitHandler
from src.services.data_validator import DataValidator
from src.storage.data_store import DataStore
from src.models.inflation_data import InflationData


class TestOECAPerformance:
    """Performance tests for OECD API integration."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mocked services for performance testing."""
        data_store = Mock(spec=DataStore)
        oecd_client = Mock(spec=OECDApiClient)
        rate_limit_handler = Mock(spec=RateLimitHandler)
        data_validator = Mock(spec=DataValidator)
        
        return {
            'data_store': data_store,
            'oecd_client': oecd_client,
            'rate_limit_handler': rate_limit_handler,
            'data_validator': data_validator
        }
    
    @pytest.fixture
    def inflation_service(self, mock_services):
        """Create InflationService with mocked dependencies."""
        return InflationService(
            data_store=mock_services['data_store'],
            oecd_client=mock_services['oecd_client'],
            rate_limit_handler=mock_services['rate_limit_handler'],
            validator=mock_services['data_validator']
        )
    
    def test_api_response_time_target(self, inflation_service, mock_services):
        """Test that API response time meets <2s target."""
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': i, 'value': 10.0 + i, 'source': 'OECD SDMX API'}
                for i in range(1, 13)  # 12 months of data
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Measure response time
        start_time = time.time()
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verify performance target
        assert response_time < 2.0, f"Response time {response_time:.3f}s exceeds 2s target"
        
        # Verify result integrity
        assert len(result) == 12
        assert all(isinstance(item, InflationData) for item in result)
    
    def test_cached_data_response_time_target(self, inflation_service):
        """Test that cached data response time meets <500ms target."""
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Mock cached data
            mock_cached_data = InflationData(
                year=2020,
                month=1,
                tufe_rate=Decimal("10.5"),
                source="OECD SDMX API"
            )
            mock_cache_service.get_cached_oecd_data.return_value = mock_cached_data
            
            # Measure response time
            start_time = time.time()
            result = inflation_service.get_cached_oecd_tufe_data(2020, 1)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Verify performance target
            assert response_time < 0.5, f"Cached response time {response_time:.3f}s exceeds 500ms target"
            
            # Verify result
            assert result == mock_cached_data
    
    def test_memory_usage_stability(self, inflation_service, mock_services):
        """Test that memory usage remains stable during operations."""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock API response with large dataset
        mock_api_result = {
            'items': [
                {'year': year, 'month': month, 'value': 10.0 + (year - 2020) * 0.5, 'source': 'OECD SDMX API'}
                for year in range(2020, 2025)  # 5 years
                for month in range(1, 13)  # 12 months
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Perform multiple operations
        for _ in range(10):
            result = inflation_service.fetch_tufe_from_oecd_api(2020, 2024)
            assert len(result) == 60  # 5 years * 12 months
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify memory usage is reasonable (less than 50MB increase)
        assert memory_increase < 50, f"Memory increase {memory_increase:.1f}MB exceeds 50MB limit"
    
    def test_concurrent_requests_performance(self, inflation_service, mock_services):
        """Test performance under concurrent requests."""
        import threading
        import queue
        
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Results queue
        results_queue = queue.Queue()
        errors_queue = queue.Queue()
        
        def make_request():
            """Make a single API request."""
            try:
                start_time = time.time()
                result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
                end_time = time.time()
                
                results_queue.put({
                    'response_time': end_time - start_time,
                    'result_count': len(result)
                })
            except Exception as e:
                errors_queue.put(str(e))
        
        # Create multiple threads
        threads = []
        num_threads = 5
        
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        errors = []
        while not errors_queue.empty():
            errors.append(errors_queue.get())
        
        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # Verify all requests completed
        assert len(results) == num_threads
        
        # Verify individual response times
        for result in results:
            assert result['response_time'] < 2.0, f"Individual response time {result['response_time']:.3f}s exceeds 2s target"
            assert result['result_count'] == 1
        
        # Verify total time is reasonable (should be much less than sum of individual times)
        individual_times = [r['response_time'] for r in results]
        total_individual_time = sum(individual_times)
        
        # Total time should be less than sum of individual times (due to concurrency)
        assert total_time < total_individual_time, f"Total time {total_time:.3f}s should be less than sum of individual times {total_individual_time:.3f}s"
    
    def test_large_dataset_performance(self, inflation_service, mock_services):
        """Test performance with large datasets."""
        # Mock large API response (10 years of monthly data)
        mock_api_result = {
            'items': [
                {'year': year, 'month': month, 'value': 10.0 + (year - 2020) * 0.5, 'source': 'OECD SDMX API'}
                for year in range(2020, 2030)  # 10 years
                for month in range(1, 13)  # 12 months
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Measure performance
        start_time = time.time()
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2029)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verify performance target (relaxed for large datasets)
        assert response_time < 5.0, f"Large dataset response time {response_time:.3f}s exceeds 5s target"
        
        # Verify result integrity
        assert len(result) == 120  # 10 years * 12 months
        assert all(isinstance(item, InflationData) for item in result)
        
        # Verify data integrity
        years = set(item.year for item in result)
        assert years == set(range(2020, 2030))
        
        months = set(item.month for item in result)
        assert months == set(range(1, 13))
    
    def test_validation_performance(self, inflation_service, mock_services):
        """Test performance of data validation."""
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': i, 'value': 10.0 + i, 'source': 'OECD SDMX API'}
                for i in range(1, 13)  # 12 months of data
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Measure validation time
        start_time = time.time()
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        end_time = time.time()
        
        validation_time = end_time - start_time
        
        # Verify validation is fast (should be much less than API time)
        assert validation_time < 0.1, f"Validation time {validation_time:.3f}s exceeds 100ms target"
        
        # Verify validation was called
        assert mock_services['data_validator'].validate_complete_record.call_count == 12
        
        # Verify result
        assert len(result) == 12
    
    def test_caching_performance(self, inflation_service, mock_services):
        """Test performance of caching operations."""
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Mock cache service
        with patch('src.services.inflation_service.TufeCacheService') as mock_cache_service_class:
            mock_cache_service = Mock()
            mock_cache_service_class.return_value = mock_cache_service
            
            # Measure caching time
            start_time = time.time()
            result = inflation_service.fetch_and_cache_oecd_tufe_data(2020, 2020)
            end_time = time.time()
            
            caching_time = end_time - start_time
            
            # Verify caching is fast
            assert caching_time < 0.5, f"Caching time {caching_time:.3f}s exceeds 500ms target"
            
            # Verify cache was called
            mock_cache_service.cache_oecd_data.assert_called_once()
            
            # Verify result
            assert len(result) == 1
    
    def test_error_handling_performance(self, inflation_service, mock_services):
        """Test performance of error handling."""
        from src.services.exceptions import TufeApiError
        
        # Mock API error
        mock_services['oecd_client'].fetch_tufe_data.side_effect = TufeApiError("API request failed")
        
        # Measure error handling time
        start_time = time.time()
        
        with pytest.raises(TufeApiError):
            inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        
        end_time = time.time()
        
        error_handling_time = end_time - start_time
        
        # Verify error handling is fast
        assert error_handling_time < 0.1, f"Error handling time {error_handling_time:.3f}s exceeds 100ms target"
    
    def test_rate_limiting_performance(self, inflation_service, mock_services):
        """Test performance of rate limiting checks."""
        # Mock rate limit status
        mock_rate_status = {
            "can_make_request": True,
            "remaining_hour": 95,
            "remaining_day": 950
        }
        mock_services['rate_limit_handler'].get_rate_limit_status.return_value = mock_rate_status
        
        # Measure rate limit check time
        start_time = time.time()
        result = inflation_service.get_rate_limit_status()
        end_time = time.time()
        
        rate_limit_time = end_time - start_time
        
        # Verify rate limit check is fast
        assert rate_limit_time < 0.01, f"Rate limit check time {rate_limit_time:.3f}s exceeds 10ms target"
        
        # Verify result
        assert result == mock_rate_status
    
    def test_health_check_performance(self, inflation_service, mock_services):
        """Test performance of health checks."""
        # Mock healthy API
        mock_services['oecd_client'].is_healthy.return_value = True
        
        # Measure health check time
        start_time = time.time()
        result = inflation_service.is_oecd_api_healthy()
        end_time = time.time()
        
        health_check_time = end_time - start_time
        
        # Verify health check is fast
        assert health_check_time < 0.1, f"Health check time {health_check_time:.3f}s exceeds 100ms target"
        
        # Verify result
        assert result is True
    
    def test_memory_cleanup_after_operations(self, inflation_service, mock_services):
        """Test that memory is properly cleaned up after operations."""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': i, 'value': 10.0 + i, 'source': 'OECD SDMX API'}
                for i in range(1, 13)  # 12 months of data
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Perform operation
        result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
        assert len(result) == 12
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Get memory usage after cleanup
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify memory increase is minimal
        assert memory_increase < 10, f"Memory increase {memory_increase:.1f}MB exceeds 10MB limit"
    
    def test_performance_under_load(self, inflation_service, mock_services):
        """Test performance under sustained load."""
        # Mock API response
        mock_api_result = {
            'items': [
                {'year': 2020, 'month': 1, 'value': 10.5, 'source': 'OECD SDMX API'}
            ]
        }
        mock_services['oecd_client'].fetch_tufe_data.return_value = mock_api_result
        mock_services['data_validator'].validate_complete_record.return_value = None
        
        # Perform multiple operations
        num_operations = 100
        response_times = []
        
        start_time = time.time()
        
        for i in range(num_operations):
            operation_start = time.time()
            result = inflation_service.fetch_tufe_from_oecd_api(2020, 2020)
            operation_end = time.time()
            
            response_times.append(operation_end - operation_start)
            assert len(result) == 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Verify performance targets
        assert avg_response_time < 2.0, f"Average response time {avg_response_time:.3f}s exceeds 2s target"
        assert max_response_time < 5.0, f"Max response time {max_response_time:.3f}s exceeds 5s target"
        
        # Verify throughput
        throughput = num_operations / total_time
        assert throughput > 10, f"Throughput {throughput:.1f} ops/sec is too low"
        
        # Verify consistency
        response_time_variance = max(response_times) - min(response_times)
        assert response_time_variance < 1.0, f"Response time variance {response_time_variance:.3f}s is too high"


if __name__ == "__main__":
    pytest.main([__file__])
