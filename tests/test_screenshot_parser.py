"""
Tests for screenshot parser service (OCR functionality).
These tests should FAIL initially (TDD approach).
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from PIL import Image


class TestPriceExtraction:
    """Test extracting rental prices from OCR text"""
    
    def test_extract_price_turkish_format(self):
        """Test extracting price in Turkish format: 35.000 TL"""
        # Arrange
        text = "Kira: 35.000 TL/ay"
        expected = Decimal("35000")
        
        # Act
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_price_from_text(text)
        
        # Assert
        assert result == expected
    
    def test_extract_price_without_dots(self):
        """Test extracting price without thousand separators: 35000 TL"""
        text = "Kira: 35000 TL"
        expected = Decimal("35000")
        
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_price_from_text(text)
        
        assert result == expected
    
    def test_extract_price_with_comma_separator(self):
        """Test extracting price with comma: 35,000 TL"""
        text = "Kira: 35,000 TL/aylık"
        expected = Decimal("35000")
        
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_price_from_text(text)
        
        assert result == expected
    
    def test_extract_price_multiple_prices_returns_first(self):
        """Test that first price is returned when multiple exist"""
        text = "Kira: 35.000 TL, Depozito: 35.000 TL"
        expected = Decimal("35000")
        
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_price_from_text(text)
        
        assert result == expected
    
    def test_extract_price_no_price_returns_none(self):
        """Test that None is returned when no price found"""
        text = "Bu bir test metnidir"
        
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_price_from_text(text)
        
        assert result is None
    
    def test_extract_price_very_high_amount(self):
        """Test extracting large rental amount"""
        text = "Kira: 125.500 TL"
        expected = Decimal("125500")
        
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_price_from_text(text)
        
        assert result == expected


class TestLocationExtraction:
    """Test extracting location/district from OCR text"""
    
    def test_extract_location_kadikoy(self):
        """Test extracting Kadıköy district"""
        text = "Kadıköy, İstanbul - 3+1 Daire"
        expected = "Kadıköy"
        
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_location(text)
        
        assert expected in result
    
    def test_extract_location_no_location_returns_none(self):
        """Test that None returned when no location found"""
        text = "35.000 TL"
        
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.extract_location(text)
        
        assert result is None


class TestImagePreprocessing:
    """Test image preprocessing for better OCR"""
    
    @patch('PIL.Image.open')
    def test_preprocess_converts_to_grayscale(self, mock_open):
        """Test that image is converted to grayscale"""
        # Arrange
        mock_image = MagicMock(spec=Image.Image)
        mock_image.convert.return_value = mock_image
        
        # Act
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        result = service.preprocess_image(mock_image)
        
        # Assert
        mock_image.convert.assert_called()
    
    def test_preprocess_image_increases_contrast(self):
        """Test that preprocessing enhances contrast"""
        pytest.skip("Requires PIL/Pillow implementation details")


class TestScreenshotParsing:
    """Test complete screenshot parsing workflow"""
    
    @patch('pytesseract.image_to_string')
    def test_parse_screenshot_returns_market_rates(self, mock_ocr):
        """Test parsing screenshot returns MarketRate objects"""
        # Arrange
        mock_ocr.return_value = "Kadıköy\nKira: 38.000 TL"
        mock_image = MagicMock(spec=Image.Image)
        filename = "test_screenshot.png"
        
        # Act
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        results = service.parse_screenshot(mock_image, filename)
        
        # Assert
        assert len(results) > 0
        assert results[0].amount_tl == Decimal("38000")
        assert results[0].screenshot_filename == filename
    
    @patch('pytesseract.image_to_string')
    def test_parse_screenshot_ocr_fails_raises_error(self, mock_ocr):
        """Test that OCR failure raises OCRError"""
        # Arrange
        mock_ocr.side_effect = Exception("OCR failed")
        mock_image = MagicMock(spec=Image.Image)
        
        # Act & Assert
        from src.services.screenshot_parser import ScreenshotParserService, OCRError
        service = ScreenshotParserService()
        
        with pytest.raises(OCRError):
            service.parse_screenshot(mock_image, "test.png")
    
    @patch('pytesseract.image_to_string')
    def test_parse_screenshot_no_prices_returns_empty_list(self, mock_ocr):
        """Test that screenshot with no prices returns empty list"""
        # Arrange
        mock_ocr.return_value = "Some text without prices"
        mock_image = MagicMock(spec=Image.Image)
        
        # Act
        from src.services.screenshot_parser import ScreenshotParserService
        service = ScreenshotParserService()
        results = service.parse_screenshot(mock_image, "test.png")
        
        # Assert
        assert len(results) == 0


class TestConfidenceScoring:
    """Test OCR confidence score calculation"""
    
    def test_calculate_confidence_high_quality_image(self):
        """Test confidence score for clear image"""
        pytest.skip("Requires OCR confidence implementation")
    
    def test_calculate_confidence_low_quality_image(self):
        """Test confidence score for blurry image"""
        pytest.skip("Requires OCR confidence implementation")

