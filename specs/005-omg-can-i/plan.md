# Implementation Plan: Easy TÜFE Data Fetching

**Branch**: `005-omg-can-i` | **Date**: 2025-10-06 | **Spec**: /specs/005-omg-can-i/spec.md
**Input**: Feature specification from `/specs/005-omg-can-i/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
**Primary Requirement**: Provide one-click TÜFE data fetching without complex API configuration or technical setup
**Technical Approach**: Implement multiple data source fallbacks with automatic source selection, smart caching, and graceful error handling to create a seamless user experience

## Technical Context
**Language/Version**: Python 3.13  
**Primary Dependencies**: Streamlit 1.50.0, Requests 2.32.3, Pandas 2.3.0  
**Storage**: SQLite (existing database with TÜFE tables)  
**Testing**: Pytest 8.3.0  
**Target Platform**: Web application (Streamlit)  
**Project Type**: Single project (existing rental negotiation support tool)  
**Performance Goals**: <2 seconds for TÜFE data fetch, <100ms cache lookup  
**Constraints**: Must work without user configuration, handle network failures gracefully  
**Scale/Scope**: Single user application, 10-50 TÜFE data points per session  

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Simple and Direct Check
- [x] Solution is straightforward and easy to understand
- [x] No unnecessary abstractions or patterns added
- [x] Code structure is as simple as possible for the requirements

### Test What Matters Check
- [x] Test strategy focuses on critical paths and hard-to-verify behavior
- [x] Not over-testing simple or obvious functionality
- [x] Tests provide real confidence, not just coverage

### Done Over Perfect Check
- [x] Feature scope is focused on working functionality
- [x] Not gold-plating or over-engineering
- [x] Plan enables shipping something useful quickly

## Project Structure

### Documentation (this feature)
```
specs/005-omg-can-i/
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
│   ├── tufe_data_source.py      # Enhanced with reliability ratings
│   ├── tufe_api_key.py          # Enhanced with auto-configuration
│   └── tufe_data_cache.py       # Enhanced with smart expiration
├── services/
│   ├── tufe_fetch_service.py    # NEW: Orchestrates multiple sources
│   ├── tufe_source_manager.py   # NEW: Manages source reliability
│   └── tufe_auto_config.py      # NEW: Zero-config setup
└── utils/
    └── tufe_validator.py        # NEW: Data validation

tests/
├── contract/
│   ├── test_tufe_fetch_service.py
│   └── test_tufe_source_manager.py
├── integration/
│   ├── test_easy_tufe_fetching.py
│   └── test_source_fallback.py
└── unit/
    ├── test_tufe_auto_config.py
    └── test_tufe_validator.py
```

**Structure Decision**: Single project structure with enhanced TÜFE services and new orchestration layer

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Research alternative TÜFE data sources beyond TCMB API
   - Find best practices for automatic source selection and fallback
   - Research data validation patterns for inflation data

2. **Generate and dispatch research agents**:
   ```
   Task: "Research alternative TÜFE data sources for Turkish inflation data"
   Task: "Find best practices for automatic API source selection and fallback patterns"
   Task: "Research data validation patterns for financial/inflation data"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Enhanced TÜFE Data Source with reliability ratings
   - TÜFE Fetch Session for tracking operations
   - Source Manager for automatic selection

2. **Generate API contracts** from functional requirements:
   - One-click fetch endpoint
   - Source status endpoint
   - Cache management endpoint

3. **Generate contract tests** from contracts:
   - Test easy fetch functionality
   - Test source fallback behavior
   - Test cache operations

4. **Extract test scenarios** from user stories:
   - One-click fetch success scenario
   - Source failure fallback scenario
   - Zero-configuration setup scenario

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh cursor`

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple data sources | TCMB API often blocked by firewalls | Single source insufficient for reliability |
| Source reliability tracking | Need to automatically select best source | Manual source selection too complex for users |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.6.0 - See `.specify/memory/constitution.md`*