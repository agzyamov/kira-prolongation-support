"""
Test that file uploaders have unique keys to prevent duplicate widget issues.

Bug: User reported "Browse files" button not working in Market Comparison.
Root cause: st.file_uploader without key parameter can cause duplicate widgets.
Fix: Added unique keys to all file_uploader components.
"""
import re


def test_market_screenshot_uploader_has_key():
    """Test that market screenshot uploader has a unique key"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find the market comparison file uploader
    market_section = re.search(
        r'page == "🏘️ Market Comparison".*?st\.file_uploader\((.*?)\)',
        content,
        re.DOTALL
    )
    
    assert market_section, "Market Comparison file uploader not found"
    uploader_args = market_section.group(1)
    
    # Check that it has a key parameter
    assert 'key=' in uploader_args, "Market screenshot uploader missing 'key' parameter"
    assert 'market_screenshot_uploader' in uploader_args, "Market screenshot uploader has wrong key"


def test_inflation_csv_uploader_has_key():
    """Test that inflation CSV uploader has a unique key"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find the inflation data file uploader
    inflation_section = re.search(
        r'page == "📊 Inflation Data".*?st\.file_uploader\((.*?)\)',
        content,
        re.DOTALL
    )
    
    assert inflation_section, "Inflation Data file uploader not found"
    uploader_args = inflation_section.group(1)
    
    # Check that it has a key parameter
    assert 'key=' in uploader_args, "Inflation CSV uploader missing 'key' parameter"
    assert 'inflation_csv_uploader' in uploader_args, "Inflation CSV uploader has wrong key"


def test_all_file_uploaders_have_unique_keys():
    """Test that all file_uploader calls have unique keys"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find all file_uploader calls
    uploaders = re.findall(
        r'st\.file_uploader\((.*?)\)',
        content,
        re.DOTALL
    )
    
    assert len(uploaders) > 0, "No file uploaders found in app.py"
    
    # Extract keys
    keys = []
    for uploader in uploaders:
        key_match = re.search(r'key=["\']([^"\']+)["\']', uploader)
        if key_match:
            keys.append(key_match.group(1))
        else:
            # Fail if any uploader doesn't have a key
            assert False, f"File uploader missing key parameter: {uploader[:100]}"
    
    # Check all keys are unique
    assert len(keys) == len(set(keys)), f"Duplicate keys found: {keys}"
    
    print(f"✓ All {len(keys)} file uploaders have unique keys: {keys}")

