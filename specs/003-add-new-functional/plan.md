
# Implementation Plan: Add New Functional Requirements

**Branch**: `003-add-new-functional` | **Date**: 2025-10-05 | **Spec**: `/specs/003-add-new-functional/spec.md`
**Input**: Feature specification from `/specs/003-add-new-functional/spec.md`

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
Add new functional requirements for the Rental Fee Negotiation Support Tool including legal CPI/cap context, neutral negotiation phrasing, negotiation mode settings, agreement period annotations, and data source disclosure. The implementation will extend the existing Streamlit application with new UI components, calculation logic, and export functionality.

## Technical Context
**Language/Version**: Python 3.13  
**Primary Dependencies**: Streamlit 1.50.0, Plotly 6.3.1, Pandas 2.3.0, Requests 2.32.3  
**Storage**: SQLite database (existing rental_negotiation.db)  
**Testing**: pytest 8.3.0  
**Target Platform**: Web application (Streamlit)  
**Project Type**: Single project (existing structure)  
**Performance Goals**: Real-time UI updates, <2s page load times  
**Constraints**: Must integrate with existing codebase, maintain backward compatibility  
**Scale/Scope**: Single user application, ~50 new lines of code per feature

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
specs/003-add-new-functional/
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
│   ├── rental_agreement.py
│   ├── exchange_rate.py
│   ├── payment_record.py
│   └── inflation_data.py
├── services/
│   ├── calculation_service.py
│   ├── exchange_rate_service.py
│   ├── inflation_service.py
│   └── export_service.py
├── utils/
│   ├── chart_generator.py
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

**Structure Decision**: Single project structure with existing Streamlit application. New features will extend existing models, services, and UI components without requiring architectural changes.

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
- Each new entity → model creation task [P]
- Each service extension → implementation task [P]
- Each UI component → integration test task
- Each quickstart scenario → validation task

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)
- Group by feature: Legal rules → Negotiation mode → Annotations → Disclosure

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md

**Task Categories**:
1. **Setup Phase**: Database migrations, new dependencies
2. **Tests First Phase**: Contract tests, unit tests, integration tests
3. **Core Implementation Phase**: Models, services, UI components
4. **Integration Phase**: Chart updates, export updates, API integration
5. **Testing & Validation Phase**: Quickstart scenarios, regression tests
6. **Documentation & Cleanup Phase**: Code cleanup, documentation updates

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
- [x] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
