# Tasks: Rental Fee Negotiation Support Tool

**Input**: Design documents from `/specs/001-problem-statement-i/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

## Phase 3.1: Setup
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with Streamlit 1.50.0 dependencies
- [ ] T003 [P] Configure linting and formatting tools

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Contract test ExchangeRateService in tests/contract/test_exchange_rate_service.py
- [ ] T005 [P] Contract test CalculationService in tests/contract/test_calculation_service.py
- [ ] T006 [P] Contract test ScreenshotParserService in tests/contract/test_screenshot_parser_service.py
- [ ] T007 [P] Contract test InflationService in tests/contract/test_inflation_service.py
- [ ] T008 [P] Contract test ExportService in tests/contract/test_export_service.py
- [ ] T009 [P] Contract test DataStore in tests/contract/test_data_store.py
- [ ] T010 [P] Contract test ChartGenerator in tests/contract/test_chart_generator.py
- [ ] T011 [P] Integration test rental agreement workflow in tests/integration/test_rental_agreement_workflow.py
- [ ] T012 [P] Integration test screenshot parsing workflow in tests/integration/test_screenshot_parsing_workflow.py
- [ ] T013 [P] Integration test negotiation summary generation in tests/integration/test_negotiation_summary.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T014 [P] RentalAgreement model in src/models/rental_agreement.py
- [ ] T015 [P] ExchangeRate model in src/models/exchange_rate.py
- [ ] T016 [P] PaymentRecord model in src/models/payment_record.py
- [ ] T017 [P] MarketRate model in src/models/market_rate.py
- [ ] T018 [P] InflationData model in src/models/inflation_data.py
- [ ] T019 [P] LegalRule model in src/models/legal_rule.py
- [ ] T020 [P] AgreementPeriod model in src/models/agreement_period.py
- [ ] T021 [P] NegotiationMode model in src/models/negotiation_mode.py
- [ ] T022 [P] Exception classes in src/services/exceptions.py
- [ ] T023 [P] ExchangeRateService implementation in src/services/exchange_rate_service.py
- [ ] T024 [P] CalculationService implementation in src/services/calculation_service.py
- [ ] T025 [P] ScreenshotParserService implementation in src/services/screenshot_parser.py
- [ ] T026 [P] InflationService implementation in src/services/inflation_service.py
- [ ] T027 [P] ExportService implementation in src/services/export_service.py
- [ ] T028 [P] DataStore implementation in src/storage/data_store.py
- [ ] T029 [P] ChartGenerator implementation in src/utils/chart_generator.py
- [ ] T030 [P] Validators implementation in src/utils/validators.py

## Phase 3.4: Integration
- [ ] T031 Connect DataStore to SQLite database
- [ ] T032 Initialize database schema and default data
- [ ] T033 Connect ExchangeRateService to TCMB API
- [ ] T034 Connect InflationService to TCMB API
- [ ] T035 Connect ScreenshotParserService to EasyOCR
- [ ] T036 Connect ChartGenerator to Plotly
- [ ] T037 Connect ExportService to chart generation

## Phase 3.5: UI Implementation
- [ ] T038 Streamlit main app structure in app.py
- [ ] T039 Rental agreement form and data entry
- [ ] T040 Screenshot upload and parsing interface
- [ ] T041 Chart display and visualization
- [ ] T042 Negotiation mode selection (Calm/Assertive)
- [ ] T043 Export functionality (PNG/PDF)
- [ ] T044 Legal context display and labeling
- [ ] T045 Data source attribution display

## Phase 3.6: Polish
- [ ] T046 [P] Unit tests for model validation in tests/unit/test_model_validation.py
- [ ] T047 [P] Unit tests for calculation logic in tests/unit/test_calculations.py
- [ ] T048 [P] Unit tests for screenshot parsing in tests/unit/test_screenshot_parsing.py
- [ ] T049 [P] Unit tests for chart generation in tests/unit/test_chart_generation.py
- [ ] T050 Performance tests (<2s page load, <5s screenshot processing)
- [ ] T051 [P] Update quickstart.md with actual usage examples
- [ ] T052 Error handling and user feedback
- [ ] T053 Data validation and edge case handling
- [ ] T054 Run manual testing workflow

## Dependencies
- Tests (T004-T013) before implementation (T014-T030)
- Models (T014-T021) before services (T022-T030)
- Services (T022-T030) before integration (T031-T037)
- Integration (T031-T037) before UI (T038-T045)
- UI (T038-T045) before polish (T046-T054)

## Parallel Example
```
# Launch T004-T013 together (Contract and Integration Tests):
Task: "Contract test ExchangeRateService in tests/contract/test_exchange_rate_service.py"
Task: "Contract test CalculationService in tests/contract/test_calculation_service.py"
Task: "Contract test ScreenshotParserService in tests/contract/test_screenshot_parser_service.py"
Task: "Contract test InflationService in tests/contract/test_inflation_service.py"
Task: "Contract test ExportService in tests/contract/test_export_service.py"
Task: "Contract test DataStore in tests/contract/test_data_store.py"
Task: "Contract test ChartGenerator in tests/contract/test_chart_generator.py"
Task: "Integration test rental agreement workflow in tests/integration/test_rental_agreement_workflow.py"
Task: "Integration test screenshot parsing workflow in tests/integration/test_screenshot_parsing_workflow.py"
Task: "Integration test negotiation summary generation in tests/integration/test_negotiation_summary.py"

# Launch T014-T021 together (Model Implementation):
Task: "RentalAgreement model in src/models/rental_agreement.py"
Task: "ExchangeRate model in src/models/exchange_rate.py"
Task: "PaymentRecord model in src/models/payment_record.py"
Task: "MarketRate model in src/models/market_rate.py"
Task: "InflationData model in src/models/inflation_data.py"
Task: "LegalRule model in src/models/legal_rule.py"
Task: "AgreementPeriod model in src/models/agreement_period.py"
Task: "NegotiationMode model in src/models/negotiation_mode.py"

# Launch T022-T030 together (Service Implementation):
Task: "Exception classes in src/services/exceptions.py"
Task: "ExchangeRateService implementation in src/services/exchange_rate_service.py"
Task: "CalculationService implementation in src/services/calculation_service.py"
Task: "ScreenshotParserService implementation in src/services/screenshot_parser.py"
Task: "InflationService implementation in src/services/inflation_service.py"
Task: "ExportService implementation in src/services/export_service.py"
Task: "DataStore implementation in src/storage/data_store.py"
Task: "ChartGenerator implementation in src/utils/chart_generator.py"
Task: "Validators implementation in src/utils/validators.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- Follow TDD: Tests must fail before implementation
- All new functional requirements (FR-013 to FR-020) are covered in the tasks

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each service interface → implementation task [P]
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Database schema → integration tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Integration → UI → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] New functional requirements (FR-013 to FR-020) covered
- [x] Legal context and negotiation modes included
- [x] Data source attribution included