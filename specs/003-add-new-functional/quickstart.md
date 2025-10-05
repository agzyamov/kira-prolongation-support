# Quickstart: Add New Functional Requirements

**Feature**: Add New Functional Requirements for Rental Fee Negotiation Support Tool  
**Date**: 2025-10-05  
**Branch**: 003-add-new-functional

## Test Scenarios

### Scenario 1: Legal CPI/Cap Context
**Given**: A rental agreement with payments spanning before and after July 1, 2024  
**When**: I view the negotiation summary  
**Then**: The "Legal max increase" must correctly display:
- "+25% (limit until July 2024)" for periods up to June 30, 2024
- "+CPI (Yearly TÜFE)" for periods after July 1, 2024

**Test Steps**:
1. Create rental agreement with start date before July 1, 2024
2. Add payment records for both pre and post July 2024 periods
3. Navigate to "🤝 Negotiation Summary" page
4. Verify legal rule labels are correct for each period
5. Check that calculations use appropriate rules

### Scenario 2: Neutral Negotiation Phrasing
**Given**: A generated negotiation summary  
**When**: I review the phrasing  
**Then**: All terms related to market position must be neutral (e.g., "Aligned with market average")

**Test Steps**:
1. Generate a negotiation summary
2. Review all text in the summary
3. Verify no emotionally charged terms are used
4. Check that neutral alternatives are used consistently

### Scenario 3: Negotiation Mode - Calm
**Given**: The application is running  
**When**: I select "Calm" negotiation mode  
**Then**: The visualizations must hide growth arrows and use toned-down visuals

**Test Steps**:
1. Navigate to any page with charts
2. Select "Calm" mode from negotiation mode selector
3. Verify charts have subdued styling
4. Check that growth arrows are hidden
5. Confirm colors are muted/toned down

### Scenario 4: Negotiation Mode - Assertive
**Given**: The application is running  
**When**: I select "Assertive" negotiation mode  
**Then**: The visualizations must highlight changes and use bold numbers

**Test Steps**:
1. Navigate to any page with charts
2. Select "Assertive" mode from negotiation mode selector
3. Verify charts have bold styling
4. Check that changes are highlighted
5. Confirm numbers are displayed prominently

### Scenario 5: Agreement Period Annotations
**Given**: A TL vs USD chart is displayed  
**When**: Multiple rental agreements exist  
**Then**: Vertical markers labeled "New Agreement (YYYY)" must appear at the start date of each new agreement

**Test Steps**:
1. Create multiple rental agreements with different start dates
2. Add payment records for each agreement
3. Navigate to "📈 Visualizations" page
4. View the TL vs USD chart
5. Verify vertical markers appear at agreement start dates
6. Check that markers are labeled correctly

### Scenario 6: Data Source Disclosure
**Given**: Any exported summary  
**When**: I review the document  
**Then**: It must include the line "Data source: TCMB (exchange rates), TÜFE (inflation)"

**Test Steps**:
1. Generate any export (PDF, CSV, or text summary)
2. Open the exported document
3. Search for "Data source: TCMB (exchange rates), TÜFE (inflation)"
4. Verify the line appears in all exports

### Scenario 7: TÜFE Data Handling
**Given**: A period after July 1, 2024  
**When**: TÜFE data is unavailable  
**Then**: The system must display "TÜFE data pending" and allow manual entry

**Test Steps**:
1. Create rental agreement with start date after July 1, 2024
2. Ensure TÜFE data is not available for the period
3. Navigate to negotiation summary
4. Verify "TÜFE data pending" is displayed
5. Check that manual entry option is available
6. Test manual entry functionality

### Scenario 8: Negotiation Mode Persistence
**Given**: I have selected a negotiation mode  
**When**: I navigate between pages or refresh the application  
**Then**: My negotiation mode preference must persist

**Test Steps**:
1. Select "Assertive" negotiation mode
2. Navigate to different pages
3. Verify mode remains "Assertive"
4. Refresh the application
5. Check that mode is still "Assertive"

## Validation Checklist

### Functional Requirements
- [ ] Legal rule determination works correctly for pre/post July 2024 periods
- [ ] Neutral phrasing is used in all generated summaries
- [ ] Negotiation mode affects chart styling appropriately
- [ ] Agreement period annotations appear on charts
- [ ] Data source disclosure appears in all exports
- [ ] TÜFE data fallback works when data is unavailable
- [ ] Negotiation mode preference persists across sessions

### User Experience
- [ ] UI is intuitive and easy to use
- [ ] Mode changes are immediately visible
- [ ] Charts are clear and informative
- [ ] Export functionality works correctly
- [ ] Error messages are helpful and clear

### Performance
- [ ] Page load times remain under 2 seconds
- [ ] Chart generation is responsive
- [ ] Mode changes are immediate
- [ ] Export generation is fast

### Integration
- [ ] Existing functionality remains unchanged
- [ ] New features integrate seamlessly
- [ ] Database changes are applied correctly
- [ ] TCMB API integration works for TÜFE data

## Edge Cases

### Edge Case 1: Agreement Starting Exactly on July 1, 2024
**Test**: Verify that agreements starting exactly on July 1, 2024 use CPI-based rules

### Edge Case 2: Missing TÜFE Data for Current Year
**Test**: Verify fallback behavior when TÜFE data is not available for current year

### Edge Case 3: Multiple Agreements with Same Start Date
**Test**: Verify that multiple agreements with same start date are handled correctly

### Edge Case 4: Invalid Negotiation Mode
**Test**: Verify that invalid mode values default to "calm"

### Edge Case 5: Export with No Data
**Test**: Verify that exports with no data still include data source disclosure

## Success Criteria

### Primary Success Criteria
1. All 8 test scenarios pass
2. No regression in existing functionality
3. Performance requirements met
4. User experience is smooth and intuitive

### Secondary Success Criteria
1. Code is maintainable and follows existing patterns
2. Tests provide good coverage of new functionality
3. Documentation is clear and complete
4. Error handling is robust

## Rollback Plan

If issues are discovered during testing:
1. Revert to previous commit
2. Run existing test suite to ensure no regressions
3. Investigate issues in isolation
4. Fix issues and re-test
5. Re-deploy when all tests pass
