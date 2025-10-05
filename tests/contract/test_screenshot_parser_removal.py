"""
Contract test for ScreenshotParserService removal.
This test verifies that ScreenshotParserService is no longer available after removal.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_screenshot_parser_service_removed():
    """Test that ScreenshotParserService is no longer importable."""
    
    # This test should fail initially (before removal) and pass after removal
    with pytest.raises(ImportError):
        from src.services.screenshot_parser import ScreenshotParserService
        # If we get here, the service still exists and should be removed
        pytest.fail("ScreenshotParserService still exists and should be removed")

def test_screenshot_parser_file_removed():
    """Test that screenshot_parser.py file no longer exists."""
    
    screenshot_parser_file = Path(__file__).parent.parent.parent / "src" / "services" / "screenshot_parser.py"
    
    # This test should fail initially (before removal) and pass after removal
    assert not screenshot_parser_file.exists(), "screenshot_parser.py file still exists and should be removed"

def test_ocr_error_removed():
    """Test that OCRError exception is no longer available."""
    
    # This test should fail initially (before removal) and pass after removal
    with pytest.raises(ImportError):
        from src.services.exceptions import OCRError
        # If we get here, OCRError still exists and should be removed
        pytest.fail("OCRError still exists and should be removed")

def test_market_rate_model_removed():
    """Test that MarketRate model is no longer importable."""
    
    # This test should fail initially (before removal) and pass after removal
    with pytest.raises(ImportError):
        from src.models.market_rate import MarketRate
        # If we get here, MarketRate still exists and should be removed
        pytest.fail("MarketRate model still exists and should be removed")

def test_market_rate_file_removed():
    """Test that market_rate.py file no longer exists."""
    
    market_rate_file = Path(__file__).parent.parent.parent / "src" / "models" / "market_rate.py"
    
    # This test should fail initially (before removal) and pass after removal
    assert not market_rate_file.exists(), "market_rate.py file still exists and should be removed"
