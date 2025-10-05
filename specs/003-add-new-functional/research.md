# Research: Add New Functional Requirements

**Feature**: Add New Functional Requirements for Rental Fee Negotiation Support Tool  
**Date**: 2025-10-05  
**Branch**: 003-add-new-functional

## Research Summary

All technical context is well-defined from existing codebase. No unknowns require research as the implementation will extend existing Streamlit application with established patterns.

## Technical Decisions

### Decision: Extend Existing Models and Services
**Rationale**: The new functional requirements can be implemented by extending existing models and services without architectural changes. This maintains simplicity and leverages existing patterns.

**Alternatives considered**: 
- Creating new separate models/services - rejected as it would duplicate existing functionality
- Refactoring existing architecture - rejected as it would violate "Simple and Direct" principle

### Decision: Use Streamlit Session State for Negotiation Mode
**Rationale**: Streamlit's session state provides built-in persistence across page interactions, which is sufficient for the negotiation mode preference requirement.

**Alternatives considered**:
- Database storage - rejected as overkill for single-user preference
- File-based storage - rejected as session state is simpler and more appropriate

### Decision: Extend Existing Chart Generator
**Rationale**: The existing ChartGenerator class already handles Plotly visualizations. Adding new chart types and styling options follows established patterns.

**Alternatives considered**:
- Creating new chart service - rejected as it would duplicate existing functionality
- Using different charting library - rejected as it would break consistency

### Decision: Use TCMB API for TÜFE Data
**Rationale**: Constitution Principle V mandates TCMB as single source of truth. TÜFE (CPI) data should come from the same authoritative source as exchange rates.

**Alternatives considered**:
- Third-party inflation APIs - rejected as they violate constitutional principle
- Manual entry only - rejected as TCMB should provide official CPI data

## Implementation Approach

### Legal Rule Determination
- Extend `CalculationService` with date-based logic to determine applicable legal rule
- Use datetime comparison to check if period is before/after July 1, 2024
- Return appropriate rule type (25% cap vs CPI-based)

### Negotiation Mode Implementation
- Add session state variable for user preference
- Extend chart generation to accept mode parameter
- Modify visual styling based on mode (arrows, colors, emphasis)

### Agreement Period Annotations
- Extend `ChartGenerator` to accept agreement dates
- Add vertical markers to TL vs USD charts
- Label markers with "New Agreement (YYYY)" format

### Data Source Disclosure
- Extend `ExportService` to include data source line
- Add to all exported summaries and reports
- Use consistent format: "Data source: TCMB (exchange rates), TÜFE (inflation)"

### Neutral Phrasing
- Update text generation in export and summary functions
- Replace emotionally charged terms with neutral alternatives
- Ensure consistency across all user-facing text

## Dependencies

### Existing Dependencies (No Changes Required)
- Streamlit 1.50.0 - for UI components and session state
- Plotly 6.3.1 - for chart generation and styling
- Pandas 2.3.0 - for data manipulation
- Requests 2.32.3 - for TCMB API calls

### New Dependencies (None Required)
All functionality can be implemented using existing dependencies.

## Risk Assessment

### Low Risk
- Extending existing models and services
- Adding UI components to existing Streamlit app
- Using session state for preferences

### Medium Risk
- TCMB API changes affecting TÜFE data availability
- Chart styling changes affecting existing visualizations

### Mitigation
- Implement fallback to manual entry for TÜFE data
- Test chart changes thoroughly to ensure no regression
- Use feature flags if needed for gradual rollout

## Conclusion

The implementation approach is straightforward and follows existing patterns. No significant research or architectural decisions are required. The feature can be implemented by extending existing components with minimal risk.
