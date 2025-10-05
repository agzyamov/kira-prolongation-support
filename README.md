# 🏠 Kira Prolongation Support

Support tool for negotiating rental fee increases in Turkey's high-inflation environment.

## Problem

Turkish tenants face automatic maximum rent increases based on official inflation rates. This tool helps visualize rental payments in both Turkish Lira (TL) and USD equivalents to support negotiation for stable USD-equivalent rental fees.

## Solution

A data-driven application that:
- 📋 Tracks historical rental agreements and payments
- 💱 Converts TL amounts to USD equivalents using historical exchange rates
- 🏘️ Compares with market rental rates (via screenshot OCR from sahibinden.com)
- 📊 Calculates legal maximum increases based on official inflation
- 📈 Generates visualizations to support negotiations
- 📸 Exports charts for WhatsApp sharing

## Tech Stack

- **Language**: Python 3.11+
- **UI**: Streamlit (web app)
- **Charts**: Plotly + Kaleido
- **OCR**: Pytesseract
- **Storage**: SQLite
- **Testing**: pytest
- **Deployment**: Streamlit Cloud (free)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd kira-prolongation-support

# Create and activate virtual environment (required for Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (for screenshot parsing)
# macOS:
brew install tesseract tesseract-lang

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-tur

# Windows:
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. Run the Application

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # On macOS/Linux
# OR on Windows: .venv\Scripts\activate

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 3. Usage Flow

1. **Add Rental Agreements** (📋 Rental Agreements page)
   - Enter your historical rental agreements
   - Include conditional pricing rules if applicable

2. **Fetch Exchange Rates** (💱 Exchange Rates page)
   - Automatically fetch USD/TRY rates from TCMB
   - Or manually enter rates

3. **Generate Payment Records** (💰 Payment Records page)
   - Calculate TL and USD amounts for each month
   - View payment history

4. **Upload Market Data** (🏘️ Market Comparison page)
   - Upload screenshots from sahibinden.com
   - OCR will extract rental prices automatically

5. **View Visualizations** (📈 Visualizations page)
   - See TL vs USD charts
   - Compare with market rates

6. **Export for Negotiation** (🤝 Negotiation Summary page)
   - View key statistics
   - Export charts as PNG for WhatsApp

## Project Structure

```
.specify/             # Spec Kit metadata
  memory/
    constitution.md   # Development principles
specs/                # Feature specifications
  001-problem-statement-i/
    spec.md          # Feature specification
    plan.md          # Technical plan
    tasks.md         # Implementation tasks (30 tasks, all complete!)
    data-model.md    # Data schema
    contracts/       # Service interfaces
    quickstart.md    # Manual testing guide
src/                  # Source code
  models/            # Data models (RentalAgreement, ExchangeRate, etc.)
  services/          # Business logic services
  storage/           # SQLite database layer
  utils/             # Utilities (validators, chart generator)
tests/                # Test suite (TDD approach)
data/                 # SQLite database (kira.db)
.streamlit/           # Streamlit configuration
app.py                # Main Streamlit application
requirements.txt      # Python dependencies
```

## Features

### ✅ Implemented
- ✅ Rental agreement management with conditional pricing
- ✅ Exchange rate fetching from TCMB (Central Bank of Turkey) - official source only
- ✅ Payment record calculation (TL and USD)
- ✅ Screenshot OCR for market rental prices
- ✅ Interactive Plotly visualizations
- ✅ Export charts as PNG (WhatsApp-optimized)
- ✅ Inflation data import and legal max calculations
- ✅ SQLite persistence
- ✅ Streamlit web interface

### 🎯 Key Pages

1. **Rental Agreements**: Manage your rental history
2. **Exchange Rates**: Fetch/view USD/TRY rates
3. **Payment Records**: See calculated payments over time
4. **Market Comparison**: Upload and parse sahibinden.com screenshots
5. **Visualizations**: Interactive TL vs USD charts
6. **Negotiation Summary**: Key stats for landlord discussions
7. **Inflation Data**: Import official inflation rates

## Development

### Running Tests

```bash
pytest tests/
```

Note: Initial tests are written following TDD approach and will fail until full implementation.

### Database

SQLite database is automatically created at `data/kira.db` on first run.

### Deployment

Deploy to Streamlit Cloud:
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy from `app.py`

See: https://streamlit.io/cloud

## Constitution

This project follows a pragmatic, solo-developer constitution:

1. **Simple and Direct**: Write the simplest code that works
2. **Test What Matters**: Focus on confidence, not coverage
3. **Done Over Perfect**: Ship working features, polish later
4. **Use Context7**: Leverage up-to-date library documentation

See `.specify/memory/constitution.md` for details.

## Specification-Driven Development

This project uses [GitHub Spec Kit](https://github.com/github/spec-kit) for structured development:

- **Spec**: Problem statement and requirements
- **Plan**: Technical implementation strategy
- **Tasks**: Ordered, dependency-aware task list (30 tasks)
- **Contracts**: Service interface definitions

All specs are in `specs/001-problem-statement-i/`

### Available Commands

Use these commands in your AI assistant (Claude/Cursor):

- `/constitution` - View or update project principles
- `/specify` - Create a feature specification
- `/plan` - Generate implementation plan from spec
- `/tasks` - Break down plan into actionable tasks
- `/implement` - Execute the implementation

## Implementation Progress

**29 of 30 tasks complete!** ✅

- ✅ Phase 3.1: Setup (T001-T004)
- ✅ Phase 3.2: Tests (T005-T010)
- ✅ Phase 3.3: Models (T011-T015)
- ✅ Phase 3.4: Storage (T016)
- ✅ Phase 3.5: Services (T017-T021)
- ✅ Phase 3.6: Utilities (T022-T023)
- ✅ Phase 3.7-3.8: Streamlit UI (T024-T029)
- ⏳ T030: Manual testing (see `specs/001-problem-statement-i/quickstart.md`)

## License

Personal project for rental negotiation support.

## Acknowledgments

Built with:
- Streamlit for the UI
- Plotly for visualizations
- TCMB (Central Bank of Turkey) for exchange rate data
- Pytesseract for OCR capabilities
- GitHub Spec Kit for structured development
