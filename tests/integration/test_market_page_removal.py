"""
Integration test for market comparison page removal.
This test verifies that the market comparison page is no longer accessible in the app.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_app_navigation_without_market_comparison():
    """Test that app navigation no longer includes market comparison page."""
    
    # Import the app module to check navigation
    import app
    
    # This test should fail initially (before removal) and pass after removal
    # We need to check that the market comparison page is not in the navigation
    
    # Since we can't easily test Streamlit UI directly, we'll check the app.py file
    app_file = Path(__file__).parent.parent.parent / "app.py"
    
    with open(app_file, 'r') as f:
        app_content = f.read()
    
    # These strings should not be present after removal
    assert "🏘️ Market Comparison" not in app_content, "Market Comparison page still exists in navigation"
    assert "Market Analysis" not in app_content, "Market Analysis page still exists in navigation"
    assert "screenshot_parser" not in app_content, "screenshot_parser still referenced in app.py"
    assert "ScreenshotParserService" not in app_content, "ScreenshotParserService still referenced in app.py"

def test_app_imports_without_market_components():
    """Test that app.py no longer imports market comparison components."""
    
    app_file = Path(__file__).parent.parent.parent / "app.py"
    
    with open(app_file, 'r') as f:
        app_content = f.read()
    
    # These imports should not be present after removal
    assert "from src.services.screenshot_parser import ScreenshotParserService" not in app_content, "ScreenshotParserService import still exists"
    assert "from src.models.market_rate import MarketRate" not in app_content, "MarketRate import still exists"

def test_app_session_state_without_screenshot_parser():
    """Test that app.py no longer initializes screenshot_parser in session state."""
    
    app_file = Path(__file__).parent.parent.parent / "app.py"
    
    with open(app_file, 'r') as f:
        app_content = f.read()
    
    # These session state initializations should not be present after removal
    assert "screenshot_parser" not in app_content, "screenshot_parser still initialized in session state"
    assert "ScreenshotParserService" not in app_content, "ScreenshotParserService still initialized in session state"

def test_app_page_routing_without_market_comparison():
    """Test that app.py no longer has market comparison page routing."""
    
    app_file = Path(__file__).parent.parent.parent / "app.py"
    
    with open(app_file, 'r') as f:
        app_content = f.read()
    
    # These page routing conditions should not be present after removal
    assert 'elif page == "🏘️ Market Comparison":' not in app_content, "Market Comparison page routing still exists"
    assert 'elif page == "Market Analysis":' not in app_content, "Market Analysis page routing still exists"

def test_app_ui_components_without_market_features():
    """Test that app.py no longer has market comparison UI components."""
    
    app_file = Path(__file__).parent.parent.parent / "app.py"
    
    with open(app_file, 'r') as f:
        app_content = f.read()
    
    # These UI components should not be present after removal
    assert "file_uploader" not in app_content or "screenshot" not in app_content.lower(), "Screenshot upload component still exists"
    assert "parse_screenshot" not in app_content, "parse_screenshot method still referenced"
    assert "market_rates" not in app_content, "market_rates still referenced in UI"
