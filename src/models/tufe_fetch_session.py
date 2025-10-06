"""
TufeFetchSession model for tracking TÜFE data fetching operations.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class FetchStatus(Enum):
    """Fetch session status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SourceAttempt:
    """Represents an attempt to fetch data from a source."""
    
    source_id: int
    source_name: str
    attempted_at: datetime
    success: bool
    response_time: float  # milliseconds
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'source_id': self.source_id,
            'source_name': self.source_name,
            'attempted_at': self.attempted_at.isoformat(),
            'success': self.success,
            'response_time': self.response_time,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SourceAttempt':
        """Create from dictionary."""
        return cls(
            source_id=data['source_id'],
            source_name=data['source_name'],
            attempted_at=datetime.fromisoformat(data['attempted_at']),
            success=data['success'],
            response_time=data['response_time'],
            error_message=data.get('error_message')
        )


@dataclass
class TufeFetchSession:
    """Model for tracking TÜFE data fetching operations."""
    
    id: Optional[int] = None
    session_id: str = ""
    requested_year: int = 0
    status: FetchStatus = FetchStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    source_attempts: List[SourceAttempt] = None
    final_source: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize and validate the fetch session."""
        if self.source_attempts is None:
            self.source_attempts = []
        
        if self.started_at is None:
            self.started_at = datetime.now()
        
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        self._validate()
    
    def _validate(self):
        """Validate the fetch session fields."""
        if not self.session_id or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        
        if not (2000 <= self.requested_year <= 2030):
            raise ValueError("requested_year must be between 2000 and 2030")
        
        if self.status not in FetchStatus:
            raise ValueError("status must be a valid FetchStatus")
        
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        
        if self.started_at and self.completed_at and self.completed_at < self.started_at:
            raise ValueError("completed_at cannot be before started_at")
    
    def to_dict(self) -> dict:
        """Convert the fetch session to a dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'requested_year': self.requested_year,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'source_attempts': json.dumps([attempt.to_dict() for attempt in self.source_attempts]),
            'final_source': self.final_source,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeFetchSession':
        """Create a TufeFetchSession from a dictionary."""
        # Parse datetime fields
        started_at = None
        if data.get('started_at'):
            started_at = datetime.fromisoformat(data['started_at'])
        
        completed_at = None
        if data.get('completed_at'):
            completed_at = datetime.fromisoformat(data['completed_at'])
        
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        updated_at = None
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
        
        # Parse status
        status = FetchStatus.PENDING
        if data.get('status'):
            try:
                status = FetchStatus(data['status'])
            except ValueError:
                status = FetchStatus.PENDING
        
        # Parse source attempts
        source_attempts = []
        if data.get('source_attempts'):
            try:
                attempts_data = json.loads(data['source_attempts'])
                source_attempts = [SourceAttempt.from_dict(attempt) for attempt in attempts_data]
            except (json.JSONDecodeError, KeyError, ValueError):
                source_attempts = []
        
        return cls(
            id=data.get('id'),
            session_id=data['session_id'],
            requested_year=data['requested_year'],
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            source_attempts=source_attempts,
            final_source=data.get('final_source'),
            error_message=data.get('error_message'),
            retry_count=data.get('retry_count', 0),
            user_id=data.get('user_id'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def start_fetch(self):
        """Start the fetch operation."""
        if self.status != FetchStatus.PENDING:
            raise ValueError(f"Cannot start fetch from status {self.status.value}")
        
        self.status = FetchStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def complete_success(self, final_source_id: int):
        """Mark the fetch as successful."""
        if self.status != FetchStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete fetch from status {self.status.value}")
        
        self.status = FetchStatus.SUCCESS
        self.completed_at = datetime.now()
        self.final_source = final_source_id
        self.error_message = None
        self.updated_at = datetime.now()
    
    def complete_failure(self, error_message: str):
        """Mark the fetch as failed."""
        if self.status not in [FetchStatus.IN_PROGRESS, FetchStatus.PENDING]:
            raise ValueError(f"Cannot fail fetch from status {self.status.value}")
        
        self.status = FetchStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
        self.updated_at = datetime.now()
    
    def cancel(self):
        """Cancel the fetch operation."""
        if self.status not in [FetchStatus.PENDING, FetchStatus.IN_PROGRESS]:
            raise ValueError(f"Cannot cancel fetch from status {self.status.value}")
        
        self.status = FetchStatus.CANCELLED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
    
    def retry(self):
        """Increment retry count and reset status for retry."""
        if self.status not in [FetchStatus.FAILED, FetchStatus.CANCELLED]:
            raise ValueError(f"Cannot retry fetch from status {self.status.value}")
        
        self.retry_count += 1
        self.status = FetchStatus.PENDING
        self.completed_at = None
        self.error_message = None
        self.updated_at = datetime.now()
    
    def add_source_attempt(self, source_id: int, source_name: str, success: bool, 
                          response_time: float, error_message: str = None):
        """Add a source attempt to the session."""
        attempt = SourceAttempt(
            source_id=source_id,
            source_name=source_name,
            attempted_at=datetime.now(),
            success=success,
            response_time=response_time,
            error_message=error_message
        )
        self.source_attempts.append(attempt)
        self.updated_at = datetime.now()
    
    def get_duration_seconds(self) -> Optional[float]:
        """Get the duration of the fetch operation in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.now()
        delta = end_time - self.started_at
        return delta.total_seconds()
    
    def is_completed(self) -> bool:
        """Check if the fetch session is completed (success, failed, or cancelled)."""
        return self.status in [FetchStatus.SUCCESS, FetchStatus.FAILED, FetchStatus.CANCELLED]
    
    def is_successful(self) -> bool:
        """Check if the fetch session was successful."""
        return self.status == FetchStatus.SUCCESS
    
    def is_failed(self) -> bool:
        """Check if the fetch session failed."""
        return self.status == FetchStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """Check if the fetch session was cancelled."""
        return self.status == FetchStatus.CANCELLED
    
    def is_in_progress(self) -> bool:
        """Check if the fetch session is in progress."""
        return self.status == FetchStatus.IN_PROGRESS
    
    def is_pending(self) -> bool:
        """Check if the fetch session is pending."""
        return self.status == FetchStatus.PENDING
    
    def get_successful_attempts(self) -> List[SourceAttempt]:
        """Get all successful source attempts."""
        return [attempt for attempt in self.source_attempts if attempt.success]
    
    def get_failed_attempts(self) -> List[SourceAttempt]:
        """Get all failed source attempts."""
        return [attempt for attempt in self.source_attempts if not attempt.success]
    
    def get_total_attempts(self) -> int:
        """Get the total number of source attempts."""
        return len(self.source_attempts)
    
    def get_average_response_time(self) -> Optional[float]:
        """Get the average response time of all attempts."""
        if not self.source_attempts:
            return None
        
        total_time = sum(attempt.response_time for attempt in self.source_attempts)
        return total_time / len(self.source_attempts)
    
    def __str__(self) -> str:
        """String representation of the fetch session."""
        duration = self.get_duration_seconds()
        duration_str = f"{duration:.2f}s" if duration else "N/A"
        return f"TufeFetchSession({self.session_id}, {self.status.value}, {duration_str})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the fetch session."""
        return (f"TufeFetchSession(id={self.id}, session_id='{self.session_id}', "
                f"requested_year={self.requested_year}, status={self.status.value}, "
                f"started_at={self.started_at}, completed_at={self.completed_at}, "
                f"final_source={self.final_source}, retry_count={self.retry_count}, "
                f"user_id='{self.user_id}')")
