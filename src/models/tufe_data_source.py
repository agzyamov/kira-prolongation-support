"""
Enhanced TufeDataSource model for managing TÜFE data sources with reliability tracking.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health status enumeration for data sources."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class TufeDataSource:
    """Enhanced model for TÜFE data sources with reliability tracking."""
    
    id: Optional[int] = None
    source_name: str = ""
    api_endpoint: str = ""
    series_code: str = ""
    data_format: str = "json"
    requires_auth: bool = True
    rate_limit_per_hour: int = 100
    last_verified: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    # Enhanced fields for reliability tracking
    priority: int = 5  # 1-10, lower = higher priority
    reliability_score: float = 0.5  # 0.0-1.0, based on success rate
    last_health_check: Optional[datetime] = None
    health_status: HealthStatus = HealthStatus.UNKNOWN
    failure_count: int = 0  # consecutive failures
    success_count: int = 0  # consecutive successes
    avg_response_time: float = 0.0  # milliseconds
    rate_limit_remaining: int = 1000  # API rate limit remaining
    rate_limit_reset: Optional[datetime] = None  # when rate limit resets
    
    def __post_init__(self):
        """Validate the data source after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate the data source fields."""
        if not self.source_name or not self.source_name.strip():
            raise ValueError("source_name must be a non-empty string")
        
        if not self.api_endpoint or not self.api_endpoint.strip():
            raise ValueError("api_endpoint must be a non-empty string")
        
        if not self.api_endpoint.startswith(('http://', 'https://')):
            raise ValueError("api_endpoint must be a valid URL starting with http:// or https://")
        
        if not self.series_code or not self.series_code.strip():
            raise ValueError("series_code must be a non-empty string")
        
        if self.data_format not in ['json', 'xml']:
            raise ValueError("data_format must be 'json' or 'xml'")
        
        if self.rate_limit_per_hour <= 0:
            raise ValueError("rate_limit_per_hour must be a positive integer")
        
        if not isinstance(self.requires_auth, bool):
            raise ValueError("requires_auth must be a boolean")
        
        if not isinstance(self.is_active, bool):
            raise ValueError("is_active must be a boolean")
        
        # Enhanced validation for new fields
        if not (1 <= self.priority <= 10):
            raise ValueError("priority must be between 1 and 10")
        
        if not (0.0 <= self.reliability_score <= 1.0):
            raise ValueError("reliability_score must be between 0.0 and 1.0")
        
        if self.health_status not in HealthStatus:
            raise ValueError("health_status must be a valid HealthStatus")
        
        if self.failure_count < 0:
            raise ValueError("failure_count must be non-negative")
        
        if self.success_count < 0:
            raise ValueError("success_count must be non-negative")
        
        if self.avg_response_time < 0:
            raise ValueError("avg_response_time must be non-negative")
        
        if self.rate_limit_remaining < 0:
            raise ValueError("rate_limit_remaining must be non-negative")
    
    def to_dict(self) -> dict:
        """Convert the data source to a dictionary."""
        return {
            'id': self.id,
            'source_name': self.source_name,
            'api_endpoint': self.api_endpoint,
            'series_code': self.series_code,
            'data_format': self.data_format,
            'requires_auth': self.requires_auth,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'last_verified': self.last_verified.isoformat() if self.last_verified else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # Enhanced fields
            'priority': self.priority,
            'reliability_score': self.reliability_score,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'health_status': self.health_status.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'avg_response_time': self.avg_response_time,
            'rate_limit_remaining': self.rate_limit_remaining,
            'rate_limit_reset': self.rate_limit_reset.isoformat() if self.rate_limit_reset else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TufeDataSource':
        """Create a TufeDataSource from a dictionary."""
        # Parse datetime fields
        last_verified = None
        if data.get('last_verified'):
            last_verified = datetime.fromisoformat(data['last_verified'])
        
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        last_health_check = None
        if data.get('last_health_check'):
            last_health_check = datetime.fromisoformat(data['last_health_check'])
        
        rate_limit_reset = None
        if data.get('rate_limit_reset'):
            rate_limit_reset = datetime.fromisoformat(data['rate_limit_reset'])
        
        # Parse health status
        health_status = HealthStatus.UNKNOWN
        if data.get('health_status'):
            try:
                health_status = HealthStatus(data['health_status'])
            except ValueError:
                health_status = HealthStatus.UNKNOWN
        
        return cls(
            id=data.get('id'),
            source_name=data['source_name'],
            api_endpoint=data['api_endpoint'],
            series_code=data['series_code'],
            data_format=data.get('data_format', 'json'),
            requires_auth=data.get('requires_auth', True),
            rate_limit_per_hour=data.get('rate_limit_per_hour', 100),
            last_verified=last_verified,
            is_active=data.get('is_active', True),
            created_at=created_at,
            # Enhanced fields
            priority=data.get('priority', 5),
            reliability_score=data.get('reliability_score', 0.5),
            last_health_check=last_health_check,
            health_status=health_status,
            failure_count=data.get('failure_count', 0),
            success_count=data.get('success_count', 0),
            avg_response_time=data.get('avg_response_time', 0.0),
            rate_limit_remaining=data.get('rate_limit_remaining', 1000),
            rate_limit_reset=rate_limit_reset
        )
    
    def update_verification(self, verified_at: datetime = None):
        """Update the last verification timestamp."""
        if verified_at is None:
            verified_at = datetime.now()
        self.last_verified = verified_at
    
    def activate(self):
        """Activate the data source."""
        self.is_active = True
    
    def deactivate(self):
        """Deactivate the data source."""
        self.is_active = False
    
    def is_verified(self) -> bool:
        """Check if the data source has been verified."""
        return self.last_verified is not None
    
    def get_verification_age_days(self) -> Optional[int]:
        """Get the age of the last verification in days."""
        if self.last_verified is None:
            return None
        
        delta = datetime.now() - self.last_verified
        return delta.days
    
    def needs_verification(self, max_age_days: int = 30) -> bool:
        """Check if the data source needs verification."""
        if not self.is_verified():
            return True
        
        age_days = self.get_verification_age_days()
        return age_days is not None and age_days > max_age_days
    
    # Enhanced methods for reliability tracking
    
    def update_health_status(self, status: HealthStatus, checked_at: datetime = None):
        """Update the health status of the data source."""
        if checked_at is None:
            checked_at = datetime.now()
        
        self.health_status = status
        self.last_health_check = checked_at
    
    def mark_success(self, response_time: float):
        """Mark a successful operation and update reliability metrics."""
        self.success_count += 1
        self.failure_count = 0  # Reset failure count on success
        
        # Update average response time
        if self.success_count == 1:
            self.avg_response_time = response_time
        else:
            # Calculate running average
            self.avg_response_time = (self.avg_response_time * (self.success_count - 1) + response_time) / self.success_count
        
        # Update reliability score
        total_attempts = self.success_count + self.failure_count
        if total_attempts > 0:
            self.reliability_score = self.success_count / total_attempts
        
        # Update health status based on performance
        if self.avg_response_time > 2000.0:  # > 2 seconds
            self.health_status = HealthStatus.DEGRADED
        elif self.success_count >= 3:
            self.health_status = HealthStatus.HEALTHY
    
    def mark_failure(self, error_message: str = None):
        """Mark a failed operation and update reliability metrics."""
        self.failure_count += 1
        self.success_count = 0  # Reset success count on failure
        
        # Update reliability score
        total_attempts = self.success_count + self.failure_count
        if total_attempts > 0:
            self.reliability_score = self.success_count / total_attempts
        
        # Update health status based on failure count
        if self.failure_count >= 3:
            self.health_status = HealthStatus.FAILED
        elif self.failure_count >= 1:
            self.health_status = HealthStatus.DEGRADED
    
    def update_priority(self, new_priority: int):
        """Update the priority of the data source."""
        if not (1 <= new_priority <= 10):
            raise ValueError("Priority must be between 1 and 10")
        self.priority = new_priority
    
    def update_rate_limit(self, remaining: int, reset_time: datetime = None):
        """Update rate limit information."""
        self.rate_limit_remaining = remaining
        if reset_time:
            self.rate_limit_reset = reset_time
    
    def is_healthy(self) -> bool:
        """Check if the data source is healthy."""
        return self.health_status == HealthStatus.HEALTHY
    
    def is_degraded(self) -> bool:
        """Check if the data source is degraded."""
        return self.health_status == HealthStatus.DEGRADED
    
    def is_failed(self) -> bool:
        """Check if the data source has failed."""
        return self.health_status == HealthStatus.FAILED
    
    def get_health_age_minutes(self) -> Optional[int]:
        """Get the age of the last health check in minutes."""
        if self.last_health_check is None:
            return None
        
        delta = datetime.now() - self.last_health_check
        return int(delta.total_seconds() / 60)
    
    def needs_health_check(self, max_age_minutes: int = 5) -> bool:
        """Check if the data source needs a health check."""
        age_minutes = self.get_health_age_minutes()
        return age_minutes is None or age_minutes > max_age_minutes
    
    def __str__(self) -> str:
        """String representation of the data source."""
        status = "Active" if self.is_active else "Inactive"
        verified = "Verified" if self.is_verified() else "Not Verified"
        health = self.health_status.value.title()
        return f"TufeDataSource({self.source_name}, {status}, {verified}, {health})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the data source."""
        return (f"TufeDataSource(id={self.id}, source_name='{self.source_name}', "
                f"api_endpoint='{self.api_endpoint}', series_code='{self.series_code}', "
                f"data_format='{self.data_format}', requires_auth={self.requires_auth}, "
                f"rate_limit_per_hour={self.rate_limit_per_hour}, "
                f"last_verified={self.last_verified}, is_active={self.is_active}, "
                f"created_at={self.created_at}, priority={self.priority}, "
                f"reliability_score={self.reliability_score}, "
                f"health_status={self.health_status.value}, "
                f"failure_count={self.failure_count}, success_count={self.success_count}, "
                f"avg_response_time={self.avg_response_time})")
