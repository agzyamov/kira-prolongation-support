"""
Unit tests for screenshot parser "bin" format improvements.
Tests the Turkish "bin" (thousand) format parsing.
"""
import pytest
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from src.services.screenshot_parser import ScreenshotParserService


class TestBinFormatParsing:
    """Test Turkish 'bin' format recognition"""
    
    def setup_method(self):
        """Setup test instance"""
        self.parser = ScreenshotParserService()
    
    def test_extract_single_bin_price(self):
        """Test extracting single 'bin' price"""
        text = "30 bin TL"
        result = self.parser.extract_price_from_text(text)
        assert result == Decimal("30000")
    
    def test_extract_bin_price_uppercase(self):
        """Test extracting 'BIN' uppercase"""
        text = "105 BIN"
        result = self.parser.extract_price_from_text(text)
        assert result == Decimal("105000")
    
    def test_extract_bin_price_mixed_case(self):
        """Test extracting 'Bin' mixed case"""
        text = "45 Bin"
        result = self.parser.extract_price_from_text(text)
        assert result == Decimal("45000")
    
    def test_extract_bin_with_no_space(self):
        """Test extracting 'bin' with minimal spacing"""
        text = "50bin"
        result = self.parser.extract_price_from_text(text)
        assert result == Decimal("50000")
    
    def test_extract_all_bin_prices(self):
        """Test extracting multiple 'bin' prices"""
        text = "Map shows: 30 bin, 105 bin, 45 bin, 50 bin"
        results = self.parser.extract_all_prices_from_text(text)
        
        expected = [
            Decimal("30000"),
            Decimal("45000"),
            Decimal("50000"),
            Decimal("105000")
        ]
        assert sorted(results) == expected
    
    def test_bin_format_priority_over_tl(self):
        """Test that bin format is checked first"""
        text = "30 bin - 35000 TL"
        # First match should be bin format
        result = self.parser.extract_price_from_text(text)
        assert result == Decimal("30000")
    
    def test_invalid_bin_numbers_filtered(self):
        """Test that unrealistic bin numbers are filtered"""
        # 3 bin = 3,000 TL (too low for rental)
        text = "3 bin"
        results = self.parser.extract_all_prices_from_text(text)
        assert len(results) == 0  # Should be filtered out
    
    def test_bin_with_trailing_text(self):
        """Test bin extraction with trailing text"""
        text = "Kiralık: 30 bin TL/ay"
        result = self.parser.extract_price_from_text(text)
        assert result == Decimal("30000")


class TestImagePreprocessing:
    """Test image preprocessing improvements"""
    
    def setup_method(self):
        """Setup test instance"""
        self.parser = ScreenshotParserService()
    
    def test_preprocess_upscales_image(self):
        """Test that preprocessing upscales the image 2x"""
        # Create a small test image
        original = Image.new('RGB', (100, 100), color='white')
        
        # Preprocess
        processed = self.parser.preprocess_image(original)
        
        # Should be 2x larger
        assert processed.size == (200, 200)
    
    def test_preprocess_converts_to_grayscale(self):
        """Test that preprocessing converts to grayscale"""
        # Create RGB image
        original = Image.new('RGB', (100, 100), color=(255, 128, 0))
        
        # Preprocess
        processed = self.parser.preprocess_image(original)
        
        # Should be grayscale (mode 'L')
        assert processed.mode == 'L'
    
    def test_preprocess_maintains_aspect_ratio(self):
        """Test that aspect ratio is maintained"""
        # Create non-square image
        original = Image.new('RGB', (200, 100), color='white')
        
        # Preprocess
        processed = self.parser.preprocess_image(original)
        
        # Aspect ratio should be same (2:1)
        assert processed.size[0] / processed.size[1] == 2.0


class TestLocationExtraction:
    """Test location extraction with Antalya cities"""
    
    def setup_method(self):
        """Setup test instance"""
        self.parser = ScreenshotParserService()
    
    def test_extract_pinarbasi(self):
        """Test extracting Pınarbaşı location"""
        text = "Pınarbaşı Mh. Kiralık Daire"
        result = self.parser.extract_location(text)
        assert result == "Pınarbaşı"
    
    def test_extract_pinarbasi_ascii(self):
        """Test extracting Pinarbasi (ASCII version)"""
        text = "Pinarbasi Mahallesi"
        result = self.parser.extract_location(text)
        assert result == "Pinarbasi"  # Returns ASCII version from list
    
    def test_extract_konyaalti(self):
        """Test extracting Konyaaltı location"""
        text = "Konyaaltı, Antalya"
        result = self.parser.extract_location(text)
        assert result == "Konyaaltı"
    
    def test_no_location_returns_none(self):
        """Test that no location returns None"""
        text = "30 bin TL rental price"
        result = self.parser.extract_location(text)
        assert result is None


class TestIntegration:
    """Integration tests with realistic scenarios"""
    
    def setup_method(self):
        """Setup test instance"""
        self.parser = ScreenshotParserService()
    
    def test_parse_map_marker_text(self):
        """Test parsing text that looks like map markers"""
        text = """
        Pınarbaşı Mh. Kiralık Daire
        30 bin
        105 bin  
        45 bin
        50 bin
        """
        
        # Extract all prices
        prices = self.parser.extract_all_prices_from_text(text)
        
        # Should find all 4 prices
        assert len(prices) == 4
        assert Decimal("30000") in prices
        assert Decimal("45000") in prices
        assert Decimal("50000") in prices
        assert Decimal("105000") in prices
        
        # Extract location
        location = self.parser.extract_location(text)
        assert location == "Pınarbaşı"
    
    def test_mixed_format_parsing(self):
        """Test parsing mixed TL and bin formats"""
        text = """
        Kiralık: 30 bin
        Depozito: 35.000 TL
        Aidat: 500 TL
        """
        
        prices = self.parser.extract_all_prices_from_text(text)
        
        # Should get all three prices
        assert Decimal("30000") in prices  # 30 bin
        assert Decimal("35000") in prices  # 35.000 TL


def test_confidence_score_with_bin_format():
    """Test confidence score calculation"""
    parser = ScreenshotParserService()
    
    # Create dummy image
    image = Image.new('RGB', (800, 600), color='white')
    
    # Text with bin format and location
    text = "30 bin TL - Pınarbaşı Mh."
    
    score = parser.calculate_confidence_score(image, text)
    
    # Should have high confidence (found price + location + good image size)
    assert score >= 0.9

