"""
Test for market rate save button bug.

Bug: User reported that clicking "Save Rate" buttons doesn't save rates to database.
Root cause: Parsed rates are not stored in st.session_state, so they're lost when
the page reruns after clicking a save button.

Fix: Store parsed rates in st.session_state to persist across reruns.
"""
import re


def test_parsed_rates_stored_in_session_state():
    """Test that parsed rates are stored in session state for persistence"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find the market comparison OCR parsing section
    market_section = re.search(
        r'page == "🏘️ Market Comparison".*?except Exception as e:',
        content,
        re.DOTALL
    )
    
    assert market_section, "Market Comparison section not found"
    section_code = market_section.group(0)
    
    # Check that parsed rates are stored in session_state
    assert 'st.session_state' in section_code, \
        "Parsed rates must be stored in st.session_state to persist across reruns"
    
    # Check for the specific session state key for parsed rates (attribute or dict access)
    assert re.search(r'st\.session_state[\.\[][\'"]*\w*parsed.*rates?\w*[\'"]*[\]\)]?', section_code, re.IGNORECASE), \
        "Should store parsed rates in st.session_state.parsed_rates or st.session_state['parsed_rates']"


def test_save_buttons_outside_parse_button():
    """Test that save buttons work independently of parse button state"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find market comparison section
    market_section_match = re.search(
        r'(page == "🏘️ Market Comparison".*?)(?=elif page ==|\Z)',
        content,
        re.DOTALL
    )
    
    assert market_section_match, "Market Comparison section not found"
    section_code = market_section_match.group(1)
    
    # Find all button definitions (including f-strings)
    parse_button = re.search(r'st\.button\(["\'].*Parse Screenshot.*["\']\)', section_code)
    save_buttons = re.findall(r'st\.button\(.*Save Rate.*\)', section_code)
    
    assert parse_button, "Parse Screenshot button not found"
    assert len(save_buttons) > 0, "Save Rate buttons not found"
    
    # Verify save buttons are outside the parse button's conditional
    # They should appear after the parse button's exception handler block
    parse_block_end = section_code.find('st.exception(e)', parse_button.start())
    if parse_block_end == -1:
        parse_block_end = section_code.find('except Exception as e:', parse_button.start())
        if parse_block_end != -1:
            # Find the end of this except block
            parse_block_end = section_code.find('\n    \n', parse_block_end)
    
    if parse_block_end != -1:
        # Check that save buttons come after the parse block
        for save_match in re.finditer(r'st\.button\(.*Save Rate.*\)', section_code):
            assert save_match.start() > parse_block_end, \
                "Save Rate buttons should be outside the Parse Screenshot conditional block"


def test_session_state_initialization():
    """Test that session state for parsed rates is properly initialized"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check for session state initialization pattern
    assert re.search(
        r'if\s+["\']parsed.*rates?["\'].*not in.*st\.session_state',
        content,
        re.IGNORECASE | re.DOTALL
    ), "Should initialize session state for parsed rates if not present"

