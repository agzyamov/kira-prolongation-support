# Tasks: Rental Fee Negotiation Support Tool

**Branch**: `001-problem-statement-i`  
**Input**: Design documents from `/specs/001-problem-statement-i/`  
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Task Format

- **[ID]** Task description with specific file path
- **[P]** Can run in parallel (different files, no dependencies)
- **File paths**: Absolute paths from repository root

## Task Dependencies

```
Setup (T001-T004)
    ↓
Tests (T005-T010) [P]
    ↓
Models (T011-T015) [P]
    ↓
Storage (T016)
    ↓
Services (T017-T021) [Sequential - depend on storage]
    ↓
UI Components (T022-T026)
    ↓
Integration & Polish (T027-T030)
```

---

## Phase 3.1: Setup & Project Initialization (4 tasks) ✅ COMPLETE

- [x] **T001** - Initialize Python project structure
  - Create directory structure as defined in plan.md
  - Create all `__init__.py` files in: `src/`, `src/models/`, `src/services/`, `src/storage/`, `src/utils/`, `tests/`
  - Create `data/` directory with `.gitkeep`
  - Create `.streamlit/` directory
  - **Files**: Project root structure

- [x] **T002** - Create requirements.txt with dependencies
  - Add all dependencies from research.md:
    ```
    streamlit>=1.28.0
    plotly>=5.17.0
    kaleido>=0.2.1
    pytesseract>=0.3.10
    Pillow>=10.0.0
    pandas>=2.1.0
    requests>=2.31.0
    lxml>=4.9.0
    beautifulsoup4>=4.12.0
    pytest>=7.4.0
    ```
  - **File**: `/Users/rustemagziamov/kira-prolongation-support/requirements.txt`

- [x] **T003** - Create .gitignore file
  - Ignore: `data/*.db`, `*.pyc`, `__pycache__/`, `.venv/`, `.pytest_cache/`, `*.png`, `*.pdf` (exports), `data/` (except .gitkeep)
  - **File**: `/Users/rustemagziamov/kira-prolongation-support/.gitignore`

- [x] **T004** - Create Streamlit configuration
  - Create `.streamlit/config.toml` with theme settings
  - Set page title, favicon, layout (wide), theme (light)
  - **File**: `/Users/rustemagziamov/kira-prolongation-support/.streamlit/config.toml`

---

## Phase 3.2: Tests First (TDD) - 6 tasks [PARALLEL] ✅ COMPLETE

**CRITICAL**: These tests MUST be written and MUST FAIL before ANY implementation

- [x] **T005** [P] - Test: Exchange rate calculations
  - Write tests for USD conversion calculations
  - Test monthly average calculation
  - Test date range handling
  - File: `/Users/rustemagziamov/kira-prolongation-support/tests/test_calculations.py`
  - **Expected**: Tests fail (no implementation yet)

- [x] **T006** [P] - Test: Conditional rental agreement logic
  - Test conditional pricing rules evaluation
  - Test: "if rate < 40 then 35000" logic
  - Test multiple conditions
  - File: `/Users/rustemagziamov/kira-prolongation-support/tests/test_conditional_agreements.py`
  - **Expected**: Tests fail (no implementation yet)

- [x] **T007** [P] - Test: Percentage change calculations
  - Test rent increase percentage calculations
  - Test TL vs USD comparison logic
  - Test edge cases (zero values, negative)
  - File: `/Users/rustemagziamov/kira-prolongation-support/tests/test_calculations.py` (add to T005 file)
  - **Expected**: Tests fail (no implementation yet)

- [x] **T008** [P] - Test: Exchange rate service with mocks
  - Mock HTTP requests to TCMB and backup API
  - Test fallback logic when TCMB fails
  - Test caching behavior
  - File: `/Users/rustemagziamov/kira-prolongation-support/tests/test_exchange_rates.py`
  - **Expected**: Tests fail (no implementation yet)

- [x] **T009** [P] - Test: Screenshot parser with sample images
  - Create 2-3 mock screenshot images with known prices
  - Test price extraction regex patterns
  - Test Turkish number formatting (35.000 TL)
  - File: `/Users/rustemagziamov/kira-prolongation-support/tests/test_screenshot_parser.py`
  - **Expected**: Tests fail (no implementation yet)

- [x] **T010** [P] - Test: Data validation rules
  - Test date validation (start < end)
  - Test amount validation (> 0)
  - Test exchange rate validation
  - File: `/Users/rustemagziamov/kira-prolongation-support/tests/test_validators.py`
  - **Expected**: Tests fail (no implementation yet)

---

## Phase 3.3: Core Models (5 tasks) [PARALLEL] ✅ COMPLETE

