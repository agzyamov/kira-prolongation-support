# Tasks: Remove Market Comparison Feature

**Input**: Design documents from `/specs/002-i-need-u/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
2. Load optional design documents ✓
3. Generate tasks by category ✓
4. Apply task rules ✓
5. Number tasks sequentially ✓
6. Generate dependency graph ✓
7. Create parallel execution examples ✓
8. Validate task completeness ✓
9. Return: SUCCESS (tasks ready for execution) ✓
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup & Preparation
- [x] T001 Create backup of existing market data in database
- [x] T002 Update requirements.txt to remove EasyOCR dependencies
- [x] T003 [P] Update README.md to remove market comparison references

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test for ScreenshotParserService removal in tests/contract/test_screenshot_parser_removal.py
- [x] T005 [P] Contract test for DataStore market rate methods removal in tests/contract/test_data_store_market_removal.py
- [x] T006 [P] Integration test for market comparison page removal in tests/integration/test_market_page_removal.py
- [x] T007 [P] Integration test for export service market data removal in tests/integration/test_export_market_removal.py
- [x] T008 [P] Regression test for core functionality preservation in tests/integration/test_core_functionality_regression.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T009 [P] Remove ScreenshotParserService from src/services/screenshot_parser.py
- [x] T010 [P] Remove MarketRate model from src/models/market_rate.py
- [x] T011 [P] Remove OCRError exception from src/services/exceptions.py
- [x] T012 [P] Remove market rate methods from src/storage/data_store.py
- [x] T013 [P] Update ExportService to remove market rate parameters in src/services/export_service.py
- [x] T014 [P] Update ChartGenerator to remove market comparison overlays in src/utils/chart_generator.py
- [x] T015 Remove market comparison page from app.py navigation and routing
- [x] T016 Remove ScreenshotParserService initialization from app.py

## Phase 3.4: Database & Integration
- [x] T017 Create database migration to remove market_rates table
- [x] T018 [P] Update database initialization to exclude market_rates table
- [x] T019 [P] Remove market rate related imports from all service files
- [x] T020 [P] Update service initialization in app.py to remove screenshot_parser

## Phase 3.5: UI & Navigation
- [x] T021 [P] Remove market comparison page UI components from app.py
- [x] T022 [P] Update sidebar navigation to remove market comparison option
- [x] T023 [P] Remove market comparison related error handling from UI
- [x] T024 [P] Update page routing logic to remove market comparison routes

## Phase 3.6: Testing & Validation
- [x] T025 [P] Update existing tests to remove market comparison references
- [x] T026 [P] Add regression tests for core functionality in tests/unit/test_core_regression.py
- [ ] T027 [P] Update integration tests to remove market comparison scenarios
- [ ] T028 [P] Add tests for graceful handling of missing market data
- [ ] T029 Run comprehensive test suite to ensure no regressions
- [ ] T030 Execute quickstart.md test scenarios

## Phase 3.7: Documentation & Cleanup
- [ ] T031 [P] Update app.py comments to remove market comparison references
- [ ] T032 [P] Update service documentation to remove market comparison methods
- [ ] T033 [P] Clean up any remaining market comparison references in code
- [ ] T034 [P] Update error messages to remove market comparison references
- [ ] T035 [P] Remove unused imports and dependencies from all files

## Dependencies
- Tests (T004-T008) before implementation (T009-T016)
- T009 blocks T015, T016 (ScreenshotParserService removal)
- T010 blocks T012 (MarketRate model removal)
- T011 blocks T019 (OCRError removal)
- T012 blocks T017 (DataStore methods removal)
- T013 blocks T020 (ExportService updates)
- T014 blocks T020 (ChartGenerator updates)
- T015 blocks T021, T022 (UI removal)
- T016 blocks T020 (Service initialization)
- Implementation before integration (T017-T024)
- Integration before testing (T025-T030)
- Testing before documentation (T031-T035)

## Parallel Execution Examples

### Phase 3.1 Setup (T002-T003 can run in parallel):
```
Task: "Update requirements.txt to remove EasyOCR dependencies"
Task: "Update README.md to remove market comparison references"
```

### Phase 3.2 Tests (T004-T008 can run in parallel):
```
Task: "Contract test for ScreenshotParserService removal in tests/contract/test_screenshot_parser_removal.py"
Task: "Contract test for DataStore market rate methods removal in tests/contract/test_data_store_market_removal.py"
Task: "Integration test for market comparison page removal in tests/integration/test_market_page_removal.py"
Task: "Integration test for export service market data removal in tests/integration/test_export_market_removal.py"
Task: "Regression test for core functionality preservation in tests/integration/test_core_functionality_regression.py"
```

### Phase 3.3 Core Implementation (T009-T014 can run in parallel):
```
Task: "Remove ScreenshotParserService from src/services/screenshot_parser.py"
Task: "Remove MarketRate model from src/models/market_rate.py"
Task: "Remove OCRError exception from src/services/exceptions.py"
Task: "Remove market rate methods from src/storage/data_store.py"
Task: "Update ExportService to remove market rate parameters in src/services/export_service.py"
Task: "Update ChartGenerator to remove market comparison overlays in src/utils/chart_generator.py"
```

### Phase 3.4 Integration (T018-T020 can run in parallel):
```
Task: "Update database initialization to exclude market_rates table"
Task: "Remove market rate related imports from all service files"
Task: "Update service initialization in app.py to remove screenshot_parser"
```

### Phase 3.5 UI (T021-T024 can run in parallel):
```
Task: "Remove market comparison page UI components from app.py"
Task: "Update sidebar navigation to remove market comparison option"
Task: "Remove market comparison related error handling from UI"
Task: "Update page routing logic to remove market comparison routes"
```

### Phase 3.6 Testing (T025-T028 can run in parallel):
```
Task: "Update existing tests to remove market comparison references"
Task: "Add regression tests for core functionality in tests/unit/test_core_regression.py"
Task: "Update integration tests to remove market comparison scenarios"
Task: "Add tests for graceful handling of missing market data"
```

### Phase 3.7 Documentation (T031-T035 can run in parallel):
```
Task: "Update app.py comments to remove market comparison references"
Task: "Update service documentation to remove market comparison methods"
Task: "Clean up any remaining market comparison references in code"
Task: "Update error messages to remove market comparison references"
Task: "Remove unused imports and dependencies from all files"
```

## Task Details

### T001: Create backup of existing market data
**File**: `scripts/backup_market_data.py`
**Description**: Create a backup script to preserve existing market data before removal
**Dependencies**: None

### T002: Update requirements.txt
**File**: `requirements.txt`
**Description**: Remove easyocr==1.7.2 and Pillow==10.4.0 dependencies
**Dependencies**: None

### T003: Update README.md
**File**: `README.md`
**Description**: Remove market comparison references from documentation
**Dependencies**: None

### T004: Contract test for ScreenshotParserService removal
**File**: `tests/contract/test_screenshot_parser_removal.py`
**Description**: Test that ScreenshotParserService is no longer importable
**Dependencies**: None

### T005: Contract test for DataStore market rate methods removal
**File**: `tests/contract/test_data_store_market_removal.py`
**Description**: Test that market rate methods are removed from DataStore
**Dependencies**: None

### T006: Integration test for market comparison page removal
**File**: `tests/integration/test_market_page_removal.py`
**Description**: Test that market comparison page is not accessible
**Dependencies**: None

### T007: Integration test for export service market data removal
**File**: `tests/integration/test_export_market_removal.py`
**Description**: Test that export service no longer accepts market rate parameters
**Dependencies**: None

### T008: Regression test for core functionality preservation
**File**: `tests/integration/test_core_functionality_regression.py`
**Description**: Test that all core rental tracking functionality remains intact
**Dependencies**: None

### T009: Remove ScreenshotParserService
**File**: `src/services/screenshot_parser.py`
**Description**: Delete the entire ScreenshotParserService file
**Dependencies**: T004

### T010: Remove MarketRate model
**File**: `src/models/market_rate.py`
**Description**: Delete the entire MarketRate model file
**Dependencies**: T005

### T011: Remove OCRError exception
**File**: `src/services/exceptions.py`
**Description**: Remove OCRError class from exceptions
**Dependencies**: T004

### T012: Remove market rate methods from DataStore
**File**: `src/storage/data_store.py`
**Description**: Remove all market rate related methods from DataStore class
**Dependencies**: T005, T010

### T013: Update ExportService
**File**: `src/services/export_service.py`
**Description**: Remove market_rates parameter from generate_negotiation_summary method
**Dependencies**: T007

### T014: Update ChartGenerator
**File**: `src/utils/chart_generator.py`
**Description**: Remove market_rates parameter from create_tl_usd_chart method
**Dependencies**: T007

### T015: Remove market comparison page from app.py
**File**: `app.py`
**Description**: Remove market comparison page routing and UI components
**Dependencies**: T009, T010, T011

### T016: Remove ScreenshotParserService initialization
**File**: `app.py`
**Description**: Remove ScreenshotParserService initialization from session state
**Dependencies**: T009

### T017: Create database migration
**File**: `scripts/migrate_remove_market_rates.py`
**Description**: Create migration script to remove market_rates table
**Dependencies**: T012

### T018: Update database initialization
**File**: `src/storage/database_init.py`
**Description**: Remove market_rates table creation from database initialization
**Dependencies**: T010

### T019: Remove market rate imports
**File**: Multiple service files
**Description**: Remove MarketRate and ScreenshotParserService imports from all files
**Dependencies**: T009, T010, T011

### T020: Update service initialization
**File**: `app.py`
**Description**: Remove screenshot_parser from service initialization
**Dependencies**: T009, T013, T014

### T021: Remove market comparison UI components
**File**: `app.py`
**Description**: Remove market comparison page UI components
**Dependencies**: T015

### T022: Update sidebar navigation
**File**: `app.py`
**Description**: Remove market comparison option from sidebar navigation
**Dependencies**: T015

### T023: Remove market comparison error handling
**File**: `app.py`
**Description**: Remove market comparison related error handling from UI
**Dependencies**: T015

### T024: Update page routing logic
**File**: `app.py`
**Description**: Remove market comparison routes from page routing
**Dependencies**: T015

### T025: Update existing tests
**File**: Multiple test files
**Description**: Remove market comparison references from existing tests
**Dependencies**: T009, T010, T011, T012, T013, T014

### T026: Add regression tests
**File**: `tests/unit/test_core_regression.py`
**Description**: Add comprehensive regression tests for core functionality
**Dependencies**: T008

### T027: Update integration tests
**File**: Multiple integration test files
**Description**: Remove market comparison scenarios from integration tests
**Dependencies**: T006, T007

### T028: Add missing market data tests
**File**: `tests/unit/test_missing_market_data.py`
**Description**: Add tests for graceful handling of missing market data
**Dependencies**: T012

### T029: Run comprehensive test suite
**File**: N/A
**Description**: Execute full test suite to ensure no regressions
**Dependencies**: T025, T026, T027, T028

### T030: Execute quickstart test scenarios
**File**: N/A
**Description**: Run quickstart.md test scenarios to validate removal
**Dependencies**: T029

### T031: Update app.py comments
**File**: `app.py`
**Description**: Remove market comparison references from comments
**Dependencies**: T015, T016, T020, T021, T022, T023, T024

### T032: Update service documentation
**File**: Multiple service files
**Description**: Remove market comparison method documentation
**Dependencies**: T012, T013, T014

### T033: Clean up remaining references
**File**: All source files
**Description**: Remove any remaining market comparison references
**Dependencies**: T019, T031, T032

### T034: Update error messages
**File**: Multiple files
**Description**: Remove market comparison references from error messages
**Dependencies**: T011, T023

### T035: Remove unused imports
**File**: All source files
**Description**: Remove unused imports and dependencies
**Dependencies**: T009, T010, T011, T019, T033

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- Focus on preserving core rental tracking functionality
- Ensure graceful handling of missing market data
- Maintain application stability throughout removal process

## Validation Checklist
*GATE: Checked before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Core functionality preservation is prioritized
- [x] Database migration is included
- [x] Comprehensive testing strategy is defined
