# Tasks: Easy TÜFE Data Fetching

**Input**: Design documents from `/specs/005-omg-can-i/`
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
- [x] T001 Create database migration for enhanced TÜFE tables
- [x] T002 [P] Configure linting and formatting tools for new TÜFE services
- [x] T003 [P] Set up test database for TÜFE feature testing

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test TufeFetchService in tests/contract/test_tufe_fetch_service.py
- [x] T005 [P] Contract test TufeSourceManager in tests/contract/test_tufe_source_manager.py
- [x] T006 [P] Contract test TufeAutoConfig in tests/contract/test_tufe_auto_config.py
- [x] T007 [P] Contract test TufeValidator in tests/contract/test_tufe_validator.py
- [x] T008 [P] Integration test one-click TÜFE fetching in tests/integration/test_easy_tufe_fetching.py
- [x] T009 [P] Integration test source fallback in tests/integration/test_source_fallback.py
- [x] T010 [P] Integration test zero-configuration setup in tests/integration/test_zero_config.py
- [x] T011 [P] Integration test data validation in tests/integration/test_data_validation.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T012 [P] Enhanced TufeDataSource model in src/models/tufe_data_source.py
- [x] T013 [P] TufeFetchSession model in src/models/tufe_fetch_session.py
- [x] T014 [P] TufeSourceManager model in src/models/tufe_source_manager.py
- [x] T015 [P] TufeAutoConfig model in src/models/tufe_auto_config.py
- [ ] T016 [P] Enhanced TufeApiKey model in src/models/tufe_api_key.py
- [ ] T017 [P] Enhanced TufeDataCache model in src/models/tufe_data_cache.py
- [x] T018 [P] TufeFetchResult DTO in src/models/tufe_fetch_result.py
- [x] T019 [P] SourceAttempt DTO in src/models/source_attempt.py
- [x] T020 [P] ValidationResult DTO in src/models/validation_result.py
- [ ] T021 [P] TufeFetchService in src/services/tufe_fetch_service.py
- [ ] T022 [P] TufeSourceManager service in src/services/tufe_source_manager.py
- [ ] T023 [P] TufeAutoConfig service in src/services/tufe_auto_config.py
- [ ] T024 [P] Enhanced TufeValidator in src/utils/tufe_validator.py
- [ ] T025 [P] Enhanced TufeDataSourceService in src/services/tufe_data_source_service.py
- [ ] T026 [P] Enhanced TufeCacheService in src/services/tufe_cache_service.py

## Phase 3.4: Integration
- [ ] T027 Connect TufeFetchService to DataStore
- [ ] T028 Connect TufeSourceManager to DataStore
- [ ] T029 Connect TufeAutoConfig to DataStore
- [ ] T030 Enhanced TufeDataSourceService database integration
- [ ] T031 Enhanced TufeCacheService database integration
- [ ] T032 TufeFetchService error handling and logging
- [ ] T033 TufeSourceManager health monitoring integration
- [ ] T034 TufeAutoConfig source discovery integration

## Phase 3.5: UI Integration
- [ ] T035 Add easy TÜFE fetching UI to app.py
- [ ] T036 Add source health dashboard to app.py
- [ ] T037 Add zero-configuration setup UI to app.py
- [ ] T038 Add data validation feedback to app.py
- [ ] T039 Add performance metrics display to app.py
- [ ] T040 Add error handling and user feedback to app.py

## Phase 3.6: Testing & Validation
- [ ] T041 [P] Unit tests for TufeFetchService in tests/unit/test_tufe_fetch_service.py
- [ ] T042 [P] Unit tests for TufeSourceManager in tests/unit/test_tufe_source_manager.py
- [ ] T043 [P] Unit tests for TufeAutoConfig in tests/unit/test_tufe_auto_config.py
- [ ] T044 [P] Unit tests for TufeValidator in tests/unit/test_tufe_validator.py
- [ ] T045 [P] Unit tests for enhanced models in tests/unit/test_enhanced_models.py
- [ ] T046 Performance tests for fetch operations (<2 seconds)
- [ ] T047 Performance tests for cache operations (<100ms)
- [ ] T048 Run comprehensive test suite to ensure no regressions
- [ ] T049 Execute quickstart.md test scenarios
- [ ] T050 Manual testing of easy TÜFE fetching feature

