# Quickstart Manual Testing Guide

**Date**: 2025-10-05  
**Purpose**: Manual testing guide for user acceptance testing  
**Target**: Non-technical users + developers

## Overview

This guide walks through manual testing of all key features in the Rental Fee Negotiation Support Tool. Tests are performed through the Streamlit web interface.

## Prerequisites

1. **Application Running**:
   ```bash
   streamlit run app.py
   ```
   Application should open in browser at `http://localhost:8501`

2. **Test Data Available**:
   - Sample rental agreement dates/amounts
   - Sample sahibinden.com screenshots
   - Sample inflation CSV (optional)

## Test Scenarios

### Scenario 1: Enter Rental Agreement

**Objective**: Test adding historical rental agreements

**Steps**:
1. Open application in browser
2. Navigate to "Rental Agreements" section
3. Click "Add New Agreement"
4. Enter details:
   - Start Date: November 2022
   - End Date: October 2023
   - Monthly Rent: 15,000 TL
   - Notes: "Initial agreement"
5. Click "Save"

**Expected Result**:
- Success message appears
- Agreement appears in list below
- Agreement is saved to database

**Pass Criteria**:
- [ ] Form accepts valid dates
- [ ] Form validates rent amount > 0
- [ ] Agreement appears in list immediately
- [ ] Agreement persists after page refresh

---

### Scenario 2: Enter Conditional Agreement

**Objective**: Test conditional pricing rules

**Steps**:
1. Add new agreement with conditional rules:
   - Start Date: December 2024
   - End Date: (leave empty - ongoing)
   - Base Monthly Rent: 31,000 TL
   - Enable "Conditional Pricing"
   - Add Rule 1:
     - Condition: "If USD exchange rate < 40 TL"
     - Amount: 35,000 TL
   - Add Rule 2:
     - Condition: "If USD exchange rate >= 40 TL"
     - Amount: 40,000 TL
2. Save agreement

**Expected Result**:
- Agreement saved with conditional rules icon
- Rules stored correctly in database
- Agreement summary shows "Conditional Pricing"

**Pass Criteria**:
- [ ] Can add multiple conditional rules
- [ ] Conditions are validated
- [ ] Rules display correctly in list view
- [ ] Conditional logic applies to payment calculations

---

### Scenario 3: Fetch Exchange Rates

**Objective**: Test automatic exchange rate fetching

**Steps**:
1. Navigate to "Exchange Rates" section
2. Click "Fetch Rates"
3. Select date range: November 2022 to October 2024
4. Click "Fetch"
5. Wait for progress indicator

**Expected Result**:
- Rates fetched for each month in range
- Success message shows: "Fetched 24 exchange rates"
- Rates appear in table with source (TCMB or backup)
- Rates are cached in database

**Pass Criteria**:
- [ ] Fetches rates from TCMB successfully
- [ ] Falls back to backup API if TCMB fails
- [ ] Shows progress during fetch
- [ ] Displays error message if both APIs fail
- [ ] Caches rates to avoid redundant API calls

---

### Scenario 4: View Payment Calculations

**Objective**: Test USD equivalent calculations

**Steps**:
1. Navigate to "Payments & Calculations" section
2. Click "Calculate Payments"
3. View generated payment records

**Expected Result**:
- Table shows monthly payments in TL and USD
- USD amounts calculated correctly (TL / exchange rate)
- Conditional pricing applies for Dec 2024 onwards
- Total calculations shown at bottom

**Example Verification**:
- November 2022: 15,000 TL ÷ 18.65 (rate) = ~804 USD
- Verify a few manually to ensure accuracy

**Pass Criteria**:
- [ ] All months have payment records
- [ ] USD calculations are mathematically correct
- [ ] Conditional rules apply at correct dates
- [ ] Totals sum correctly
- [ ] Percentage changes calculated correctly

---

### Scenario 5: Upload Screenshot for Market Rates

**Objective**: Test OCR parsing of sahibinden.com screenshots

