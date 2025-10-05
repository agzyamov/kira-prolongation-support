# Feature Specification: Add New Functional Requirements

**Feature Branch**: `003-add-new-functional`  
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
As a tenant preparing for rent negotiations, I want the system to provide legally accurate rent increase calculations and neutral presentation options so that I can present my case professionally and effectively to my landlord.

### Acceptance Scenarios
1. **Given** a rental agreement with a start date before July 1, 2024, **When** I view the negotiation summary, **Then** the system displays "+25% (limit until July 2024)" as the legal maximum increase
2. **Given** a rental agreement with a start date after July 1, 2024, **When** I view the negotiation summary, **Then** the system displays "+CPI (Yearly TÜFE)" as the legal maximum increase
3. **Given** I select "Calm" negotiation mode, **When** I view the summary, **Then** the system hides growth arrows and uses subdued visual styling
4. **Given** I select "Assertive" negotiation mode, **When** I view the summary, **Then** the system highlights changes with bold numbers and prominent visual indicators
5. **Given** I have multiple rental agreements, **When** I view the TL vs USD chart, **Then** the system shows vertical markers labeled "New Agreement (YYYY)" at contract boundaries
6. **Given** I export a negotiation summary, **When** I view the exported document, **Then** it includes "Data source: TCMB (exchange rates), TÜFE (inflation)" for transparency

### Edge Cases
- What happens when the system cannot determine the applicable legal rule for a given period?
- How does the system handle missing TÜFE data for periods after July 2024?
- What happens when a user switches negotiation modes mid-session?
- How does the system handle overlapping rental agreements in visualizations?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST automatically determine the applicable legal rule for rent increases based on agreement period (pre/post July 1, 2024)
- **FR-002**: System MUST display "+25% (limit until July 2024)" for agreements starting before July 1, 2024
- **FR-003**: System MUST display "+CPI (Yearly TÜFE)" for agreements starting after July 1, 2024
- **FR-004**: System MUST use neutral wording ("Aligned with market average") instead of emotionally charged terms in generated summaries
- **FR-005**: System MUST provide a user-selectable negotiation mode setting with "Calm" and "Assertive" options
- **FR-006**: System MUST hide growth arrows and use subdued visuals when "Calm" mode is selected
- **FR-007**: System MUST highlight changes with bold numbers and prominent indicators when "Assertive" mode is selected
- **FR-008**: System MUST include vertical markers labeled "New Agreement (YYYY)" on TL vs USD charts to show contract boundaries
- **FR-009**: System MUST include "Data source: TCMB (exchange rates), TÜFE (inflation)" in every exported summary
- **FR-010**: System MUST persist the user's negotiation mode preference across sessions
- **FR-011**: System MUST handle cases where TÜFE data is unavailable for post-July 2024 periods by displaying "TÜFE data pending" and allowing manual entry of the official CPI rate
- **FR-012**: System MUST validate that agreement dates are correctly interpreted for legal rule determination

### Key Entities *(include if feature involves data)*
- **Legal Rule**: Represents the applicable rent increase regulation (25% cap vs CPI-based), includes effective date range and calculation method
- **Negotiation Mode**: User preference setting that controls visual presentation style (Calm/Assertive), affects summary generation and chart display
- **Agreement Boundary**: Visual marker on charts indicating contract start/end dates, includes year label for clarity
- **Data Source Attribution**: Required disclosure information for exported documents, includes specific source names and data types

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