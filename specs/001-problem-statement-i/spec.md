# Feature Specification: Rental Fee Negotiation Support Tool

**Feature Branch**: `001-problem-statement-i`  
**Created**: 2025-10-05  
**Status**: Ready for Planning  
**Input**: User description: "I live in Turkiye where inflation is relatively high. As a result, there is a law that allows landlords to raise the rent fee maximum for the inflation percentage and landlords perceive that they MUST increase the fee on the maximum allowed rate. I as a tenant want to have a graphical representation of how many Turkish liras did I pay every year and how much USD it correlates to. My main point is I want to pay more or less same rental fee in USD. Also I'd like to consider market rental fees for similar apartments."

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

As a tenant in Turkey preparing for annual rent negotiation, I want to visualize my historical rental payments in both Turkish Lira (TL) and USD equivalents so that I can demonstrate that my USD-equivalent rent has already increased significantly despite landlord assumptions. I also want to compare my current rent with market rates for similar apartments to support my negotiation position.

**Context**: The tenant needs to negotiate rental agreements on an annual basis. The solution must work for any future negotiation period without additional development. Historical example agreements:
- November 2022: 15,000 TL
- November 2023: 25,000 TL
- November 2024: 31,000 TL (with conditional increase: 35,000 TL if USD exchange rate < 40 TL, or 40,000 TL if USD >= 40 TL for the period Dec 2024 onwards)

### Acceptance Scenarios

1. **Given** I have entered my historical rental agreements (dates and TL amounts), **When** I view the visualization, **Then** I see a simple graph showing both TL payments over time and their USD equivalents using monthly average exchange rates

2. **Given** I have historical rental data entered, **When** I calculate USD equivalents, **Then** the system uses accurate historical monthly average USD/TL exchange rates from a free, reputable source

3. **Given** I take a screenshot of sahibinden.com filtered map view showing rental listings, **When** I upload the screenshot, **Then** the system parses rental fees from the image and displays them as market comparison benchmarks

4. **Given** I have market rental data parsed, **When** I view the comparison, **Then** I see how my current rent compares to market rates for similar apartments in my area

5. **Given** I'm preparing for any future rent negotiation, **When** I generate a negotiation summary, **Then** I see key data points: TL increase percentage, USD equivalent changes, market rate comparisons, and legal maximum increase based on official inflation

6. **Given** I have conditional rental agreements (like the 2024 agreement with exchange rate triggers), **When** I track payments, **Then** the system correctly applies the appropriate rent amount based on actual monthly average exchange rates

7. **Given** I have completed my analysis, **When** I export the summary, **Then** I receive a shareable format (image or PDF) that I can easily send via WhatsApp to my landlord

### Edge Cases

- What happens when exchange rate API is temporarily unavailable?
- How does the system handle screenshot parsing failures (poor quality, unexpected format)?
- What if no market listings are found in the screenshot?
- How should the system validate that parsed rental prices are reasonable?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to manually enter historical rental agreement data including start date, end date, rental amount in TL, and any conditional pricing rules (bulk import not required - only 3-4 agreements typical)

- **FR-002**: System MUST store rental agreement history persistently

- **FR-003**: System MUST automatically fetch historical USD/TL exchange rates from a free, open, and reputable source (e.g., exchangerate-api.io, TCMB open data, or similar)

- **FR-004**: System MUST calculate the USD equivalent of each TL rental payment using the monthly average exchange rate for that payment period

- **FR-005**: System MUST display a simple graphical visualization showing rental payments over time in both TL and USD, optimized to support the user's negotiation position

- **FR-006**: System MUST allow users to upload screenshots from sahibinden.com (filtered map view showing rental listings) and parse rental fees from the screenshot to use as market comparison benchmarks

- **FR-007**: System MUST display a comparison between the user's rental payments and market rates parsed from screenshots

- **FR-008**: System MUST handle conditional rental agreements (e.g., "if USD rate > 40 TL, then rent = 40,000 TL") and calculate actual payments based on historical exchange rates

- **FR-009**: System MUST calculate the total percentage increase in rent from the first period to the current period in both TL and USD

- **FR-010**: System MUST allow users to export or share the visualization and negotiation summary as images or PDF format suitable for WhatsApp sharing

- **FR-011**: System MUST provide a summary view suitable for presenting during rent negotiations, highlighting key arguments (USD stability, market comparisons, legal maximum increase)

- **FR-012**: System MUST fetch and display official Turkish inflation rates to show the legal maximum rent increase the landlord could request

### Key Entities

- **Rental Agreement**: Represents a time period with associated rental terms
  - Start date (month/year)
  - End date (month/year)
  - Base rental amount (TL)
  - Conditional pricing rules (optional: conditions based on exchange rates)
  - Actual amounts paid per month

- **Exchange Rate Data**: Historical USD/TL exchange rates
  - Month/Year
  - Monthly average exchange rate (TL per 1 USD)
  - Source of data

- **Payment Record**: Individual rental payment
  - Payment month/year
  - Amount in TL
  - Calculated USD equivalent
  - Associated rental agreement

- **Market Rate Data**: Comparable apartment rental information parsed from screenshots
  - Rental amount (TL)
  - Location/area (if parseable)
  - Source (sahibinden.com screenshot)

- **Inflation Data**: Official Turkish inflation rates
  - Period (month/year)
  - Inflation rate (percentage)
  - Legal maximum rent increase allowed

### Non-Functional Requirements

- **NFR-001**: Visualizations MUST be clear, simple, and optimized to present a strong negotiation position

- **NFR-002**: Exchange rate data MUST be from a free, open, and reputable source with good reliability

- **NFR-003**: System MUST work as a web application or desktop application that requires no paid infrastructure and is usable by non-developer users (e.g., can be shared with colleagues in Turkey)

- **NFR-004**: Screenshot parsing MUST handle typical sahibinden.com map view layouts

- **NFR-005**: Export functionality MUST produce files easily shareable via WhatsApp (optimized file sizes)

- **NFR-006**: System MUST work for any future negotiation period without requiring code changes or additional development (evergreen solution)

---

## Review & Acceptance Checklist

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

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked and resolved
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

**Status**: ✅ Ready for `/plan` command

---

## Additional Context

### Example Historical Data (for reference only)
The following are example historical agreements. The system must support any date ranges and rental amounts:
- November 2022 - October 2023: 15,000 TL/month
- November 2023 - October 2024: 25,000 TL/month
- November 2024 - November 2024: 31,000 TL
- December 2024 onwards: Conditional pricing
  - If USD < 40 TL: 35,000 TL/month
  - If USD >= 40 TL: 40,000 TL/month

### Legal Context
Turkish rental law allows landlords to increase rent up to the official inflation rate percentage. This creates pressure for maximum increases even when currency devaluation may have already compensated landlords.

### User Goal
Maintain approximately stable rental cost in USD terms, using data-driven negotiation to push back against automatic maximum increases.

### Key Design Decisions (from clarifications)
- **Evergreen Solution**: Must work for any future negotiation period without code changes or additional development
- **Data Entry**: Manual entry for 3-4 historical agreements (no bulk import needed)
- **Exchange Rates**: Monthly averages from free, reputable API (must support historical and current data)
- **Market Data**: Screenshot upload from sahibinden.com with automatic parsing
- **Visualizations**: Simple charts that support negotiation, shareable via WhatsApp
- **Platform**: Free-to-host, accessible to non-developers (colleagues can use it)
- **Inflation Tracking**: Display official rates to show legal maximum increase
