"""
TufeFetchResult DTO for representing the result of a TÜFE data fetch operation.
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from src.models.tufe_data import TufeData
from src.models.tufe_data_source import TufeDataSource
from src.models.tufe_fetch_session import SourceAttempt


@dataclass
class TufeFetchResult:
    """Data Transfer Object for TÜFE data fetch operation results."""
    
    success: bool
    data: Optional[TufeData] = None
    source: Optional[TufeDataSource] = None
    session_id: str = ""
    fetch_duration: float = 0.0  # seconds
    attempts: List[SourceAttempt] = None
    error_message: Optional[str] = None
    cached: bool = False
    
    def __post_init__(self):
        """Initialize the fetch result."""
        if self.attempts is None:
            self.attempts = []
    
    def to_dict(self) -> dict:
        """Convert the fetch result to a dictionary."""
        return {
            'success': self.success,
            'data': self.data.to_dict() if self.data else None,
            'source': self.source.to_dict() if self.source else None,
            'session_id': self.session_id,
            'fetch_duration': self.fetch_duration,
            'attempts': [attempt.to_dict() for attempt in self.attempts],
            'error_message': self.error_message,
            'cached': self.cached
        }
    
    def get_attempt_count(self) -> int:
        """Get the number of attempts made."""
        return len(self.attempts)
    
    def get_successful_attempts(self) -> List[SourceAttempt]:
        """Get all successful attempts."""
        return [attempt for attempt in self.attempts if attempt.success]
    
    def get_failed_attempts(self) -> List[SourceAttempt]:
        """Get all failed attempts."""
        return [attempt for attempt in self.attempts if not attempt.success]
    
    def get_average_response_time(self) -> Optional[float]:
        """Get the average response time of all attempts."""
        if not self.attempts:
            return None
        
        total_time = sum(attempt.response_time for attempt in self.attempts)
        return total_time / len(self.attempts)
    
    def __str__(self) -> str:
        """String representation of the fetch result."""
        status = "Success" if self.success else "Failed"
        duration = f"{self.fetch_duration:.2f}s"
        attempts = len(self.attempts)
        cached = " (cached)" if self.cached else ""
        return f"TufeFetchResult({status}, {duration}, {attempts} attempts{cached})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the fetch result."""
        return (f"TufeFetchResult(success={self.success}, "
                f"session_id='{self.session_id}', "
                f"fetch_duration={self.fetch_duration}, "
                f"attempts_count={len(self.attempts)}, "
                f"cached={self.cached})")
