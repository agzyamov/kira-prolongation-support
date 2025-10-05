# Research: Remove Market Comparison Feature

**Feature**: Remove Market Comparison Feature  
**Date**: 2025-10-05  
**Branch**: `002-i-need-u`

## Research Summary

This research phase analyzed the removal of market comparison functionality from the Rental Fee Negotiation Support Tool. The analysis focused on identifying all components that need to be removed, understanding dependencies, and ensuring core functionality remains intact.

## Key Research Areas

### 1. Dependency Analysis

**Decision**: Remove EasyOCR and related OCR dependencies

**Rationale**: 
- EasyOCR is only used for screenshot parsing in market comparison feature
- No other features depend on OCR functionality
- Removing EasyOCR reduces application size and complexity
- Eliminates GPU/CPU requirements for OCR processing

**Alternatives Considered**:
- Keep EasyOCR for potential future use: Rejected - violates "Simple and Direct" principle
- Replace with lighter OCR library: Rejected - no need for OCR without market comparison

**Dependencies to Remove**:
```
easyocr==1.7.2
Pillow==10.4.0  # Only needed for OCR image processing
```

### 2. Database Schema Impact

**Decision**: Remove market_rates table and related data

**Rationale**:
- Market rates table is only used for market comparison feature
- No foreign key relationships with core rental data
- Safe to remove without affecting core functionality
- Reduces database size and complexity

**Database Changes Required**:
- Drop `market_rates` table
- Remove market rate related methods from DataStore
- Clean up any existing market rate data

**Alternatives Considered**:
- Keep table for potential future use: Rejected - violates "Done Over Perfect" principle
- Archive data instead of deleting: Rejected - no business value in archived market data

### 3. Service Architecture Impact

**Decision**: Remove ScreenshotParserService entirely

**Rationale**:
- ScreenshotParserService is only used for market comparison
- No other services depend on it
- Removing it simplifies the service layer
- Reduces code complexity and maintenance burden

**Services to Remove**:
- `src/services/screenshot_parser.py` - Complete file deletion
- Market rate related methods from `src/storage/data_store.py`

**Alternatives Considered**:
- Keep service for potential future use: Rejected - violates "Simple and Direct" principle
- Refactor to generic image processing: Rejected - no other use cases identified

### 4. UI Component Analysis

**Decision**: Remove Market Comparison page and related UI components

**Rationale**:
- Market Comparison page is self-contained
- No shared UI components with other features
- Removing it simplifies navigation and user experience
- Reduces UI complexity

**UI Changes Required**:
- Remove "🏘️ Market Comparison" from sidebar navigation
- Remove market comparison page routing
- Remove screenshot upload components
- Update chart generation to remove market comparison overlays

**Alternatives Considered**:
- Hide page instead of removing: Rejected - violates "Simple and Direct" principle
- Keep UI for potential future use: Rejected - violates "Done Over Perfect" principle

### 5. Integration Points Analysis

**Decision**: Remove market comparison from negotiation summaries and charts

**Rationale**:
- Market comparison is optional enhancement, not core functionality
- Removing it simplifies negotiation summary generation
- Charts remain functional without market comparison overlays
- Core rental tracking functionality is preserved

**Integration Points to Update**:
- Negotiation summary generation (remove market comparison section)
- Chart generation (remove market rate overlays)
- Export functionality (remove market comparison data)

**Alternatives Considered**:
- Keep market comparison as optional feature: Rejected - violates "Simple and Direct" principle
- Replace with manual market data entry: Rejected - no user requirement for this

### 6. Testing Strategy

**Decision**: Remove market comparison tests and update integration tests

**Rationale**:
- Market comparison tests are no longer relevant
- Integration tests need updates to remove market comparison scenarios
- Core functionality tests remain unchanged
- Reduces test maintenance burden

**Test Changes Required**:
- Remove screenshot parser tests
- Remove market rate model tests
- Update integration tests to remove market comparison scenarios
- Add regression tests to ensure core functionality remains intact

**Alternatives Considered**:
- Keep tests for potential future use: Rejected - violates "Test What Matters" principle
- Archive tests instead of deleting: Rejected - no value in archived tests

## Risk Assessment

### Low Risk Changes
- **File Deletions**: Safe to delete isolated components
- **Dependency Removal**: EasyOCR has no other dependencies
- **UI Simplification**: Market comparison page is self-contained

### Medium Risk Changes
- **Database Schema Changes**: Requires careful migration to avoid data loss
- **Integration Updates**: Need to ensure no broken references remain

### Mitigation Strategies
- **Database Migration**: Create migration script to safely remove market_rates table
- **Integration Testing**: Comprehensive testing to ensure no broken references
- **Gradual Removal**: Remove UI first, then services, then models, then database

## Performance Impact

### Positive Impacts
- **Reduced Memory Usage**: No EasyOCR model loading
- **Faster Startup**: No OCR initialization
- **Simpler UI**: Fewer navigation options
- **Smaller Dependencies**: Reduced requirements.txt size

### Neutral Impacts
- **Core Functionality**: No performance impact on rental tracking
- **Database Operations**: No impact on core data operations
- **Chart Generation**: Minimal impact (just removing overlays)

## Conclusion

The removal of market comparison functionality is a straightforward simplification that aligns with constitutional principles. The feature is well-isolated with minimal integration points, making it safe to remove without affecting core rental tracking functionality. The removal will result in a simpler, more focused application that better serves the primary use case of personal rental payment tracking and negotiation support.

**Next Steps**:
1. Execute Phase 1 design to create detailed removal specifications
2. Generate tasks for systematic removal of components
3. Implement changes following constitutional principles
4. Validate that core functionality remains intact
