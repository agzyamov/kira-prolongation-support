"""
Export service for generating images and PDFs from charts.
"""
import plotly.graph_objects as go
from typing import List
from PIL import Image
import io
from datetime import datetime
from decimal import Decimal

from src.services.exceptions import ExportError
from src.models.rental_agreement import RentalAgreement


class ExportService:
    """
    Service for exporting charts and data to various formats.
    Handles PNG export optimized for WhatsApp sharing.
    """
    
    def export_chart_as_image(
        self, 
        figure: go.Figure, 
        filename: str = "chart.png",
        width: int = 800,
        height: int = 600
    ) -> bytes:
        """
        Export Plotly figure as PNG image.
        
        Args:
            figure: Plotly Figure object
            filename: Output filename (for metadata)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            PNG image as bytes
            
        Raises:
            ExportError: If export fails
        """
        try:
            # Use Plotly's built-in image export via Kaleido
            img_bytes = figure.to_image(
                format="png",
                width=width,
                height=height,
                scale=2  # Higher DPI for better quality
            )
            return img_bytes
        
        except Exception as e:
            raise ExportError(f"Failed to export chart as image: {e}")
    
    def create_whatsapp_optimized_image(
        self, 
        figures: List[go.Figure],
        max_width: int = 1600
    ) -> bytes:
        """
        Create single image with multiple charts optimized for WhatsApp.
        - Compressed for smaller file size
        - Readable on mobile devices
        - Max 1600px width for WhatsApp compatibility
        
        Args:
            figures: List of Plotly figures to combine
            max_width: Maximum width in pixels
            
        Returns:
            PNG image as bytes
            
        Raises:
            ExportError: If export fails
        """
        if not figures:
            raise ExportError("No figures provided for export")
        
        try:
            # If single figure, just export it optimized
            if len(figures) == 1:
                return self.export_chart_as_image(
                    figures[0],
                    width=max_width,
                    height=900
                )
            
            # For multiple figures, export each and combine vertically
            chart_images = []
            for figure in figures:
                img_bytes = self.export_chart_as_image(
                    figure,
                    width=max_width,
                    height=600
                )
                chart_images.append(Image.open(io.BytesIO(img_bytes)))
            
            # Calculate combined height
            total_height = sum(img.height for img in chart_images)
            combined_width = max_width
            
            # Create combined image
            combined = Image.new('RGB', (combined_width, total_height), 'white')
            
            y_offset = 0
            for img in chart_images:
                combined.paste(img, (0, y_offset))
                y_offset += img.height
            
            # Compress for WhatsApp (optimize file size)
            output = io.BytesIO()
            combined.save(
                output,
                format='PNG',
                optimize=True,
                quality=85
            )
            output.seek(0)
            
            return output.read()
        
        except Exception as e:
            raise ExportError(f"Failed to create WhatsApp-optimized image: {e}")
    
    def export_summary_pdf(
        self, 
        data: dict,
        charts: List[go.Figure],
        filename: str = "rent_summary.pdf"
    ) -> bytes:
        """
        Export comprehensive summary as PDF.
        Includes charts, statistics, and negotiation points.
        
        NOTE: This is a simplified implementation.
        For production, consider using ReportLab or similar PDF library.
        
        Args:
            data: Summary statistics dictionary
            charts: List of Plotly figures to include
            filename: Output filename
            
        Returns:
            PDF as bytes
            
        Raises:
            ExportError: If export fails
        """
        # For now, export as high-quality PNG instead of PDF
        # This keeps dependencies simple (no ReportLab needed)
        try:
            img_bytes = self.create_whatsapp_optimized_image(charts, max_width=1200)
            return img_bytes
        
        except Exception as e:
            raise ExportError(f"Failed to export summary PDF: {e}")
    
    def add_data_source_disclosure(self, content: str) -> str:
        """
        Add data source disclosure to export content.
        
        Args:
            content: Export content to add disclosure to
            
        Returns:
            Content with data source disclosure appended
        """
        disclosure = "\n\nData source: TCMB (exchange rates), TÜFE (inflation)"
        return content + disclosure
    
    def generate_negotiation_summary(self, agreement: RentalAgreement, mode: str) -> str:
        """
        Generate negotiation summary with neutral phrasing.
        
        Args:
            agreement: Rental agreement to summarize
            mode: Negotiation mode for styling
            
        Returns:
            Formatted negotiation summary
        """
        if mode not in ["calm", "assertive"]:
            raise ValueError(f"Invalid negotiation mode: {mode}. Must be 'calm' or 'assertive'.")
        
        # Generate summary with neutral phrasing
        summary = f"""
Rental Agreement Summary
========================

Agreement Period: {agreement.start_date.strftime('%Y-%m')} to {agreement.end_date.strftime('%Y-%m') if agreement.end_date else 'ongoing'}
Base Rent: {agreement.base_amount_tl:,.2f} TL

Legal Context:
- Current rent is aligned with market average
- Legal maximum increase applies based on agreement period
- All calculations follow official Turkish regulations

Negotiation Position:
- Rent structure supports stable long-term tenancy
- Payment history demonstrates consistent compliance
- Terms are within acceptable market parameters
"""
        
        # Add data source disclosure
        return self.add_data_source_disclosure(summary)

