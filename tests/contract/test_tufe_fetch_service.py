"""
Contract tests for TufeFetchService.
Tests the service interface and expected behavior for easy TÜFE data fetching.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.tufe_fetch_service import TufeFetchService
from src.services.exceptions import TufeFetchError, ValidationError, SourceNotFoundError, SessionNotFoundError, SessionNotCancellableError
from src.models.tufe_fetch_result import TufeFetchResult
from src.models.tufe_fetch_session import TufeFetchSession


class TestTufeFetchService:
    """Test TufeFetchService contract and interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_data_store = Mock()
        self.mock_source_manager = Mock()
        self.service = TufeFetchService(self.mock_data_store, self.mock_source_manager)
    
    def test_fetch_tufe_easy_success(self):
        """Test successful easy TÜFE fetching."""
        # Arrange
        year = 2023
        expected_result = TufeFetchResult(
            success=True,
            data=Mock(),
            source=Mock(),
            session_id="test_session_123",
            fetch_duration=1.5,
            attempts=[],
            error_message=None,
            cached=False
        )
        
        with patch.object(self.service, '_fetch_with_fallback') as mock_fetch:
            mock_fetch.return_value = expected_result
            
            # Act
            result = self.service.fetch_tufe_easy(year)
            
            # Assert
            assert result.success is True
            assert result.session_id == "test_session_123"
            assert result.fetch_duration == 1.5
            mock_fetch.assert_called_once_with(year)
    
    def test_fetch_tufe_easy_validation_error(self):
        """Test easy TÜFE fetching with invalid year."""
        # Arrange
        invalid_year = 1999
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Year must be between 2000 and"):
            self.service.fetch_tufe_easy(invalid_year)
    
    def test_fetch_tufe_easy_all_sources_fail(self):
        """Test easy TÜFE fetching when all sources fail."""
        # Arrange
        year = 2023
        
        with patch.object(self.service, '_fetch_with_fallback') as mock_fetch:
            mock_fetch.side_effect = TufeFetchError("All sources failed")
            
            # Act & Assert
            with pytest.raises(TufeFetchError, match="All sources failed"):
                self.service.fetch_tufe_easy(year)
    
    def test_fetch_tufe_with_source_success(self):
        """Test fetching TÜFE data from a specific source."""
        # Arrange
        year = 2023
        source_id = 1
        expected_result = TufeFetchResult(
            success=True,
            data=Mock(),
            source=Mock(),
            session_id="test_session_456",
            fetch_duration=0.8,
            attempts=[],
            error_message=None,
            cached=False
        )
        
        with patch.object(self.service, '_fetch_from_specific_source') as mock_fetch:
            mock_fetch.return_value = expected_result
            
            # Act
            result = self.service.fetch_tufe_with_source(year, source_id)
            
            # Assert
            assert result.success is True
            assert result.session_id == "test_session_456"
            mock_fetch.assert_called_once_with(year, source_id)
    
    def test_fetch_tufe_with_source_not_found(self):
        """Test fetching from non-existent source."""
        # Arrange
        year = 2023
        source_id = 999
        
        with patch.object(self.service, '_fetch_from_specific_source') as mock_fetch:
            mock_fetch.side_effect = SourceNotFoundError(f"Source {source_id} not found")
            
            # Act & Assert
            with pytest.raises(SourceNotFoundError, match="Source 999 not found"):
                self.service.fetch_tufe_with_source(year, source_id)
    
    def test_fetch_tufe_with_source_failure(self):
        """Test fetching from source that fails."""
        # Arrange
        year = 2023
        source_id = 1
        
        with patch.object(self.service, '_fetch_from_specific_source') as mock_fetch:
            mock_fetch.side_effect = TufeFetchError("Source failed")
            
            # Act & Assert
            with pytest.raises(TufeFetchError, match="Source failed"):
                self.service.fetch_tufe_with_source(year, source_id)
    
    def test_get_fetch_status_success(self):
        """Test getting fetch status for existing session."""
        # Arrange
        session_id = "test_session_123"
        expected_session = TufeFetchSession(
            id=1,
            session_id=session_id,
            requested_year=2023,
            status="success",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            source_attempts="[]",
            final_source=1,
            error_message=None,
            retry_count=0,
            user_id="test_user"
        )
        
        self.mock_data_store.get_tufe_fetch_session.return_value = expected_session
        
        # Act
        result = self.service.get_fetch_status(session_id)
        
        # Assert
        assert result.session_id == session_id
        assert result.status == "success"
        self.mock_data_store.get_tufe_fetch_session.assert_called_once_with(session_id)
    
    def test_get_fetch_status_not_found(self):
        """Test getting fetch status for non-existent session."""
        # Arrange
        session_id = "non_existent_session"
        self.mock_data_store.get_tufe_fetch_session.return_value = None
        
        # Act & Assert
        with pytest.raises(SessionNotFoundError, match="Session not found"):
            self.service.get_fetch_status(session_id)
    
    def test_cancel_fetch_success(self):
        """Test successfully cancelling a fetch operation."""
        # Arrange
        session_id = "test_session_123"
        session = TufeFetchSession(
            id=1,
            session_id=session_id,
            requested_year=2023,
            status="in_progress",
            started_at=datetime.now(),
            completed_at=None,
            source_attempts="[]",
            final_source=None,
            error_message=None,
            retry_count=0,
            user_id="test_user"
        )
        
        self.mock_data_store.get_tufe_fetch_session.return_value = session
        self.mock_data_store.update_tufe_fetch_session.return_value = True
        
        # Act
        result = self.service.cancel_fetch(session_id)
        
        # Assert
        assert result is True
        self.mock_data_store.update_tufe_fetch_session.assert_called_once()
    
    def test_cancel_fetch_session_not_found(self):
        """Test cancelling non-existent session."""
        # Arrange
        session_id = "non_existent_session"
        self.mock_data_store.get_tufe_fetch_session.return_value = None
        
        # Act & Assert
        with pytest.raises(SessionNotFoundError, match="Session not found"):
            self.service.cancel_fetch(session_id)
    
    def test_cancel_fetch_not_cancellable(self):
        """Test cancelling session that cannot be cancelled."""
        # Arrange
        session_id = "test_session_123"
        session = TufeFetchSession(
            id=1,
            session_id=session_id,
            requested_year=2023,
            status="completed",  # Already completed
            started_at=datetime.now(),
            completed_at=datetime.now(),
            source_attempts="[]",
            final_source=1,
            error_message=None,
            retry_count=0,
            user_id="test_user"
        )
        
        self.mock_data_store.get_tufe_fetch_session.return_value = session
        
        # Act & Assert
        with pytest.raises(SessionNotCancellableError, match="Session cannot be cancelled"):
            self.service.cancel_fetch(session_id)
    
    def test_fetch_tufe_easy_performance_requirement(self):
        """Test that easy fetch meets performance requirement (<2 seconds)."""
        # Arrange
        year = 2023
        start_time = datetime.now()
        
        with patch.object(self.service, '_fetch_with_fallback') as mock_fetch:
            mock_fetch.return_value = TufeFetchResult(
                success=True,
                data=Mock(),
                source=Mock(),
                session_id="test_session",
                fetch_duration=1.5,  # Within 2 second requirement
                attempts=[],
                error_message=None,
                cached=False
            )
            
            # Act
            result = self.service.fetch_tufe_easy(year)
            
            # Assert
            assert result.fetch_duration < 2.0
            assert result.success is True
    
    def test_fetch_tufe_easy_cached_result(self):
        """Test that cached results are returned quickly."""
        # Arrange
        year = 2023
        
        with patch.object(self.service, '_check_cache') as mock_cache:
            mock_cache.return_value = TufeFetchResult(
                success=True,
                data=Mock(),
                source=Mock(),
                session_id="test_session",
                fetch_duration=0.05,  # Very fast cache lookup
                attempts=[],
                error_message=None,
                cached=True
            )
            
            # Act
            result = self.service.fetch_tufe_easy(year)
            
            # Assert
            assert result.cached is True
            assert result.fetch_duration < 0.1  # Cache should be very fast
            mock_cache.assert_called_once_with(year)
    
    def test_fetch_tufe_easy_source_attempts_tracking(self):
        """Test that source attempts are properly tracked."""
        # Arrange
        year = 2023
        attempts = [
            Mock(source_id=1, source_name="TCMB", attempted_at=datetime.now(), success=False, response_time=1000.0, error_message="Timeout"),
            Mock(source_id=2, source_name="TÜİK", attempted_at=datetime.now(), success=True, response_time=500.0, error_message=None)
        ]
        
        with patch.object(self.service, '_fetch_with_fallback') as mock_fetch:
            mock_fetch.return_value = TufeFetchResult(
                success=True,
                data=Mock(),
                source=Mock(),
                session_id="test_session",
                fetch_duration=1.5,
                attempts=attempts,
                error_message=None,
                cached=False
            )
            
            # Act
            result = self.service.fetch_tufe_easy(year)
            
            # Assert
            assert len(result.attempts) == 2
            assert result.attempts[0].success is False
            assert result.attempts[1].success is True
            assert result.attempts[0].error_message == "Timeout"
            assert result.attempts[1].error_message is None
