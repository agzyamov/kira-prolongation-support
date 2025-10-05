# Implementation Plan: Remove Market Comparison Feature

**Branch**: `002-i-need-u` | **Date**: 2025-10-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-i-need-u/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✓
2. Fill Technical Context (scan for NEEDS CLARIFICATION) ✓
3. Fill the Constitution Check section ✓
4. Evaluate Constitution Check section ✓
5. Execute Phase 0 → research.md ✓
6. Execute Phase 1 → contracts, data-model.md, quickstart.md ✓
7. Re-evaluate Constitution Check section ✓
8. Plan Phase 2 → Describe task generation approach ✓
9. STOP - Ready for /tasks command ✓
```

## Summary

Remove market comparison functionality from the Rental Fee Negotiation Support Tool to simplify the application and focus solely on personal rental payment tracking. This includes removing screenshot upload, OCR processing, market rate data storage, and all related UI components while preserving core rental agreement management, exchange rate tracking, and visualization features.

**Key Changes**:
- Remove "🏘️ Market Comparison" page from navigation
- Delete screenshot upload and OCR processing capabilities
- Remove market rate data models and storage
- Clean up existing market data from database
- Update documentation and dependencies

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Streamlit 1.50.0, Plotly 6.3.1, Pandas 2.3.0, Requests 2.32.3  
**Storage**: SQLite (remove market_rates table)  
**Testing**: pytest 8.3.0 for regression testing  
**Target Platform**: Web browser via Streamlit  
**Project Type**: Single web application (Streamlit)  
**Performance Goals**: Maintain <3s page load, remove OCR processing overhead  
**Constraints**: Zero infrastructure costs, preserve core functionality  
**Scale/Scope**: Single user + ~10 colleagues, ~10 rental agreements, no market data

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
specs/002-i-need-u/
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
├── models/              # Remove market_rate.py
├── services/            # Remove screenshot_parser.py
├── storage/             # Remove market rate methods from data_store.py
└── utils/               # Keep chart_generator.py (remove market comparison logic)

tests/
├── contract/            # Remove screenshot parser tests
├── integration/         # Update integration tests
└── unit/                # Remove market rate tests

app.py                   # Remove Market Comparison page
requirements.txt         # Remove EasyOCR dependencies
README.md                # Update feature documentation
```

**Structure Decision**: Single project structure maintained, removing market comparison components while preserving core rental tracking functionality.

## Phase 0: Outline & Research

### Research Tasks Completed:

1. **Dependency Analysis**: Identified EasyOCR and related dependencies to remove
2. **Database Schema Impact**: Analyzed market_rates table removal requirements
3. **UI Component Mapping**: Catalogued all market comparison UI elements
4. **Service Dependencies**: Mapped ScreenshotParserService usage and removal
5. **Integration Points**: Identified where market data is referenced in other features

### Key Findings:
- Market comparison is isolated feature with minimal integration points
- Core rental tracking functionality is independent of market features
- EasyOCR dependency can be safely removed without affecting other features
- Database cleanup required for existing market data

**Output**: research.md with dependency removal strategy

## Phase 1: Design & Contracts

### Data Model Changes:
- **Remove**: MarketRate entity and related database table
- **Preserve**: All existing rental agreement, exchange rate, and payment record models
- **Update**: Database schema to remove market_rates table

### Service Contract Changes:
- **Remove**: ScreenshotParserService interface and implementation
- **Update**: DataStore to remove market rate methods
- **Preserve**: All other service contracts remain unchanged

### UI Contract Changes:
- **Remove**: Market Comparison page navigation and routing
- **Update**: Chart generation to remove market comparison overlays
- **Preserve**: All other UI functionality

### Test Scenarios:
- Verify market comparison page is removed from navigation
- Confirm existing market data is cleaned up gracefully
- Validate core rental tracking functionality remains intact
- Test error handling for missing market data references

**Output**: data-model.md, /contracts/*, quickstart.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate removal tasks from Phase 1 design docs
- Each removed component → deletion task [P]
- Each modified component → update task [P]
- Database cleanup → migration task
- Integration tests → update task
- Documentation → update task

**Ordering Strategy**:
- Dependency order: Remove UI first, then services, then models, then database
- Mark [P] for parallel execution (independent file deletions)
- Test updates after implementation changes

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations - this is a simplification effort*

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
*Based on Constitution v1.4.0 - See `.specify/memory/constitution.md`*