
# Implementation Plan: Rental Fee Negotiation Support Tool

**Branch**: `001-problem-statement-i` | **Date**: 2025-10-05 | **Spec**: [link]
**Input**: Feature specification from `/specs/001-problem-statement-i/spec.md`

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
A web application for Turkish tenants to visualize historical rental payments in TL and USD equivalents, compare with market rates, and generate negotiation materials. The system fetches exchange rates from TCMB, parses market data from screenshots, and provides legal context for rent increases with user-selectable presentation modes.

## Technical Context
**Language/Version**: Python 3.13  
**Primary Dependencies**: Streamlit 1.50.0, Plotly 6.3.1, EasyOCR 1.7.2, Pandas 2.3.0, Requests 2.32.3  
**Storage**: SQLite (local database for persistence)  
**Testing**: pytest 8.3.0  
**Target Platform**: Web application (Streamlit Cloud or similar free hosting)  
**Project Type**: single (web application)  
**Performance Goals**: <2s page load, <5s screenshot processing, <1s chart rendering  
**Constraints**: Free hosting, no paid infrastructure, usable by non-developers  
**Scale/Scope**: Personal use, 3-4 rental agreements, shareable with colleagues

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Simple and Direct Check
- [x] Solution is straightforward and easy to understand
- [x] No unnecessary abstractions or patterns added
- [x] Code structure is as simple as possible for the requirements

### Test What Matters Check
- [x] Test strategy focuses on critical paths and hard-to-verify behavior
- [x] Not over-testing simple or obvious functionality

### Latest Stable Dependencies Check
- [x] All dependencies pinned to specific versions (no ranges)
- [x] Using latest stable releases as of September 2025
- [x] Streamlit 1.50.0 specified for web framework
- [x] Dependencies updated for security patches and bug fixes

### Done Over Perfect Check
- [x] Feature scope is focused on working functionality
- [x] Not gold-plating or over-engineering
- [x] Plan enables shipping something useful quickly

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
│   ├── __init__.py
│   ├── rental_agreement.py
│   ├── exchange_rate.py
│   ├── payment_record.py
│   ├── market_rate.py
│   └── inflation_data.py
├── services/
│   ├── __init__.py
│   ├── exchange_rate_service.py
│   ├── calculation_service.py
│   ├── screenshot_parser.py
│   ├── inflation_service.py
│   └── export_service.py
├── storage/
│   ├── __init__.py
│   └── data_store.py
└── utils/
    ├── __init__.py
    ├── chart_generator.py
    └── validators.py

tests/
├── test_models.py
├── test_services.py
├── test_storage.py
└── test_utils.py

app.py
requirements.txt
```

**Structure Decision**: Single project structure with clear separation of models, services, storage, and utilities. Streamlit app.py serves as the main entry point.

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

**Specific Task Categories**:
1. **Setup Tasks**: Project structure, dependencies, configuration
2. **Model Tasks**: RentalAgreement, ExchangeRate, PaymentRecord, MarketRate, InflationData, LegalRule, AgreementPeriod, NegotiationMode
3. **Service Tasks**: ExchangeRateService, CalculationService, ScreenshotParserService, InflationService, ExportService, DataStore, ChartGenerator
4. **Contract Tests**: Service interface tests, API integration tests
5. **Integration Tests**: End-to-end user workflows, screenshot parsing, chart generation
6. **UI Tasks**: Streamlit interface, form handling, file uploads, chart display
7. **Export Tasks**: PNG/PDF generation, negotiation summary formatting
8. **Polish Tasks**: Error handling, validation, documentation

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)
- Critical path: Models → Services → UI → Export

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

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
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.5.0 - See `.specify/memory/constitution.md`*