## Phase 3.7: Documentation & Cleanup
- [ ] T051 [P] Update README.md with easy TÜFE fetching documentation
- [ ] T052 [P] Update API documentation for new services
- [ ] T053 [P] Create user guide for easy TÜFE fetching
- [ ] T054 Remove any temporary files or debug code
- [ ] T055 Final code review and cleanup
- [ ] T056 Update progress tracking in plan.md

## Dependencies
- Tests (T004-T011) before implementation (T012-T026)
- T012 blocks T021, T027
- T013 blocks T021, T027
- T014 blocks T022, T028
- T015 blocks T023, T029
- T016 blocks T025, T030
- T017 blocks T026, T031
- T018-T020 block T021
- T021 blocks T027, T032
- T022 blocks T028, T033
- T023 blocks T029, T034
- T024 blocks T021, T022, T023
- T025 blocks T030
- T026 blocks T031
- Implementation before UI integration (T035-T040)
- UI integration before testing (T041-T050)
- Testing before documentation (T051-T056)

## Parallel Example
```
# Launch T004-T011 together (Contract and Integration Tests):
Task: "Contract test TufeFetchService in tests/contract/test_tufe_fetch_service.py"
Task: "Contract test TufeSourceManager in tests/contract/test_tufe_source_manager.py"
Task: "Contract test TufeAutoConfig in tests/contract/test_tufe_auto_config.py"
Task: "Contract test TufeValidator in tests/contract/test_tufe_validator.py"
Task: "Integration test one-click TÜFE fetching in tests/integration/test_easy_tufe_fetching.py"
Task: "Integration test source fallback in tests/integration/test_source_fallback.py"
Task: "Integration test zero-configuration setup in tests/integration/test_zero_config.py"
Task: "Integration test data validation in tests/integration/test_data_validation.py"

# Launch T012-T020 together (Model Creation):
Task: "Enhanced TufeDataSource model in src/models/tufe_data_source.py"
Task: "TufeFetchSession model in src/models/tufe_fetch_session.py"
Task: "TufeSourceManager model in src/models/tufe_source_manager.py"
Task: "TufeAutoConfig model in src/models/tufe_auto_config.py"
Task: "Enhanced TufeApiKey model in src/models/tufe_api_key.py"
Task: "Enhanced TufeDataCache model in src/models/tufe_data_cache.py"
Task: "TufeFetchResult DTO in src/models/tufe_fetch_result.py"
Task: "SourceAttempt DTO in src/models/source_attempt.py"
Task: "ValidationResult DTO in src/models/validation_result.py"

# Launch T021-T026 together (Service Implementation):
Task: "TufeFetchService in src/services/tufe_fetch_service.py"
Task: "TufeSourceManager service in src/services/tufe_source_manager.py"
Task: "TufeAutoConfig service in src/services/tufe_auto_config.py"
Task: "Enhanced TufeValidator in src/utils/tufe_validator.py"
Task: "Enhanced TufeDataSourceService in src/services/tufe_data_source_service.py"
Task: "Enhanced TufeCacheService in src/services/tufe_cache_service.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- Follow TDD approach: write failing tests first
- Ensure all new services integrate with existing TÜFE infrastructure
- Maintain backward compatibility with existing TÜFE functionality

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - TufeFetchService → contract test task [P]
   - TufeSourceManager → contract test task [P]
   - TufeAutoConfig → contract test task [P]
   - TufeValidator → contract test task [P]
   
2. **From Data Model**:
   - TufeDataSource (Enhanced) → model enhancement task [P]
   - TufeFetchSession (New) → model creation task [P]
   - TufeSourceManager (New) → model creation task [P]
   - TufeAutoConfig (New) → model creation task [P]
   - TufeApiKey (Enhanced) → model enhancement task [P]
   - TufeDataCache (Enhanced) → model enhancement task [P]
   - DTOs → model creation tasks [P]
   
3. **From User Stories**:
   - One-click fetching → integration test [P]
   - Source fallback → integration test [P]
   - Zero-configuration → integration test [P]
   - Data validation → integration test [P]

4. **Ordering**:
   - Setup → Tests → Models → Services → Integration → UI → Testing → Documentation
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All quickstart scenarios have corresponding tests
- [x] All new services have integration tests
- [x] All enhanced models have unit tests
- [x] Performance requirements are tested
- [x] Error handling is tested
- [x] UI integration is included
- [x] Documentation tasks are included
