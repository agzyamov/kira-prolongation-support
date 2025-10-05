# Feature Specification: Add New Functional Requirements for Rental Fee Negotiation Support Tool

**Feature Branch**: `002-add-new-functional`  
**Created**: 2025-10-05  
**Status**: Draft  
**Input**: User description: "Add new functional requirements for the "Rental Fee Negotiation Support Tool":"

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a tenant preparing for rent negotiations, I want the system to provide legally compliant and professionally presented negotiation materials so that I can confidently discuss rent increases with my landlord using official data and neutral language.

### Acceptance Scenarios
1. **Given** I have rental agreements spanning different legal periods, **When** I generate a negotiation summary, **Then** the system displays the correct legal cap (+25% for pre-July 2024, TÜFE for post-July 2024) with clear labeling
2. **Given** I want to present my case professionally, **When** I select "Calm" negotiation mode, **Then** the system removes growth arrows and uses subdued visuals
3. **Given** I want to emphasize changes strongly, **When** I select "Assertive" negotiation mode, **Then** the system highlights changes with bold numbers and prominent visual indicators
4. **Given** I view the rental payment chart, **When** I look at the timeline, **Then** I see vertical markers labeled "New Agreement (YYYY)" showing contract boundaries
5. **Given** I export a negotiation summary, **When** I review the document, **Then** it includes "Data source: TCMB (exchange rates), TÜFE (inflation)" for transparency

### Edge Cases
- What happens when TÜFE data is unavailable for a specific period?
- How does the system handle agreements that span the July 1, 2024 legal boundary?
- What if a user switches negotiation modes mid-session?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-017**: System MUST automatically determine the applicable legal rule for rent increases based on agreement period (pre-July 2024: +25% cap, post-July 2024: TÜFE)
- **FR-018**: System MUST display legal maximum increase with clear labels ("+25% (limit until July 2024)" or "+CPI (Yearly TÜFE)")
- **FR-019**: System MUST use neutral negotiation phrasing ("Aligned with market average") instead of emotionally charged terms ("Above average")
- **FR-020**: System MUST provide user-selectable negotiation modes (Calm and Assertive)
- **FR-021**: System MUST hide growth arrows and tone down visuals in Calm mode
- **FR-022**: System MUST highlight changes and use bold numbers in Assertive mode
- **FR-023**: System MUST include vertical markers labeled "New Agreement (YYYY)" on the TL vs USD chart to show contract boundaries
- **FR-024**: System MUST include "Data source: TCMB (exchange rates), TÜFE (inflation)" in every exported summary
- **FR-025**: System MUST fetch official TÜFE (CPI) values from TCMB for periods after July 1, 2024
- **FR-026**: System MUST handle agreements that span the July 1, 2024 legal boundary by applying the appropriate rule for each period segment

### Key Entities *(include if feature involves data)*
- **Legal Rule**: Represents the applicable rent increase regulation (fixed cap vs TÜFE) with effective date range and calculation method
- **Negotiation Mode**: User preference setting that controls visual presentation style (Calm/Assertive) and language tone
- **Agreement Period**: Time segment of a rental agreement that determines which legal rule applies
- **TÜFE Data**: Official inflation data from TCMB with date, value, and source attribution

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous  
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---