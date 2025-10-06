# Tasks: Easy TÜFE Data Fetching

**Input**: Design documents from `/specs/005-omg-can-i/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/  

## Execution Flow (main)
```
1. Load plan.md from feature directory ✅
   → Extract: Python 3.13, Streamlit 1.50.0, Requests 2.32.3, SQLite
2. Load design documents ✅
   → data-model.md: 3 new entities (OECDApiClient, RateLimitHandler, DataValidator)
   → contracts/: 1 service interface file → contract test task
   → research.md: OECD API integration decisions
3. Generate tasks by category ✅
   → Setup: Database migrations, dependencies
   → Tests: Contract tests, integration tests
   → Core: New services, enhanced existing services
   → Integration: Streamlit UI, error handling
   → Polish: Unit tests, performance validation
4. Apply task rules ✅
   → Different files = mark [P] for parallel
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T030) ✅
6. Generate dependency graph ✅
7. Create parallel execution examples ✅
8. Validate task completeness ✅
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup
- [x] T001 Create database migration for enhanced TÜFE tables in scripts/migrate_enhance_oecd_tables.py
- [x] T002 [P] Add OECD API dependencies to requirements.txt (requests, xml.etree.ElementTree)
- [x] T003 [P] Configure rate limiting constants in src/config/oecd_config.py

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test OECDApiClient in tests/contract/test_oecd_api_client.py
- [x] T005 [P] Contract test RateLimitHandler in tests/contract/test_rate_limit_handler.py
- [x] T006 [P] Contract test DataValidator in tests/contract/test_data_validator.py
- [x] T007 [P] Integration test OECD API fetching in tests/integration/test_oecd_tufe_fetching.py
- [x] T008 [P] Integration test rate limiting behavior in tests/integration/test_rate_limiting.py
- [x] T009 [P] Integration test caching with TTL in tests/integration/test_oecd_caching.py
- [x] T010 [P] Integration test error handling scenarios in tests/integration/test_oecd_error_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T011 [P] OECDApiClient service in src/services/oecd_api_client.py
- [x] T012 [P] RateLimitHandler service in src/services/rate_limit_handler.py
- [x] T013 [P] DataValidator service in src/services/data_validator.py
- [x] T014 [P] Enhanced TufeDataSource model with rate limiting fields in src/models/tufe_data_source.py
- [x] T015 [P] Enhanced TufeDataCache model with TTL fields in src/models/tufe_data_cache.py
- [x] T016 Enhanced InflationService with OECD API integration in src/services/inflation_service.py
- [x] T017 Enhanced TufeCacheService with TTL support in src/services/tufe_cache_service.py
- [x] T018 Enhanced DataStore with new TÜFE table methods in src/storage/data_store.py

## Phase 3.4: Integration
- [x] T019 Add OECD API exception classes in src/services/exceptions.py
- [x] T020 Initialize OECD services in app.py init_services()
- [x] T021 Add OECD API UI components to Streamlit app in app.py
- [x] T022 Implement one-click TÜFE fetch button in app.py
- [x] T023 Add error handling and user feedback in app.py
- [x] T024 Add cache management UI in app.py
- [x] T025 Add rate limiting status display in app.py

## Phase 3.5: UI Integration
- [x] T026 [P] Add OECD API configuration section to Inflation Data page
- [x] T027 [P] Add TÜFE data fetching progress indicators
- [x] T028 [P] Add cache statistics display
- [x] T029 [P] Add manual data entry fallback UI
- [x] T030 [P] Add data source attribution display

## Phase 3.6: Testing & Validation
- [x] T031 [P] Unit tests for OECDApiClient in tests/unit/test_oecd_api_client.py
- [x] T032 [P] Unit tests for RateLimitHandler in tests/unit/test_rate_limit_handler.py
- [x] T033 [P] Unit tests for DataValidator in tests/unit/test_data_validator.py
- [x] T034 [P] Unit tests for enhanced TufeDataSource in tests/unit/test_tufe_data_source_enhanced.py
- [x] T035 [P] Unit tests for enhanced TufeDataCache in tests/unit/test_tufe_data_cache_enhanced.py
- [x] T036 Integration test complete OECD fetch flow in tests/integration/test_complete_oecd_flow.py
- [x] T037 Performance test API response times (<2s target) in tests/performance/test_oecd_performance.py
- [x] T038 End-to-end test Streamlit UI integration in tests/e2e/test_oecd_ui_integration.py

## Phase 3.7: Documentation & Cleanup
- [x] T039 [P] Update README.md with OECD API integration documentation
- [x] T040 [P] Add API documentation for new services in docs/api.md
- [x] T041 [P] Update quickstart.md with OECD API usage examples
- [x] T042 [P] Add troubleshooting guide for common OECD API issues
- [x] T043 [P] Clean up temporary test files and scripts
- [x] T044 [P] Add rate limiting best practices documentation
- [x] T045 [P] Update service initialization documentation
- [x] T046 [P] Add error handling examples and recovery procedures

