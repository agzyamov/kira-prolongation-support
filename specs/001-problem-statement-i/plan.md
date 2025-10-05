# Implementation Plan: Rental Fee Negotiation Support Tool

**Branch**: `001-problem-statement-i` | **Date**: 2025-10-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-problem-statement-i/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✓
2. Fill Technical Context ✓
3. Fill the Constitution Check section ✓
4. Evaluate Constitution Check section ✓
5. Execute Phase 0 → research.md (IN PROGRESS)
6. Execute Phase 1 → contracts, data-model.md, quickstart.md
7. Re-evaluate Constitution Check section
8. Plan Phase 2 → Describe task generation approach
9. STOP - Ready for /tasks command
```

## Summary

Build a web application to help tenants in Turkey negotiate rental agreements by:
- Visualizing historical rent payments in both TL and USD equivalents
- Comparing current rent with market rates from sahibinden.com screenshots
- Showing legal maximum increases based on Turkish inflation data
- Exporting WhatsApp-friendly summaries for negotiations

**Key Constraints**:
- Zero paid infrastructure (free hosting required)
- Usable by non-developers
- Evergreen solution (works for any future period)
- Simple and direct implementation (per constitution)

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Streamlit, Plotly, Pytesseract, requests, pandas, SQLite  
**Storage**: SQLite (simple, no infrastructure, portable)  
**Testing**: pytest for calculations/logic, manual testing for UI  
**Target Platform**: Web browser (Chrome, Safari, Firefox) + Streamlit Cloud (free hosting)  
**Project Type**: Web application (Streamlit single-page app)  
**Performance Goals**: <3s page load, <5s screenshot parsing, responsive charts  
**Constraints**: Zero infrastructure costs, <100MB storage, works offline after initial data fetch  
**Scale/Scope**: Single user + ~10 colleagues, ~10 rental agreements, ~100 screenshots

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Simple and Direct Check
- [x] Solution is straightforward (single Python web app, minimal dependencies)
- [x] No unnecessary abstractions (direct data flow: input → calculate → visualize → export)
- [x] Code structure as simple as possible (monolithic Streamlit app, no microservices)

### II. Test What Matters Check
- [x] Test strategy focuses on critical paths (exchange rate calculations, USD conversions, conditional agreements)
- [x] Not over-testing simple functionality (manual UI testing, no unit tests for trivial getters)
- [x] Tests provide real confidence (test edge cases: missing data, invalid screenshots, API failures)

### III. Done Over Perfect Check
- [x] Feature scope focused on working functionality (core features only, no extras)
- [x] Not gold-plating (simple libraries, no premature optimization)
- [x] Plan enables quick shipping (MVP deployable in single iteration)

### IV. Use Context7 for Library Research Check
- [x] Will use Context7 MCP to research Streamlit best practices and current APIs
- [x] Will use Context7 for Plotly documentation (chart types, export options)
- [x] Will use Context7 for Pytesseract/OCR library current patterns

**Constitution Check Result**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)
```
specs/001-problem-statement-i/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (next)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/tasks command)
```

### Source Code (repository root)
```
kira-prolongation-support/
├── app.py                       # Main Streamlit app entry point
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rental_agreement.py    # RentalAgreement entity
│   │   ├── exchange_rate.py       # ExchangeRate entity  
│   │   ├── payment_record.py      # PaymentRecord entity
│   │   ├── market_rate.py         # MarketRate entity
│   │   └── inflation_data.py      # InflationData entity
│   ├── services/
│   │   ├── __init__.py
│   │   ├── exchange_rate_service.py   # Fetch USD/TL rates from TCMB/backup API
│   │   ├── inflation_service.py       # Fetch/store Turkish inflation data
│   │   ├── screenshot_parser.py       # Parse sahibinden screenshots with OCR
│   │   ├── calculation_service.py     # USD conversions, percentage changes
│   │   └── export_service.py          # PDF/image export for WhatsApp
│   ├── storage/
│   │   ├── __init__.py
│   │   └── data_store.py              # SQLite persistence layer
│   └── utils/
│       ├── __init__.py
│       ├── chart_generator.py         # Plotly chart creation
│       └── validators.py              # Input validation helpers
├── tests/
│   ├── __init__.py
│   ├── test_calculations.py           # Test USD conversions, percentages, conditional logic
│   ├── test_exchange_rates.py         # Test rate fetching and caching
│   ├── test_conditional_agreements.py # Test conditional pricing logic
│   └── test_screenshot_parser.py      # Test OCR parsing (mock images)
├── data/                               # Local data storage (gitignored)
│   ├── .gitkeep
│   └── user_data.db                    # SQLite database (created at runtime)
├── .streamlit/
│   └── config.toml                     # Streamlit configuration
├── .gitignore
├── requirements.txt                    # Python dependencies
├── README.md                           # Setup and usage instructions
└── .python-version                     # Python version (3.11)
```

**Structure Decision**: Single Streamlit web application - simplest architecture that meets all requirements. Streamlit handles both frontend and backend, eliminating need for separate API layer. Clear separation of concerns: models (data structures), services (business logic), storage (persistence), utils (helpers).

## Phase 0: Outline & Research

**Status**: Starting - will use Context7 MCP for library documentation

### Research Areas
1. **Streamlit**: Current best practices, deployment to Streamlit Cloud, file upload handling
2. **Plotly**: Chart types for comparison visualizations, static image export, WhatsApp optimization
3. **OCR Libraries**: Pytesseract vs alternatives, accuracy for Turkish text, image preprocessing
4. **Exchange Rate APIs**: TCMB API format, free alternatives, rate limiting strategies
5. **Turkish Inflation Data**: TUIK data sources, scraping strategies vs manual entry

### Output
- `research.md` with technology decisions, alternatives considered, and rationale
- Resolved any remaining technical uncertainties
- Library version recommendations with Context7-validated current APIs

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

### Outputs Required
1. **data-model.md**: Entity definitions based on spec (RentalAgreement, ExchangeRate, PaymentRecord, MarketRate, InflationData)
2. **contracts/**: Service interfaces (no REST API needed for Streamlit, but define service contracts)
3. **quickstart.md**: Manual testing guide for core user flows
4. **Agent context file**: Updated `.cursor/` file with tech stack and recent changes

### Data Model Entities (from spec)
- Rental Agreement (dates, amount, conditional rules)
- Exchange Rate Data (month/year, rate, source)
- Payment Record (calculated from agreements + exchange rates)
- Market Rate Data (from screenshot parsing)
- Inflation Data (period, rate, legal maximum)

### Service Contracts
- ExchangeRateService: fetch_rates(start_date, end_date) → List[ExchangeRate]
- InflationService: fetch_inflation(start_date, end_date) → List[InflationData]
- ScreenshotParser: parse_screenshot(image) → List[MarketRate]
- CalculationService: calculate_usd_equivalent(agreements, exchange_rates) → List[PaymentRecord]
- ExportService: export_summary(data) → bytes (PNG/PDF)

## Phase 2: Task Planning Approach

**This section describes what the /tasks command will do - DO NOT execute during /plan**

### Task Generation Strategy
- Setup tasks: Python environment, Streamlit config, directory structure
- Model tasks: Create entity classes (parallel - different files)
- Storage tasks: SQLite schema, data_store implementation
- Service tasks: Implement each service (some parallel, some sequential)
- UI tasks: Streamlit pages/components for each feature
- Integration tasks: Wire services together, add error handling
- Testing tasks: Write tests for calculations, conditional logic, edge cases
- Deployment tasks: requirements.txt, README, Streamlit Cloud setup

### Ordering Strategy
- TDD where it matters: Test calculation logic before implementing
- Bottom-up for architecture: Models → Storage → Services → UI
- Mark [P] for truly independent files (models, pure functions)
- Sequential for integrated components (services that depend on storage)

### Estimated Output
~20-25 tasks total, organized in phases:
- Phase 3.1: Setup (3-4 tasks)
- Phase 3.2: Core Models & Storage (4-5 tasks, mostly [P])
- Phase 3.3: Services (6-7 tasks, mixed [P] and sequential)
- Phase 3.4: UI Components (5-6 tasks)
- Phase 3.5: Testing & Deployment (3-4 tasks)

## Phase 3+: Future Implementation

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks following constitutional principles)  
**Phase 5**: Validation (run tests, manual testing via quickstart.md, deploy to Streamlit Cloud)

## Post-Design Constitution Check ✅

**Re-evaluation after Phase 1 design completion**:

### I. Simple and Direct Check
- [x] **Data Model**: 5 simple entities, no complex relationships ✓
- [x] **Services**: 6 focused services, each with clear purpose ✓
- [x] **Storage**: Single SQLite file, no distributed systems ✓
- [x] **Architecture**: Monolithic Streamlit app, simplest possible ✓
- **Result**: PASS - Design remains simple and direct

### II. Test What Matters Check
- [x] **Testing Focus**: Calculations, OCR, conditional logic identified ✓
- [x] **No Over-Testing**: UI testing manual, as appropriate ✓
- [x] **Quickstart Created**: 10 focused test scenarios ✓
- **Result**: PASS - Testing approach is pragmatic

### III. Done Over Perfect Check
- [x] **MVP Scope**: Core features only, no extras ✓
- [x] **Deliverable**: Can ship with basic features ✓
- [x] **No Gold-Plating**: Optional features marked clearly (TUIK scraping) ✓
- **Result**: PASS - Design enables quick delivery

### IV. Use Context7 Check
- [x] **Research Completed**: All libraries researched via Context7 ✓
- [x] **Current APIs**: Streamlit, Plotly, Pytesseract docs retrieved ✓
- [x] **Trust Scores**: All selected libraries 8.0+ ✓
- [x] **Code Examples**: 2000+ examples available for implementation ✓
- **Result**: PASS - Context7 used throughout planning

**Overall Post-Design Check**: ✅ **PASS** - All constitutional principles maintained

## Complexity Tracking

*No constitutional violations - all checks passed. Simple, direct solution.*

| Check | Status | Notes |
|-------|--------|-------|
| Simple architecture | ✓ | Single Streamlit app, 5 entities, 6 services |
| Minimal abstractions | ✓ | Direct service calls, no complex patterns |
| Test what matters | ✓ | Focus on calculations, conditional logic, OCR |
| Ship quickly | ✓ | MVP ready with ~25 tasks (Phase 2) |
| Use Context7 | ✓ | All libraries researched, current APIs validated |

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (Context7 used for all libraries)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning approach described (/plan command)
- [ ] Phase 3: Tasks generated (/tasks command - NEXT STEP)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS (re-evaluated below)
- [x] All technical decisions made: research.md complete
- [x] Complexity deviations documented: None (no violations)

**Artifacts Generated**:
- [x] plan.md (this file)
- [x] research.md (Context7-validated library research)
- [x] data-model.md (5 entities, SQLite schema)
- [x] contracts/service-interfaces.md (6 service contracts)
- [x] quickstart.md (10 test scenarios)
- [x] .cursor/rules/specify-rules.mdc (agent context updated)

---
*Based on Constitution v1.1.0 - See `.specify/memory/constitution.md`*
