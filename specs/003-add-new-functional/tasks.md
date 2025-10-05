# Tasks: Add New Functional Requirements

**Input**: Design documents from `/specs/003-add-new-functional/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

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
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [x] T001 Create database migration script to add new tables (negotiation_settings, legal_rules)
- [x] T002 [P] Create database initialization script for default legal rules
- [x] T003 [P] Update requirements.txt if new dependencies needed

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test for NegotiationSettingsService in tests/contract/test_negotiation_settings_service.py
- [x] T005 [P] Contract test for LegalRuleService in tests/contract/test_legal_rule_service.py
- [x] T006 [P] Contract test for extended CalculationService in tests/contract/test_calculation_service_extensions.py
- [x] T007 [P] Contract test for extended ChartGenerator in tests/contract/test_chart_generator_extensions.py
- [x] T008 [P] Contract test for extended ExportService in tests/contract/test_export_service_extensions.py
- [x] T009 [P] Contract test for extended InflationService in tests/contract/test_inflation_service_extensions.py
- [x] T010 [P] Integration test for legal rule determination in tests/integration/test_legal_rule_determination.py
- [x] T011 [P] Integration test for negotiation mode persistence in tests/integration/test_negotiation_mode_persistence.py
- [x] T012 [P] Integration test for agreement period annotations in tests/integration/test_agreement_annotations.py
- [x] T013 [P] Integration test for data source disclosure in tests/integration/test_data_source_disclosure.py
- [x] T014 [P] Integration test for TÜFE data handling in tests/integration/test_tufe_data_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T015 [P] NegotiationSettings model in src/models/negotiation_settings.py
- [x] T016 [P] LegalRule model in src/models/legal_rule.py
- [x] T017 [P] NegotiationSettingsService in src/services/negotiation_settings_service.py
- [x] T018 [P] LegalRuleService in src/services/legal_rule_service.py
- [x] T019 [P] Extend RentalAgreement model with legal rule methods in src/models/rental_agreement.py
- [x] T020 [P] Extend InflationData model with TÜFE methods in src/models/inflation_data.py
- [x] T021 [P] Extend CalculationService with legal rule methods in src/services/calculation_service.py
- [x] T022 [P] Extend ChartGenerator with negotiation mode and annotation methods in src/utils/chart_generator.py
- [x] T023 [P] Extend ExportService with data source disclosure in src/services/export_service.py
- [x] T024 [P] Extend InflationService with TÜFE methods in src/services/inflation_service.py

## Phase 3.4: Integration
- [x] T025 Update DataStore to support new entities in src/storage/data_store.py
- [x] T026 [P] Add new exception classes to src/services/exceptions.py
- [x] T027 [P] Update service imports in src/services/__init__.py
- [x] T028 [P] Update model imports in src/models/__init__.py
- [x] T029 Add negotiation mode selector to Streamlit UI in app.py
- [x] T030 Add legal rule display to negotiation summary page in app.py
- [x] T031 Add agreement period annotations to charts in app.py
- [x] T032 Add data source disclosure to export functionality in app.py
- [x] T033 Add TÜFE data handling to inflation data page in app.py

## Phase 3.5: Testing & Validation
- [x] T034 [P] Unit tests for NegotiationSettings model in tests/unit/test_negotiation_settings.py
- [x] T035 [P] Unit tests for LegalRule model in tests/unit/test_legal_rule.py
- [x] T036 [P] Unit tests for NegotiationSettingsService in tests/unit/test_negotiation_settings_service.py
- [x] T037 [P] Unit tests for LegalRuleService in tests/unit/test_legal_rule_service.py
- [x] T038 [P] Unit tests for extended RentalAgreement methods in tests/unit/test_rental_agreement_extensions.py
- [x] T039 [P] Unit tests for extended InflationData methods in tests/unit/test_inflation_data_extensions.py
- [x] T040 [P] Unit tests for extended CalculationService methods in tests/unit/test_calculation_service_extensions.py
- [x] T041 [P] Unit tests for extended ChartGenerator methods in tests/unit/test_chart_generator_extensions.py
- [x] T042 [P] Unit tests for extended ExportService methods in tests/unit/test_export_service_extensions.py
- [x] T043 [P] Unit tests for extended InflationService methods in tests/unit/test_inflation_service_extensions.py
- [x] T044 Run comprehensive test suite to ensure no regressions
- [x] T045 Execute quickstart.md test scenarios

## Phase 3.6: Documentation & Cleanup
- [x] T046 [P] Update app.py comments to document new features
- [x] T047 [P] Update service documentation to include new methods
- [x] T048 [P] Clean up any remaining TODO comments
- [x] T049 [P] Update error messages to include new functionality
- [x] T050 [P] Remove unused imports and dependencies from all files

## Dependencies
- Tests (T004-T014) before implementation (T015-T024)
- T015 blocks T017, T025
- T016 blocks T018, T025
- T019 blocks T021
- T020 blocks T024
- T021 blocks T029, T030
- T022 blocks T031
- T023 blocks T032
- T024 blocks T033
- Implementation before testing (T034-T045)
- Testing before documentation (T046-T050)

## Parallel Example
```
# Launch T004-T014 together (all contract and integration tests):
Task: "Contract test for NegotiationSettingsService in tests/contract/test_negotiation_settings_service.py"
Task: "Contract test for LegalRuleService in tests/contract/test_legal_rule_service.py"
Task: "Contract test for extended CalculationService in tests/contract/test_calculation_service_extensions.py"
Task: "Contract test for extended ChartGenerator in tests/contract/test_chart_generator_extensions.py"
Task: "Contract test for extended ExportService in tests/contract/test_export_service_extensions.py"
Task: "Contract test for extended InflationService in tests/contract/test_inflation_service_extensions.py"
Task: "Integration test for legal rule determination in tests/integration/test_legal_rule_determination.py"
Task: "Integration test for negotiation mode persistence in tests/integration/test_negotiation_mode_persistence.py"
Task: "Integration test for agreement period annotations in tests/integration/test_agreement_annotations.py"
Task: "Integration test for data source disclosure in tests/integration/test_data_source_disclosure.py"
Task: "Integration test for TÜFE data handling in tests/integration/test_tufe_data_handling.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
