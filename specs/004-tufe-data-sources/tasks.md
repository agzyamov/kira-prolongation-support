# Tasks: Secure TÜFE Data Sources

**Input**: Design documents from `/specs/004-tufe-data-sources/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Phase 3.1: Setup
- [x] T001 Create database migration script to add new TÜFE tables (tufe_data_sources, tufe_api_keys, tufe_data_cache)
- [x] T002 [P] Update requirements.txt if new dependencies needed for API integration
- [x] T003 [P] Create environment configuration for TCMB API key management

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test for TufeDataSourceService in tests/contract/test_tufe_data_source_service.py
- [x] T005 [P] Contract test for TufeApiKeyService in tests/contract/test_tufe_api_key_service.py
- [x] T006 [P] Contract test for TufeCacheService in tests/contract/test_tufe_cache_service.py
- [x] T007 [P] Contract test for TCMB API client in tests/contract/test_tcmb_api_client.py
- [x] T008 [P] Contract test for TufeConfigService in tests/contract/test_tufe_config_service.py
- [x] T009 [P] Integration test for TCMB API key configuration in tests/integration/test_tcmb_api_key_config.py
- [x] T010 [P] Integration test for TÜFE data fetching from TCMB API in tests/integration/test_tufe_data_fetching.py
- [x] T011 [P] Integration test for data source attribution in tests/integration/test_data_source_attribution.py
- [x] T012 [P] Integration test for cache management in tests/integration/test_tufe_cache_management.py
- [x] T013 [P] Integration test for API error handling in tests/integration/test_tufe_api_error_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T014 [P] TufeDataSource model in src/models/tufe_data_source.py
- [x] T015 [P] TufeApiKey model in src/models/tufe_api_key.py
- [x] T016 [P] TufeDataCache model in src/models/tufe_data_cache.py
- [x] T017 [P] TufeDataSourceService in src/services/tufe_data_source_service.py
- [x] T018 [P] TufeApiKeyService in src/services/tufe_api_key_service.py
- [x] T019 [P] TufeCacheService in src/services/tufe_cache_service.py
- [x] T020 [P] TCMB API client in src/services/tcmb_api_client.py
- [x] T021 [P] TufeConfigService in src/services/tufe_config_service.py
- [x] T022 Extend InflationData model with source attribution methods in src/models/inflation_data.py
- [x] T023 Extend InflationService with TCMB API integration methods in src/services/inflation_service.py

## Phase 3.4: Integration
- [x] T024 Update DataStore to support new TÜFE entities in src/storage/data_store.py
- [x] T025 [P] Add new exception classes to src/services/exceptions.py
- [x] T026 [P] Update service imports in src/services/__init__.py
- [x] T027 [P] Update model imports in src/models/__init__.py
- [x] T028 Add TCMB API key configuration UI to Streamlit app in app.py
- [x] T029 Add TÜFE data source management UI to inflation data page in app.py
- [x] T030 Add secure TÜFE data fetching functionality to inflation data page in app.py
- [x] T031 Add data source attribution display to export functionality in app.py
- [x] T032 Add cache status and management UI to inflation data page in app.py

## Phase 3.5: Testing & Validation
- [x] T033 [P] Unit tests for TufeDataSource model in tests/unit/test_tufe_data_source.py
- [x] T034 [P] Unit tests for TufeApiKey model in tests/unit/test_tufe_api_key.py
- [x] T035 [P] Unit tests for TufeDataCache model in tests/unit/test_tufe_data_cache.py
- [x] T036 [P] Unit tests for TufeDataSourceService in tests/unit/test_tufe_data_source_service.py
- [x] T037 [P] Unit tests for TufeApiKeyService in tests/unit/test_tufe_api_key_service.py
- [x] T038 [P] Unit tests for TufeCacheService in tests/unit/test_tufe_cache_service.py
- [x] T039 [P] Unit tests for TCMB API client in tests/unit/test_tcmb_api_client.py
- [x] T040 [P] Unit tests for TufeConfigService in tests/unit/test_tufe_config_service.py
- [x] T041 [P] Unit tests for extended InflationData methods in tests/unit/test_inflation_data_extensions.py
- [x] T042 [P] Unit tests for extended InflationService methods in tests/unit/test_inflation_service_extensions.py
- [x] T043 Run comprehensive test suite to ensure no regressions
- [x] T044 Execute quickstart.md test scenarios

## Phase 3.6: Documentation & Cleanup
- [x] T045 [P] Update app.py comments to document new TÜFE data source features
- [x] T046 [P] Update service documentation to include new TÜFE methods
- [x] T047 [P] Clean up any remaining TODO comments
- [x] T048 [P] Update error messages to include new TÜFE functionality
- [x] T049 [P] Remove unused imports and dependencies from all files
- [x] T050 [P] Add security documentation for API key management

## Dependencies
- Tests (T004-T013) before implementation (T014-T023)
- T014 blocks T017, T024
- T015 blocks T018, T024
- T016 blocks T019, T024
- T017 blocks T028
- T018 blocks T028
- T019 blocks T032
- T020 blocks T030
- T021 blocks T028
- T022 blocks T023
- T023 blocks T030, T031
- T024 blocks T028, T029, T030, T031, T032
- Implementation before testing (T033-T044)
- Testing before documentation (T045-T050)

## Parallel Execution Examples

### Phase 3.2: Tests First (TDD)
```bash
# Launch T004-T013 together (all contract and integration tests):
Task: "Contract test for TufeDataSourceService in tests/contract/test_tufe_data_source_service.py"
Task: "Contract test for TufeApiKeyService in tests/contract/test_tufe_api_key_service.py"
Task: "Contract test for TufeCacheService in tests/contract/test_tufe_cache_service.py"
Task: "Contract test for TCMB API client in tests/contract/test_tcmb_api_client.py"
Task: "Contract test for TufeConfigService in tests/contract/test_tufe_config_service.py"
Task: "Integration test for TCMB API key configuration in tests/integration/test_tcmb_api_key_config.py"
Task: "Integration test for TÜFE data fetching from TCMB API in tests/integration/test_tufe_data_fetching.py"
Task: "Integration test for data source attribution in tests/integration/test_data_source_attribution.py"
Task: "Integration test for cache management in tests/integration/test_tufe_cache_management.py"
Task: "Integration test for API error handling in tests/integration/test_tufe_api_error_handling.py"
```

### Phase 3.3: Core Implementation
```bash
# Launch T014-T021 together (all new models and services):
Task: "TufeDataSource model in src/models/tufe_data_source.py"
Task: "TufeApiKey model in src/models/tufe_api_key.py"
Task: "TufeDataCache model in src/models/tufe_data_cache.py"
Task: "TufeDataSourceService in src/services/tufe_data_source_service.py"
Task: "TufeApiKeyService in src/services/tufe_api_key_service.py"
Task: "TufeCacheService in src/services/tufe_cache_service.py"
Task: "TCMB API client in src/services/tcmb_api_client.py"
Task: "TufeConfigService in src/services/tufe_config_service.py"
```

### Phase 3.5: Testing & Validation
```bash
# Launch T033-T042 together (all unit tests):
Task: "Unit tests for TufeDataSource model in tests/unit/test_tufe_data_source.py"
Task: "Unit tests for TufeApiKey model in tests/unit/test_tufe_api_key.py"
Task: "Unit tests for TufeDataCache model in tests/unit/test_tufe_data_cache.py"
Task: "Unit tests for TufeDataSourceService in tests/unit/test_tufe_data_source_service.py"
Task: "Unit tests for TufeApiKeyService in tests/unit/test_tufe_api_key_service.py"
Task: "Unit tests for TufeCacheService in tests/unit/test_tufe_cache_service.py"
Task: "Unit tests for TCMB API client in tests/unit/test_tcmb_api_client.py"
Task: "Unit tests for TufeConfigService in tests/unit/test_tufe_config_service.py"
Task: "Unit tests for extended InflationData methods in tests/unit/test_inflation_data_extensions.py"
Task: "Unit tests for extended InflationService methods in tests/unit/test_inflation_service_extensions.py"
```

### Phase 3.6: Documentation & Cleanup
```bash
# Launch T045-T050 together (all documentation tasks):
Task: "Update app.py comments to document new TÜFE data source features"
Task: "Update service documentation to include new TÜFE methods"
Task: "Clean up any remaining TODO comments"
Task: "Update error messages to include new TÜFE functionality"
Task: "Remove unused imports and dependencies from all files"
Task: "Add security documentation for API key management"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- TCMB API key must be stored securely (environment variables)
- All API calls must use HTTPS
- Data validation required before storage
- Cache management with 24-hour expiration
- Source attribution required in all exports

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - service-interfaces.md → contract test tasks T004-T008
   - Each service interface → corresponding test task [P]
   
2. **From Data Model**:
   - TufeDataSource → model task T014 [P]
   - TufeApiKey → model task T015 [P]
   - TufeDataCache → model task T016 [P]
   - InflationData extensions → extension task T022
   
3. **From User Stories**:
   - API key configuration → integration test T009 [P]
   - Data fetching → integration test T010 [P]
   - Source attribution → integration test T011 [P]
   - Cache management → integration test T012 [P]
   - Error handling → integration test T013 [P]

4. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Testing → Documentation
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T004-T008)
- [x] All entities have model tasks (T014-T016)
- [x] All tests come before implementation (T004-T013 before T014-T023)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TCMB API integration properly planned
- [x] Security considerations included
- [x] Cache management included
- [x] Data source attribution included
