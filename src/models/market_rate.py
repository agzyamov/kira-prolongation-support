"""
MarketRate model for storing rental market data parsed from screenshots.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


@dataclass
class MarketRate:
    """
    Represents a market rental rate parsed from a screenshot.
    Used for comparison with user's actual rent.
    
    Attributes:
        amount_tl: Market rental price in Turkish Lira
        screenshot_filename: Path to source screenshot file
        location: Parsed location/district (e.g., "Kadıköy")
        date_captured: When the screenshot was taken
        id: Database primary key (None for new records)
        confidence: OCR confidence score (0.0-1.0)
        raw_ocr_text: Optional raw OCR output for debugging
        property_details: Optional parsed details (size, rooms, etc.)
        notes: Optional user notes
        created_at: Timestamp when record was created
    """
    amount_tl: Decimal
    screenshot_filename: str
    date_captured: date
    id: Optional[int] = None
    location: Optional[str] = None
    confidence: Optional[float] = None
    raw_ocr_text: Optional[str] = None
    property_details: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate market rate data after initialization"""
        # Validate amount is positive
        if self.amount_tl <= 0:
            raise ValueError(f"amount_tl must be positive, got {self.amount_tl}")
        
        # Validate screenshot_filename is provided
        if not self.screenshot_filename or not self.screenshot_filename.strip():
            raise ValueError("screenshot_filename must be a non-empty string")
        
        # Validate confidence score range (if provided)
        if self.confidence is not None:
            if not (0.0 <= self.confidence <= 1.0):
                raise ValueError(
                    f"confidence must be between 0.0-1.0, got {self.confidence}"
                )
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if OCR confidence is above threshold"""
        if self.confidence is None:
            return False
        return self.confidence >= threshold
    
    def __repr__(self) -> str:
        loc_str = f", {self.location}" if self.location else ""
        conf_str = f", conf={self.confidence:.2f}" if self.confidence else ""
        return (
            f"MarketRate({self.amount_tl} TL{loc_str}{conf_str}, "
            f"from {self.screenshot_filename})"
        )

