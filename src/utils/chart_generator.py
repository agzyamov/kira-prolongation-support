"""
Chart generation utilities using Plotly.
Creates visualizations that support rent negotiation position.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict
from decimal import Decimal

from src.models import PaymentRecord, MarketRate


class ChartGenerator:
    """
    Utility class for generating Plotly charts.
    Color scheme emphasizes stable USD rent to support negotiation.
    """
    
    # Color scheme
    COLOR_TL = "#E74C3C"  # Red - emphasizes TL increase
    COLOR_USD = "#27AE60"  # Green - emphasizes USD stability
    COLOR_MARKET = "#3498DB"  # Blue - market rates
    COLOR_LEGAL = "#F39C12"  # Orange - legal maximum
    
    def create_tl_vs_usd_chart(
        self, 
        payments: List[PaymentRecord],
        title: str = "Rental Payments: TL vs USD Equivalent"
    ) -> go.Figure:
        """
        Create line chart showing TL amounts vs USD equivalents over time.
        
        Args:
            payments: List of payment records
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        # Sort payments by date
        sorted_payments = sorted(payments, key=lambda p: (p.year, p.month))
        
        # Extract data
        periods = [f"{p.year}-{p.month:02d}" for p in sorted_payments]
        tl_amounts = [float(p.amount_tl) for p in sorted_payments]
        usd_amounts = [float(p.amount_usd) for p in sorted_payments]
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # TL line (primary y-axis)
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=tl_amounts,
                name="Rent (TL)",
                line=dict(color=self.COLOR_TL, width=3),
                mode='lines+markers',
                hovertemplate='<b>%{x}</b><br>TL: %{y:,.0f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        # USD line (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=usd_amounts,
                name="Rent (USD)",
                line=dict(color=self.COLOR_USD, width=3),
                mode='lines+markers',
                hovertemplate='<b>%{x}</b><br>USD: $%{y:,.2f}<extra></extra>'
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            title=title,
            title_font_size=18,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
            template="plotly_white"
        )
        
        # Update axes
        fig.update_xaxes(title_text="Period")
        fig.update_yaxes(title_text="Turkish Lira (TL)", secondary_y=False)
        fig.update_yaxes(title_text="US Dollars (USD)", secondary_y=True)
        
        return fig
    
    def create_payment_comparison_bar_chart(
        self, 
        payments: List[PaymentRecord],
        title: str = "Rent Comparison by Period"
    ) -> go.Figure:
        """
        Create grouped bar chart comparing TL and USD amounts.
        
        Args:
            payments: List of payment records
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        # Sort payments
        sorted_payments = sorted(payments, key=lambda p: (p.year, p.month))
        
        # Extract data
        periods = [f"{p.year}-{p.month:02d}" for p in sorted_payments]
        tl_amounts = [float(p.amount_tl) for p in sorted_payments]
        
        # Normalize USD to same scale as TL (for visual comparison)
        # Scale USD by average exchange rate
        avg_rate = sum(float(p.amount_tl / p.amount_usd) for p in sorted_payments) / len(sorted_payments)
        usd_scaled = [float(p.amount_usd) * avg_rate for p in sorted_payments]
        
        fig = go.Figure()
        
        # TL bars
        fig.add_trace(go.Bar(
            x=periods,
            y=tl_amounts,
            name='Rent (TL)',
            marker_color=self.COLOR_TL,
            hovertemplate='<b>%{x}</b><br>TL: %{y:,.0f}<extra></extra>'
        ))
        
        # USD bars (scaled)
        fig.add_trace(go.Bar(
            x=periods,
            y=usd_scaled,
            name=f'Rent (USD × {avg_rate:.1f})',
            marker_color=self.COLOR_USD,
            hovertemplate='<b>%{x}</b><br>USD Scaled: %{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            title_font_size=18,
            xaxis_title="Period",
            yaxis_title="Amount (TL)",
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
            template="plotly_white"
        )
        
        return fig
    
    def create_market_comparison_chart(
        self, 
        user_rent: Decimal,
        market_rates: List[MarketRate],
        title: str = "Your Rent vs Market Rates"
    ) -> go.Figure:
        """
        Create chart comparing user's rent with market rates.
        
        Args:
            user_rent: User's current/proposed rent
            market_rates: List of market rental rates
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        if not market_rates:
            # Return empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No market data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Extract market amounts
        market_amounts = [float(rate.amount_tl) for rate in market_rates]
        market_avg = sum(market_amounts) / len(market_amounts)
        
        # Create box plot with user's rent
        fig = go.Figure()
        
        # Market rates box plot
        fig.add_trace(go.Box(
            y=market_amounts,
            name='Market Rates',
            marker_color=self.COLOR_MARKET,
            boxmean='sd'
        ))
        
        # User's rent as horizontal line
        fig.add_hline(
            y=float(user_rent),
            line_dash="dash",
            line_color=self.COLOR_TL,
            line_width=3,
            annotation_text=f"Your Rent: {user_rent:,.0f} TL",
            annotation_position="right"
        )
        
        # Market average line
        fig.add_hline(
            y=market_avg,
            line_dash="dot",
            line_color=self.COLOR_MARKET,
            line_width=2,
            annotation_text=f"Market Avg: {market_avg:,.0f} TL",
            annotation_position="left"
        )
        
        fig.update_layout(
            title=title,
            title_font_size=18,
            yaxis_title="Monthly Rent (TL)",
            showlegend=False,
            height=500,
            template="plotly_white"
        )
        
        return fig
    
    def create_negotiation_summary_chart(
        self, 
        data: Dict
    ) -> go.Figure:
        """
        Create summary chart with key negotiation points.
        
        Args:
            data: Dictionary with negotiation data:
                - current_tl: Current rent in TL
                - proposed_tl: Proposed rent in TL
                - current_usd: Current rent in USD
                - proposed_usd: Proposed rent in USD
                - market_avg: Market average rent
                - legal_max: Legal maximum rent
                
        Returns:
            Plotly Figure object
        """
        categories = ['Current', 'Proposed', 'Market Avg', 'Legal Max']
        tl_values = [
            float(data.get('current_tl', 0)),
            float(data.get('proposed_tl', 0)),
            float(data.get('market_avg', 0)),
            float(data.get('legal_max', 0))
        ]
        
        fig = go.Figure()
        
        # Bar chart
        fig.add_trace(go.Bar(
            x=categories,
            y=tl_values,
            marker=dict(
                color=[self.COLOR_USD, self.COLOR_TL, self.COLOR_MARKET, self.COLOR_LEGAL],
                opacity=0.7
            ),
            text=[f"{v:,.0f} TL" for v in tl_values],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>%{y:,.0f} TL<extra></extra>'
        ))
        
        fig.update_layout(
            title="Rent Negotiation Summary",
            title_font_size=18,
            yaxis_title="Monthly Rent (TL)",
            showlegend=False,
            height=500,
            template="plotly_white"
        )
        
        return fig