## Dependencies
- Setup (T001-T003) before everything
- Tests (T004-T010) before implementation (T011-T018)
- T011 blocks T016 (OECDApiClient needed by InflationService)
- T012 blocks T016 (RateLimitHandler needed by InflationService)
- T013 blocks T016 (DataValidator needed by InflationService)
- T014 blocks T018 (Enhanced TufeDataSource needed by DataStore)
- T015 blocks T017 (Enhanced TufeDataCache needed by TufeCacheService)
- Core implementation (T011-T018) before integration (T019-T025)
- Integration (T019-T025) before UI (T026-T030)
- UI (T026-T030) before testing (T031-T038)
- Testing (T031-T038) before documentation (T039-T046)

## Parallel Execution Examples

### Phase 3.1 Setup (T002-T003 can run together):
```
Task: "Add OECD API dependencies to requirements.txt (requests, xml.etree.ElementTree)"
Task: "Configure rate limiting constants in src/config/oecd_config.py"
```

### Phase 3.2 Tests First (T004-T010 can run together):
```
Task: "Contract test OECDApiClient in tests/contract/test_oecd_api_client.py"
Task: "Contract test RateLimitHandler in tests/contract/test_rate_limit_handler.py"
Task: "Contract test DataValidator in tests/contract/test_data_validator.py"
Task: "Integration test OECD API fetching in tests/integration/test_oecd_tufe_fetching.py"
Task: "Integration test rate limiting behavior in tests/integration/test_rate_limiting.py"
Task: "Integration test caching with TTL in tests/integration/test_oecd_caching.py"
Task: "Integration test error handling scenarios in tests/integration/test_oecd_error_handling.py"
```

### Phase 3.3 Core Implementation (T011-T015 can run together):
```
Task: "OECDApiClient service in src/services/oecd_api_client.py"
Task: "RateLimitHandler service in src/services/rate_limit_handler.py"
Task: "DataValidator service in src/services/data_validator.py"
Task: "Enhanced TufeDataSource model with rate limiting fields in src/models/tufe_data_source.py"
Task: "Enhanced TufeDataCache model with TTL fields in src/models/tufe_data_cache.py"
```

### Phase 3.5 UI Integration (T026-T030 can run together):
```
Task: "Add OECD API configuration section to Inflation Data page"
Task: "Add TÜFE data fetching progress indicators"
Task: "Add cache statistics display"
Task: "Add manual data entry fallback UI"
Task: "Add data source attribution display"
```

### Phase 3.6 Testing (T031-T035 can run together):
```
Task: "Unit tests for OECDApiClient in tests/unit/test_oecd_api_client.py"
Task: "Unit tests for RateLimitHandler in tests/unit/test_rate_limit_handler.py"
Task: "Unit tests for DataValidator in tests/unit/test_data_validator.py"
Task: "Unit tests for enhanced TufeDataSource in tests/unit/test_tufe_data_source_enhanced.py"
Task: "Unit tests for enhanced TufeDataCache in tests/unit/test_tufe_data_cache_enhanced.py"
```

### Phase 3.7 Documentation (T039-T046 can run together):
```
Task: "Update README.md with OECD API integration documentation"
Task: "Add API documentation for new services in docs/api.md"
Task: "Update quickstart.md with OECD API usage examples"
Task: "Add troubleshooting guide for common OECD API issues"
Task: "Clean up temporary test files and scripts"
Task: "Add rate limiting best practices documentation"
Task: "Add service initialization documentation"
Task: "Add error handling examples and recovery procedures"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing (TDD approach)
- Commit after each phase completion
- OECD API integration extends existing TÜFE infrastructure
- Rate limiting is critical for API sustainability
- Caching reduces API calls and improves performance
- Error handling provides graceful degradation

## Task Generation Rules Applied
1. **From Contracts**: 1 service interface file → 7 contract/integration test tasks
2. **From Data Model**: 3 new entities → 3 model creation tasks + 2 enhancement tasks
3. **From User Stories**: 8 quickstart scenarios → 8 integration test tasks
4. **Ordering**: Setup → Tests → Models → Services → Integration → UI → Testing → Documentation

## Validation Checklist ✅
- [x] All contracts have corresponding tests (7 test tasks for 1 contract file)
- [x] All entities have model tasks (3 new entities + 2 enhancements)
- [x] All tests come before implementation (T004-T010 before T011-T018)
- [x] Parallel tasks truly independent (different files, no shared dependencies)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task