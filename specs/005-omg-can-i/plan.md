
# Implementation Plan: Easy TÜFE Data Fetching

**Branch**: `005-omg-can-i` | **Date**: 2025-01-27 | **Spec**: `/specs/005-omg-can-i/spec.md`
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
Implement one-click TÜFE data fetching using OECD API as the primary and only data source, with automatic caching, rate limit respect, and fallback to manual entry when needed. The system will provide zero-configuration access to Turkish inflation data for rental negotiations.

## Technical Context
**Language/Version**: Python 3.13  
**Primary Dependencies**: Streamlit 1.50.0, Requests 2.32.3, Pandas 2.3.0, SQLite  
**Storage**: SQLite with existing TÜFE tables (tufe_data_sources, tufe_api_keys, tufe_data_cache)  
**Testing**: pytest 8.3.0  
**Target Platform**: Web application (Streamlit)  
**Project Type**: single (existing rental negotiation support tool)  
**Performance Goals**: <2s response time for TÜFE data fetch, <500ms for cached data  
**Constraints**: Must respect OECD API rate limits, offline-capable with cached data, zero user configuration required  
**Scale/Scope**: Single user application, existing codebase integration

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Simple and Direct Check
- [x] Solution is straightforward and easy to understand (OECD API integration with caching)
- [x] No unnecessary abstractions or patterns added (direct API calls with simple caching)
- [x] Code structure is as simple as possible for the requirements (single service class)

### Test What Matters Check
- [x] Test strategy focuses on critical paths and hard-to-verify behavior (API integration, rate limiting, caching)
- [x] Not over-testing simple or obvious functionality (focus on integration and error handling)
- [x] Tests provide real confidence, not just coverage (API connectivity, data validation)

### Done Over Perfect Check
- [x] Feature scope is focused on working functionality (one-click fetch with caching)
- [x] Not gold-plating or over-engineering (simple OECD API integration)
- [x] Plan enables shipping something useful quickly (leverages existing infrastructure)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
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
│   ├── tufe_data_source.py
│   ├── tufe_api_key.py
│   ├── tufe_data_cache.py
│   └── inflation_data.py
├── services/
│   ├── tufe_data_source_service.py
│   ├── tufe_api_key_service.py
│   ├── tufe_cache_service.py
│   ├── tcmb_api_client.py
│   └── inflation_service.py
└── storage/
    └── data_store.py

tests/
├── contract/
│   ├── test_tufe_data_source_service.py
│   ├── test_tufe_api_key_service.py
│   ├── test_tufe_cache_service.py
│   └── test_tcmb_api_client.py
├── integration/
│   ├── test_tufe_data_fetching.py
│   └── test_data_source_attribution.py
└── unit/
    ├── test_tufe_data_source.py
    ├── test_tufe_api_key.py
    └── test_tufe_data_cache.py

app.py  # Main Streamlit application
```

**Structure Decision**: Single project structure with existing TÜFE infrastructure. The feature will extend existing services and models rather than creating new ones.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

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

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh cursor`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
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
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


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
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
