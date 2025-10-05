# Quickstart Guide: Rental Fee Negotiation Support Tool

## Overview
This tool helps Turkish tenants visualize their rental payment history in both Turkish Lira (TL) and USD equivalents, compare with market rates, and generate professional negotiation materials.

## Prerequisites
- Python 3.13+
- Internet connection (for TCMB API access)
- Screenshots from sahibinden.com (optional, for market comparison)

## Installation

### 1. Clone and Setup
```bash
git clone <repository-url>
cd kira-prolongation-support
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Basic Usage

### Step 1: Enter Rental Agreement History
1. **Click "Add Rental Agreement"**
2. **Fill in the form**:
   - Start Date: When the agreement began
   - End Date: When it ended (leave blank if ongoing)
   - Base Amount (TL): Monthly rent in Turkish Lira
   - Conditional Rules (optional): For agreements with exchange rate triggers
   - Notes: Any additional information

**Example Agreement**:
- Start Date: 2022-11-01
- End Date: 2023-10-31
- Base Amount: 15000 TL
- Notes: "First agreement period"

### Step 2: Add Market Comparison Data (Optional)
1. **Take a screenshot** of sahibinden.com showing rental listings in your area
2. **Click "Upload Screenshot"**
3. **Select your image file**
4. **Review parsed amounts** and adjust if needed
5. **Click "Save Market Rates"**

### Step 3: Generate Negotiation Materials
1. **Select Negotiation Mode**:
   - **Calm**: Professional, subdued presentation
   - **Assertive**: Bold, attention-grabbing presentation
2. **Click "Generate Summary"**
3. **Review the charts and summary**
4. **Export as needed**:
   - PNG for WhatsApp sharing
   - PDF for formal documents

## Advanced Features

### Conditional Rental Agreements
For agreements with exchange rate triggers:

**Example**: "If USD < 40 TL: 35,000 TL, If USD >= 40 TL: 40,000 TL"

1. **Select "Add Conditional Rules"**
2. **Enter the conditions**:
   - Condition: "USD < 40"
   - Amount: 35000
   - Add another condition: "USD >= 40"
   - Amount: 40000
3. **Save the agreement**

The system will automatically calculate the correct rent based on historical exchange rates.

### Legal Context Display
The system automatically shows:
- **Pre-July 2024**: "+25% (limit until July 2024)"
- **Post-July 2024**: "+CPI (Yearly TÜFE)"

This helps you understand the legal maximum increase your landlord can request.

### Data Source Attribution
All exported materials include:
"Data source: TCMB (exchange rates), TÜFE (inflation)"

This provides transparency and credibility for your negotiation materials.

## Troubleshooting

### Common Issues

#### "Exchange rate data unavailable"
- **Cause**: TCMB API is temporarily down
- **Solution**: The system will prompt for manual entry of exchange rates

#### "Screenshot parsing failed"
- **Cause**: Image quality or format issues
- **Solution**: 
  - Ensure screenshot is clear and well-lit
  - Try cropping to focus on rental amounts
  - Manually enter market rates if parsing continues to fail

#### "No legal rule applies to this date"
- **Cause**: Agreement date outside known legal periods
- **Solution**: Contact support or manually specify the legal rule

### Data Backup
- **Export your data** regularly using the export functionality
- **Screenshot files** are stored locally and should be backed up
- **Database file** (SQLite) can be copied for backup

## Example Workflow

### Scenario: Preparing for 2025 Rent Negotiation

1. **Enter Historical Agreements**:
   - 2022-2023: 15,000 TL/month
   - 2023-2024: 25,000 TL/month
   - 2024-2025: 31,000 TL/month (with conditional rules)

2. **Add Market Data**:
   - Upload screenshot of current sahibinden.com listings
   - Review parsed amounts (e.g., 28,000-35,000 TL range)

3. **Generate Materials**:
   - Select "Assertive" mode for strong presentation
   - Review charts showing USD stability over time
   - Check legal maximum increase (TÜFE-based)

4. **Export and Share**:
   - Export as PNG for WhatsApp
   - Include data source attribution
   - Share with landlord during negotiation

## Tips for Effective Negotiations

### Key Arguments to Highlight
1. **USD Stability**: Show that your USD-equivalent rent has remained stable
2. **Market Comparison**: Demonstrate your rent is aligned with market rates
3. **Legal Context**: Reference the legal maximum increase allowed
4. **Data Transparency**: Emphasize official TCMB data sources

### Presentation Tips
- **Calm Mode**: Use for professional, diplomatic negotiations
- **Assertive Mode**: Use when you need to emphasize your position strongly
- **Visual Impact**: Charts are more persuasive than raw numbers
- **Source Credibility**: Always include data source attribution

## Support

### Getting Help
- **Check the troubleshooting section** above
- **Review the user manual** for detailed explanations
- **Contact support** if issues persist

### Feature Requests
- **Submit feedback** through the application
- **Request new features** via the feedback form
- **Report bugs** with detailed descriptions

## Data Privacy

### Your Data
- **All data stored locally** on your device
- **No external transmission** except to TCMB API
- **No user accounts** or authentication required
- **Export functionality** for data portability

### Data Sources
- **TCMB**: Official Turkish Central Bank data
- **TÜFE**: Official Turkish inflation data
- **Market Data**: User-provided screenshots (no liability for accuracy)

## Legal Disclaimer

This tool is for informational purposes only. It does not constitute legal advice. Always consult with a legal professional for specific rental law questions. Market data accuracy depends on user-provided screenshots and is not guaranteed by the application.