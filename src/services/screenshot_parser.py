"""
Screenshot parser service using OCR to extract rental prices.
"""
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from decimal import Decimal
from typing import List, Optional
from datetime import date

from src.models import MarketRate
from src.services.exceptions import OCRError


class ScreenshotParserService:
    """
    Service for parsing rental prices from sahibinden.com screenshots using OCR.
    Handles Turkish number formats and location extraction.
    """
    
    def parse_screenshot(
        self, 
        image: Image.Image, 
        screenshot_filename: str
    ) -> List[MarketRate]:
        """
        Parse screenshot and extract rental prices.
        
        Args:
            image: PIL Image object
            screenshot_filename: Original filename for reference
            
        Returns:
            List of MarketRate objects extracted from screenshot
            
        Raises:
            OCRError: If OCR processing fails
        """
        try:
            # Preprocess image for better OCR
            processed_image = self.preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_image, lang='tur')
            
            # Extract prices and location
            prices = self.extract_all_prices_from_text(text)
            location = self.extract_location(text)
            
            # Create MarketRate objects
            market_rates = []
            for price in prices:
                market_rate = MarketRate(
                    amount_tl=price,
                    screenshot_filename=screenshot_filename,
                    date_captured=date.today(),
                    location=location,
                    confidence=None,  # Could add confidence calculation
                    raw_ocr_text=text
                )
                market_rates.append(market_rate)
            
            return market_rates
        
        except Exception as e:
            raise OCRError(f"Failed to parse screenshot: {e}")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        - Upscale image for better small text recognition
        - Convert to grayscale
        - Enhance contrast
        - Apply sharpening
        
        Args:
            image: Original PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        # Upscale image 2x for better OCR on small text (like map markers)
        width, height = image.size
        image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast significantly
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply edge enhancement for small text
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        return image
    
    def extract_price_from_text(self, text: str) -> Optional[Decimal]:
        """
        Extract first rental price from OCR text.
        
        Handles Turkish number formats:
        - 35.000 TL
        - 35,000 TL
        - 35000 TL
        - 30 bin (30 thousand in Turkish)
        
        Args:
            text: OCR text output
            
        Returns:
            Price as Decimal, or None if no price found
        """
        # Pattern for Turkish rental prices
        patterns = [
            # Turkish "bin" format (e.g., "30 bin" = 30,000)
            r'(\d{1,3})\s*(?:bin|BIN|Bin)',
            # With thousands separator
            r'(?:Kira|kira|KIRA)?\s*:?\s*(\d{1,3}[.,]?\d{3})\s*(?:TL|tl)',
            # Without separator
            r'(?:Kira|kira|KIRA)?\s*:?\s*(\d{4,6})\s*(?:TL|tl)',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1)
                
                if i == 0:  # "bin" format - multiply by 1000
                    try:
                        return Decimal(price_str) * 1000
                    except:
                        continue
                else:  # Regular TL format
                    # Remove thousand separators (. and ,)
                    price_str = price_str.replace('.', '').replace(',', '')
                    try:
                        return Decimal(price_str)
                    except:
                        continue
        
        return None
    
    def extract_all_prices_from_text(self, text: str) -> List[Decimal]:
        """
        Extract all rental prices from OCR text.
        
        Handles Turkish "bin" format and standard TL formats.
        
        Args:
            text: OCR text output
            
        Returns:
            List of prices as Decimal
        """
        prices = []
        
        # Find all price matches
        patterns = [
            (r'(\d{1,3})\s*(?:bin|BIN|Bin)', True),  # Turkish "bin" format (multiply by 1000)
            (r'(\d{1,3}[.,]\d{3})\s*(?:TL|tl)', False),  # With thousands separator
            (r'(\d{5,6})\s*(?:TL|tl)', False),  # Without separator (5-6 digits)
        ]
        
        for pattern, is_bin_format in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if is_bin_format:
                        # "bin" format: multiply by 1000
                        price = Decimal(match) * 1000
                    else:
                        # Regular TL format: remove thousand separators
                        price_str = match.replace('.', '').replace(',', '')
                        price = Decimal(price_str)
                    
                    # Filter reasonable rental prices (5,000 - 500,000 TL)
                    if Decimal("5000") <= price <= Decimal("500000"):
                        if price not in prices:  # Avoid duplicates
                            prices.append(price)
                except:
                    continue
        
        return sorted(prices)  # Return sorted for consistency
    
    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location/district from OCR text.
        Handles common Turkish districts and neighborhoods.
        
        Args:
            text: OCR text output
            
        Returns:
            Location string if found, None otherwise
        """
        # Common Turkish districts and neighborhoods
        districts = [
            # Istanbul
            'Kadıköy', 'Kadiköy', 'KADIKÖY',
            'Beşiktaş', 'Besiktas', 'BEŞİKTAŞ',
            'Şişli', 'Sisli', 'ŞİŞLİ',
            'Ümraniye', 'Umraniye', 'ÜMRAN İYE',
            'Maltepe', 'MALTEPE',
            'Ataşehir', 'Atasehir', 'ATAŞEH İR',
            'Üsküdar', 'Uskudar', 'ÜSKÜDAR',
            'Fatih', 'FATİH',
            'Bakırköy', 'Bakirkoy', 'BAKIRKÖY',
            'Beyoğlu', 'Beyoglu', 'BEYOĞLU',
            # Antalya
            'Konyaaltı', 'Konyaalti', 'KONYAALTI',
            'Muratpaşa', 'Muratpasa', 'MURATPAŞA',
            'Kepez', 'KEPEZ',
            'Pınarbaşı', 'Pinarbasi', 'PINARBAŞI',
            # Other major cities
            'Çankaya', 'Cankaya', 'ÇANKAYA',
            'Konak', 'KONAK',
            'Karşıyaka', 'Karsiyaka', 'KARŞIYAKA'
        ]
        
        for district in districts:
            if district.lower() in text.lower():
                return district
        
        return None
    
    def calculate_confidence_score(
        self, 
        image: Image.Image, 
        extracted_text: str
    ) -> float:
        """
        Calculate OCR confidence score (0.0-1.0).
        
        Simple heuristic based on:
        - Image quality (size, contrast)
        - Text extraction success (found prices, location)
        
        Args:
            image: Original image
            extracted_text: OCR output text
            
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Bonus for finding price
        if self.extract_price_from_text(extracted_text):
            confidence += 0.3
        
        # Bonus for finding location
        if self.extract_location(extracted_text):
            confidence += 0.1
        
        # Bonus for larger image (better quality)
        if image.width > 800 and image.height > 600:
            confidence += 0.1
        
        return min(confidence, 1.0)