**Steps**:
1. Navigate to "Market Comparison" section
2. Click "Upload Screenshot"
3. Select a sahibinden.com screenshot showing rental listings
4. Wait for OCR processing
5. Review parsed results

**Expected Result**:
- Screenshot uploads successfully
- OCR extracts rental prices
- Prices displayed with confidence scores
- User can verify/edit parsed prices

**Pass Criteria**:
- [ ] File upload works (PNG, JPG accepted)
- [ ] OCR extracts at least some prices
- [ ] Confidence score shown for each price
- [ ] User can manually correct incorrect prices
- [ ] Can mark prices as "verified"
- [ ] Low-confidence prices flagged for review

**Edge Cases to Test**:
- [ ] Poor quality image (blurry)
- [ ] Multiple prices in one screenshot
- [ ] Turkish number formatting (35.000 TL)
- [ ] No prices in screenshot (error handling)

---

### Scenario 6: Import Inflation Data

**Objective**: Test inflation data import

**Steps**:
1. Navigate to "Inflation Data" section
2. Click "Import from CSV"
3. Upload sample TUIK inflation CSV
4. Review imported data

**Expected Result**:
- CSV parsed successfully
- Inflation rates displayed in table by month/year
- Legal maximum rent increases calculated

**Pass Criteria**:
- [ ] CSV upload works
- [ ] Parses month, year, rate columns
- [ ] Displays import summary (X rows imported)
- [ ] Handles duplicate months (updates existing)
- [ ] Shows parsing errors for invalid CSV

**Fallback Test**:
- [ ] Manual entry: Can add single inflation rate
- [ ] Manual entry: Validates rate is reasonable (-100% to +200%)

---

### Scenario 7: View Visualizations

**Objective**: Test chart generation and display

**Steps**:
1. Navigate to "Visualizations" section
2. View "TL vs USD Payments Over Time" chart
3. Hover over data points
4. Toggle between chart views

**Expected Result**:
- Line chart shows TL payments (rising trend)
- Line chart shows USD payments (more stable)
- Both lines on same chart for easy comparison
- Hover shows exact values
- Interactive (can zoom, pan)

**Chart Types to Test**:
- [ ] Line chart: TL vs USD over time
- [ ] Bar chart: Payment comparison by agreement period
- [ ] Comparison chart: Your rent vs market rates
- [ ] Summary chart: Total paid in TL vs USD

**Pass Criteria**:
- [ ] Charts render without errors
- [ ] Data points match payment records
- [ ] Hover tooltips show correct values
- [ ] Charts are readable and clear
- [ ] Colors support negotiation position (highlight USD stability)

---

### Scenario 8: Generate Negotiation Summary

**Objective**: Test summary generation for negotiation

**Steps**:
1. Navigate to "Negotiation Summary" section
2. Click "Generate Summary"
3. Review all components

**Expected Result**:
- Summary shows key statistics:
  - Total TL increase: 166.7% (from 15K to 40K)
  - USD equivalent: More stable (varies less)
  - Market comparison: Your rent vs avg market
  - Legal maximum: Based on inflation rate
- Clear call-outs for negotiation points

**Pass Criteria**:
- [ ] All statistics calculated correctly
- [ ] Comparison with market rates shown
- [ ] Legal maximum rent displayed
- [ ] Negotiation points highlighted
- [ ] Summary is clear and easy to understand

**Key Negotiation Points to Verify**:
- [ ] "USD rent already increased by X%"
- [ ] "Current rent is Y% above/below market"
- [ ] "Legal maximum increase is Z% (inflation)"
- [ ] "You've already absorbed TL devaluation"

---

### Scenario 9: Export for WhatsApp

**Objective**: Test export functionality

**Steps**:
1. From "Negotiation Summary" section
2. Click "Export as PNG"
3. Wait for image generation
4. Download image

**Expected Result**:
- PNG image downloaded to computer
- Image contains all key charts and statistics
- Image is optimized for mobile viewing
- File size < 2MB (WhatsApp friendly)
- Clear and readable on phone screen