- [x] **T011** [P] - Create RentalAgreement model
  - Implement dataclass from data-model.md
  - Add validation: start_date < end_date, base_amount_tl > 0
  - Handle conditional_rules JSON parsing
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/models/rental_agreement.py`

- [x] **T012** [P] - Create ExchangeRate model
  - Implement dataclass from data-model.md
  - Add validation: month 1-12, year reasonable, rate > 0
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/models/exchange_rate.py`

- [x] **T013** [P] - Create PaymentRecord model
  - Implement dataclass from data-model.md
  - Add validation: amounts > 0, valid date
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/models/payment_record.py`

- [x] **T014** [P] - Create MarketRate model
  - Implement dataclass from data-model.md
  - Add validation: amount_tl > 0, confidence 0-1
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/models/market_rate.py`

- [x] **T015** [P] - Create InflationData model
  - Implement dataclass from data-model.md
  - Add validation: month 1-12, year valid
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/models/inflation_data.py`

---

## Phase 3.4: Storage Layer (1 task) ✅ COMPLETE

- [x] **T016** - Implement SQLite DataStore
  - Create database schema from data-model.md (all 5 tables)
  - Implement all CRUD methods from contracts/service-interfaces.md
  - Add indexes for performance
  - Initialize database on first run
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/storage/data_store.py`
  - **Dependencies**: T011-T015 (needs model classes)

---

## Phase 3.5: Services (5 tasks) [SEQUENTIAL - each depends on T016]

- [ ] **T017** - Implement ExchangeRateService
  - Implement all methods from contracts/service-interfaces.md
  - TCMB API integration (XML parsing with lxml)
  - Fallback to exchangerate-api.io
  - Caching in DataStore
  - Error handling: ExchangeRateAPIError
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/services/exchange_rate_service.py`
  - **Dependencies**: T016 (needs DataStore)

- [ ] **T018** - Implement InflationService
  - Implement all methods from contracts/service-interfaces.md
  - CSV parsing with pandas
  - Legal maximum increase calculation
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/services/inflation_service.py`
  - **Dependencies**: T016 (needs DataStore)

- [ ] **T019** - Implement ScreenshotParserService
  - Implement all methods from contracts/service-interfaces.md
  - Pytesseract integration
  - Image preprocessing (grayscale, contrast, denoise)
  - Turkish number format parsing (regex: "35.000 TL" → 35000)
  - Confidence score calculation
  - Error handling: OCRError
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/services/screenshot_parser.py`
  - **Dependencies**: T016 (needs DataStore)

- [ ] **T020** - Implement CalculationService
  - Implement all methods from contracts/service-interfaces.md
  - USD conversion logic
  - Conditional pricing rule evaluation
  - Percentage change calculations
  - Market comparison statistics
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/services/calculation_service.py`
  - **Dependencies**: T016 (needs DataStore)

- [ ] **T021** - Implement ExportService
  - Implement all methods from contracts/service-interfaces.md
  - Plotly figure to PNG export (using Kaleido)
  - WhatsApp-optimized image generation (< 2MB)
  - Optional: PDF export
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/services/export_service.py`
  - **Dependencies**: None (pure utility)

---

## Phase 3.6: Utilities (2 tasks) [PARALLEL]

- [ ] **T022** [P] - Implement ChartGenerator utility
  - Create Plotly chart generation functions:
    - TL vs USD line chart over time
    - Payment comparison bar chart
    - Market rate comparison chart
  - Use colors that support negotiation position
  - Interactive hover tooltips
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/utils/chart_generator.py`
  - **Dependencies**: None (pure utility)

- [ ] **T023** [P] - Implement Validators utility
  - Input validation functions
  - Date validation helpers
  - Amount validation helpers
  - File: `/Users/rustemagziamov/kira-prolongation-support/src/utils/validators.py`
  - **Dependencies**: None (pure utility)

---

## Phase 3.7: Streamlit UI (4 tasks) [SEQUENTIAL]

- [ ] **T024** - Create main Streamlit app structure
  - Create app.py with sidebar navigation
  - Setup session state management
  - Initialize services
  - Page structure: Rental Agreements, Exchange Rates, Payments, Market Comparison, Negotiation Summary
  - File: `/Users/rustemagziamov/kira-prolongation-support/app.py`
  - **Dependencies**: T017-T021 (needs services)

- [ ] **T025** - Implement Rental Agreements UI
  - Form for adding/editing agreements
  - List view of all agreements
  - Conditional pricing rule input
  - File: `/Users/rustemagziamov/kira-prolongation-support/app.py` (section in main app)
  - **Dependencies**: T024

