# Implementation Plan: Secure TÜFE Data Sources

**Branch**: `004-tufe-data-sources` | **Date**: 2025-10-05 | **Spec**: `/specs/004-tufe-data-sources/spec.md`
**Input**: Feature specification from `/specs/004-tufe-data-sources/spec.md`

## Summary
Research and implement secure TÜFE data sources using official APIs instead of web scraping. The implementation will integrate TCMB EVDS API for fetching TÜFE data, add proper data validation and caching, and ensure secure API key management. This addresses security concerns with web scraping while providing reliable, official data sources.

## Technical Context
**Language/Version**: Python 3.13  
**Primary Dependencies**: Streamlit 1.50.0, Plotly 6.3.1, Pandas 2.3.0, Requests 2.32.3, BeautifulSoup4 4.12.0  
**Storage**: SQLite database (existing rental_negotiation.db)  
**Testing**: pytest 8.3.0  
**Target Platform**: Web application (Streamlit)  
**Project Type**: Single project (existing structure)  
**Performance Goals**: API calls <5s, cache lookups <100ms, data validation <50ms  
**Constraints**: Must use official APIs only, no web scraping, secure API key storage  
**Scale/Scope**: Single user application, ~200 new lines of code for API integration

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Simple and Direct Check
- [x] Solution is straightforward and uses official APIs
- [x] No unnecessary abstractions or patterns added
- [x] Code structure is as simple as possible for the requirements

### Test What Matters Check
- [x] Test strategy focuses on API integration and data validation
- [x] Not over-testing simple configuration or UI components
- [x] Tests provide real confidence in data integrity and security

### Done Over Perfect Check
- [x] Feature scope is focused on working API integration
- [x] Not gold-plating with complex caching or multiple data sources
- [x] Plan enables shipping secure TÜFE data fetching quickly

## Project Structure

### Documentation (this feature)
```
specs/004-tufe-data-sources/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/
│   ├── tufe_data_source.py      # New: TÜFE data source configuration
│   ├── tufe_api_key.py          # New: API key management
│   └── tufe_data_cache.py       # New: TÜFE data caching
├── services/
│   ├── tufe_data_source_service.py  # New: Data source management
│   ├── tufe_api_key_service.py      # New: API key management
│   ├── tufe_cache_service.py        # New: Cache management
│   ├── tcmb_api_client.py           # New: TCMB API client
│   └── tufe_config_service.py       # New: Configuration management
├── utils/
│   └── validators.py
└── storage/
    └── data_store.py

tests/
├── contract/
├── integration/
└── unit/

app.py                   # Main Streamlit application
requirements.txt         # Python dependencies
```

**Structure Decision**: Single project structure with existing Streamlit application. New TÜFE data source functionality will extend existing services and add new specialized services for API management.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - TCMB EVDS API registration and authentication process
   - API response format and data structure
   - Rate limiting and error handling patterns
   - Secure API key storage and encryption methods

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all TCMB API integration details resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - TufeDataSource, TufeApiKey, TufeDataCache entities
   - Database schema changes and relationships
   - Validation rules and security considerations

2. **Generate API contracts** from functional requirements:
   - TCMB EVDS API integration patterns
   - Service interfaces for data source management
   - Error handling and validation contracts
   - Output service interfaces to `/contracts/`

3. **Generate contract tests** from contracts:
   - API client integration tests
   - Data validation and caching tests
   - Security and error handling tests
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - API key configuration and validation
   - TÜFE data fetching and caching
   - Error handling and fallback scenarios
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh cursor`
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each new entity → model creation task [P]
- Each service → implementation task [P]
- Each API integration → client implementation task
- Each quickstart scenario → validation task

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before API clients
- Mark [P] for parallel execution (independent files)
- Group by feature: Data sources → API keys → Caching → Integration

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**Task Categories**:
1. **Setup Phase**: Database migrations, new dependencies, configuration
2. **Tests First Phase**: Contract tests, API integration tests, security tests
3. **Core Implementation Phase**: Models, services, API clients
4. **Integration Phase**: UI components, error handling, caching
5. **Testing & Validation Phase**: Quickstart scenarios, end-to-end tests
6. **Documentation & Cleanup Phase**: Code cleanup, security review

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, security validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All TCMB API integration details resolved
- [x] Security requirements clearly defined

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