**Pass Criteria**:
- [ ] Export button generates image successfully
- [ ] Image includes all relevant charts
- [ ] Text is readable at mobile size
- [ ] File size is reasonable (< 2MB)
- [ ] Image can be shared via WhatsApp

**Additional Export Tests**:
- [ ] Export as PDF (if implemented)
- [ ] Download individual charts as PNG
- [ ] Batch export multiple charts

---

### Scenario 10: End-to-End User Journey

**Objective**: Complete user journey from data entry to negotiation

**Steps**:
1. Enter all historical rental agreements (3-4 agreements)
2. Fetch exchange rates for entire period
3. Upload 2-3 market comparison screenshots
4. Import inflation data CSV
5. Generate all visualizations
6. Create negotiation summary
7. Export as PNG for WhatsApp

**Expected Result**:
- Complete workflow works smoothly
- No errors or crashes
- Data flows correctly between steps
- Final export is professional and useful

**Pass Criteria**:
- [ ] Can complete entire workflow without errors
- [ ] Data persists between sections
- [ ] No data loss on page refresh
- [ ] Export contains all necessary information
- [ ] Workflow feels intuitive

**Time to Complete**: Should take < 15 minutes for experienced user

---

## Edge Cases & Error Handling

### Edge Case Tests

1. **Empty State**:
   - [ ] App works with no data entered
   - [ ] Shows helpful "Get Started" messages
   - [ ] No crashes on empty database

2. **Invalid Data**:
   - [ ] Rejects negative rent amounts
   - [ ] Rejects invalid dates (end before start)
   - [ ] Validates exchange rates > 0
   - [ ] Handles malformed CSV gracefully

3. **API Failures**:
   - [ ] Handles TCMB API timeout
   - [ ] Falls back to backup API
   - [ ] Shows error message if all APIs fail
   - [ ] Allows retry after failure

4. **OCR Failures**:
   - [ ] Handles unreadable screenshots
   - [ ] Provides manual entry option
   - [ ] Shows helpful error messages
   - [ ] Doesn't crash on corrupt images

5. **Large Datasets**:
   - [ ] Handles 20+ rental agreements
   - [ ] Charts with 100+ data points
   - [ ] 50+ market rate screenshots
   - [ ] Export still works with large data

### Browser Compatibility

Test in multiple browsers:
- [ ] Chrome (primary)
- [ ] Safari (macOS/iOS)
- [ ] Firefox
- [ ] Mobile browsers (responsive)

### Performance Tests

- [ ] Page loads in < 3 seconds
- [ ] Exchange rate fetch < 10 seconds
- [ ] OCR processing < 5 seconds per screenshot
- [ ] Chart rendering < 2 seconds
- [ ] Export generation < 5 seconds

---

## Bug Reporting Template

If issues found during testing, report with:

```
**Issue Title**: [Brief description]

**Steps to Reproduce**:
1. ...
2. ...

**Expected Result**: ...

**Actual Result**: ...

**Screenshots**: [Attach if applicable]

**Browser**: Chrome 118 / Safari 17 / etc.

**Severity**: Critical / High / Medium / Low
```

---

## Success Criteria

Application is ready for production when:

- [ ] All 10 test scenarios pass
- [ ] All edge cases handled gracefully
- [ ] No critical or high severity bugs
- [ ] Export files work on WhatsApp
- [ ] Non-technical users can complete workflow
- [ ] Constitution principles satisfied:
  - [ ] Simple and Direct: Easy to use
  - [ ] Test What Matters: Core calculations verified
  - [ ] Done Over Perfect: MVP functional
  - [ ] Context7: Built with current libraries

---

## Next Steps

After manual testing passes:
1. Deploy to Streamlit Cloud
2. Share app URL with colleagues for beta testing
3. Gather feedback
4. Iterate on UX improvements
5. Use in real negotiation (ultimate test!)