- [ ] **T026** - Implement Exchange Rates & Payments UI
  - Fetch exchange rates button
  - Date range selector
  - Display exchange rates table
  - Calculate and display payment records
  - File: `/Users/rustemagziamov/kira-prolongation-support/app.py` (section in main app)
  - **Dependencies**: T024

- [ ] **T027** - Implement Market Comparison & Screenshot Upload UI
  - File uploader for screenshots
  - OCR processing with progress indicator
  - Display parsed market rates
  - Manual edit/verify interface
  - File: `/Users/rustemagziamov/kira-prolongation-support/app.py` (section in main app)
  - **Dependencies**: T024

---

## Phase 3.8: Final Integration (3 tasks)

- [ ] **T028** - Implement Visualizations section
  - Generate charts using ChartGenerator
  - Display TL vs USD chart
  - Display market comparison chart
  - Interactive Plotly charts in Streamlit
  - File: `/Users/rustemagziamov/kira-prolongation-support/app.py` (section in main app)
  - **Dependencies**: T022, T024

- [ ] **T029** - Implement Negotiation Summary & Export
  - Calculate all statistics
  - Display key negotiation points
  - Export as PNG button
  - Display inflation data and legal maximum
  - File: `/Users/rustemagziamov/kira-prolongation-support/app.py` (section in main app)
  - **Dependencies**: T021, T024

- [ ] **T030** - Run manual testing via quickstart.md
  - Execute all 10 test scenarios from quickstart.md
  - Verify all features work end-to-end
  - Fix any bugs found
  - Test edge cases
  - **Dependencies**: ALL previous tasks

---

## Parallel Execution Examples

### Example 1: Tests (can run together)
All test tasks (T005-T010) can run in parallel since they create different test files:

```bash
# T005: tests/test_calculations.py
# T006: tests/test_conditional_agreements.py  
# T008: tests/test_exchange_rates.py
# T009: tests/test_screenshot_parser.py
# T010: tests/test_validators.py
```

### Example 2: Models (can run together)
All model tasks (T011-T015) can run in parallel since they create different files:

```bash
# T011: src/models/rental_agreement.py
# T012: src/models/exchange_rate.py
# T013: src/models/payment_record.py
# T014: src/models/market_rate.py
# T015: src/models/inflation_data.py
```

### Example 3: Utilities (can run together)
Utility tasks (T022-T023) are independent:

```bash
# T022: src/utils/chart_generator.py
# T023: src/utils/validators.py
```

---

## Task Summary

**Total Tasks**: 30

**By Phase**:
- Setup: 4 tasks
- Tests (TDD): 6 tasks
- Models: 5 tasks
- Storage: 1 task
- Services: 5 tasks
- Utilities: 2 tasks
- UI: 4 tasks
- Integration: 3 tasks

**Parallelizable Tasks**: 13 tasks marked [P]

**Estimated Time**:
- Setup: 1-2 hours
- Tests + Models: 2-3 hours (parallel)
- Storage + Services: 4-5 hours
- UI + Integration: 4-5 hours
- Testing: 2-3 hours
- **Total**: ~12-18 hours for full implementation

---

## Dependencies Summary

| Task Range | Depends On | Can Run |
|------------|-----------|---------|
| T001-T004 | Nothing | Immediately |
| T005-T010 | T001-T004 | Parallel |
| T011-T015 | T001-T004 | Parallel |
| T016 | T011-T015 | After models |
| T017-T021 | T016 | Sequential |
| T022-T023 | T001-T004 | Parallel |
| T024 | T017-T021 | After services |
| T025-T027 | T024 | Sequential |
| T028-T029 | T024, T022 | Sequential |
| T030 | ALL | Final |

---

## Implementation Notes

1. **TDD Approach**: Tests (T005-T010) MUST fail before implementing services
2. **Service Independence**: Services (T017-T021) can be implemented in any order after T016
3. **UI is Monolithic**: All UI tasks (T024-T029) modify `app.py` - must be sequential
4. **Manual Testing**: T030 is critical - use quickstart.md scenarios
5. **Constitution Compliance**:
   - Simple: No complex abstractions
   - Test what matters: Focus on calculations, conditional logic
   - Done over perfect: MVP first, iterate later
   - Context7: Use current library docs if needed

---

## Deployment Checklist (After T030)

- [ ] All tests pass
- [ ] Manual testing complete (10 scenarios)
- [ ] README.md updated with setup instructions
- [ ] requirements.txt complete
- [ ] .gitignore covers sensitive data
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Test deployed version
- [ ] Share URL with colleagues

---

**Ready for Implementation**: Use `/implement` command to execute tasks in order

---
*Generated from: plan.md, research.md, data-model.md, contracts/, quickstart.md*  
*Constitution v1.1.0 compliant*

