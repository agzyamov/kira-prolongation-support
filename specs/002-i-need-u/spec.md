# Feature Specification: Remove Market Comparison Feature

**Feature Branch**: `002-i-need-u`  
**Created**: 2025-10-05  
**Status**: Draft  
**Input**: User description: "i need u to get rid of market comparison feature including upload and OCR of sahibinden screenshot"

## Impact Analysis (Principle VII Compliance)

### Existing System Features (Current State)
**Core Features to Preserve:**
- ✅ Rental agreement management with conditional pricing
- ✅ Exchange rate fetching from TCMB (Central Bank of Turkey)
- ✅ Payment record calculation (TL and USD equivalents)
- ✅ Interactive Plotly visualizations
- ✅ Export charts as PNG (WhatsApp-optimized)
- ✅ Negotiation summary generation

**Features to Remove:**
- ❌ Market comparison functionality
- ❌ Screenshot upload from sahibinden.com
- ❌ OCR processing for rental price extraction
- ❌ Market rate data storage and display
- ❌ Market comparison in visualizations
- ❌ Market data in negotiation summaries

### Dependencies and Affected Components
**Files to Modify:**
- `app.py` - Remove "🏘️ Market Comparison" page and related UI
- `src/services/screenshot_parser.py` - Delete entire service
- `src/models/market_rate.py` - Delete model class
- `src/storage/data_store.py` - Remove market rate methods
- `requirements.txt` - Remove EasyOCR and related dependencies
- `README.md` - Update feature list and workflow steps

**Database Changes:**
- Remove `market_rates` table
- Clean up existing market rate data

**UI Navigation Changes:**
- Remove "🏘️ Market Comparison" from sidebar navigation
- Update page routing logic

### Potential Side Effects
**Low Risk:**
- Core rental tracking functionality remains intact
- Exchange rate and payment calculations unaffected
- Chart generation continues to work (without market comparison)

**Medium Risk:**
- Existing market data will be lost (acceptable per user request)
- Users with saved market rates will lose that data

**Mitigation:**
- Clear documentation of removed features
- Graceful handling of missing market data references

## Execution Flow (main)
```
1. Parse user description from Input ✓
2. Extract key concepts from description ✓
3. For each unclear aspect: ✓ (no ambiguities)
4. Fill User Scenarios & Testing section ✓
5. Generate Functional Requirements ✓
6. Identify Key Entities ✓
7. Run Review Checklist ✓
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

As a user of the Rental Fee Negotiation Support Tool, I want the market comparison feature completely removed so that the application focuses solely on my personal rental payment history and USD equivalent calculations without the complexity of external market data analysis.

### Acceptance Scenarios

1. **Given** I access the application, **When** I navigate through the interface, **Then** I should not see any market analysis or screenshot upload functionality

2. **Given** I am on the main dashboard, **When** I look at the navigation menu, **Then** the "🏘️ Market Comparison" page should not be available

3. **Given** I am adding a rental agreement, **When** I review the form, **Then** there should be no fields or options related to market price comparison

4. **Given** I generate a negotiation summary, **When** I review the output, **Then** it should not include any market comparison data or references

5. **Given** I export charts or reports, **When** I view the exported content, **Then** it should focus only on my personal rental payment history without market benchmarks

6. **Given** I have existing market data in the system, **When** the feature is removed, **Then** the system should handle the missing data gracefully without errors

### Edge Cases

- What happens to existing market data if any was previously uploaded?
- How does the removal affect the negotiation summary generation?
- Should any references to market comparison be removed from help text or documentation?
- How does the system handle database queries that previously included market data?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST remove the "🏘️ Market Comparison" page from the navigation menu
- **FR-002**: System MUST remove all screenshot upload functionality from the user interface
- **FR-003**: System MUST remove OCR (Optical Character Recognition) processing capabilities
- **FR-004**: System MUST remove market rate data storage and retrieval functionality
- **FR-005**: System MUST remove market comparison logic from negotiation summary generation
- **FR-006**: System MUST remove any market-related fields from rental agreement forms
- **FR-007**: System MUST remove market data from exported charts and reports
- **FR-008**: System MUST clean up any existing market data from the database
- **FR-009**: System MUST remove market-related error handling and validation
- **FR-010**: System MUST update help text and documentation to remove market comparison references
- **FR-011**: System MUST remove EasyOCR and related dependencies from requirements.txt
- **FR-012**: System MUST ensure core rental tracking functionality remains fully operational
- **FR-013**: System MUST handle missing market data references gracefully without errors

### Key Entities *(include if feature involves data)*

- **MarketRate**: Entity to be completely removed from the system
- **ScreenshotParserService**: Service to be removed as it's only used for market analysis
- **Market Analysis UI Components**: All user interface elements related to market comparison

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

## Additional Context

### Scope of Removal
This feature specification covers the complete removal of market price comparison functionality, including:

1. **User Interface Removal**:
   - Market Comparison page
   - Screenshot upload components
   - Market data display elements

2. **Backend Functionality Removal**:
   - OCR processing services
   - Market rate data models
   - Market comparison calculations

3. **Data Cleanup**:
   - Existing market data removal
   - Database schema updates
   - Related configuration cleanup

### Impact on Core Functionality
The removal of market comparison features should not affect the core rental payment tracking and USD equivalent calculation functionality. The application will continue to provide:

- Rental agreement management
- Payment history visualization
- USD equivalent calculations
- Negotiation summary generation
- Export functionality (focused on personal data only)

### User Experience
After this change, users will have a streamlined experience focused on their personal rental payment history without the complexity of external market data analysis. The application will be simpler to use and maintain.

### Dependencies to Remove
- EasyOCR library and related dependencies
- Screenshot processing utilities
- Market rate data models and services
- OCR-related error handling