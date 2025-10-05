# Research: Rental Fee Negotiation Support Tool

## Technology Decisions

### Web Framework: Streamlit
**Decision**: Use Streamlit 1.50.0 as the web framework
**Rationale**: 
- Simple, Python-native web framework
- Built-in file upload, charting, and export capabilities
- Free hosting options available (Streamlit Cloud)
- Non-developer friendly interface
- Fast development cycle

**Alternatives considered**: 
- Flask/FastAPI: More complex setup, requires more frontend work
- Django: Overkill for this simple application
- Desktop app: Less shareable, harder to deploy

### Charting Library: Plotly
**Decision**: Use Plotly 6.3.1 for visualizations
**Rationale**:
- Interactive charts with export capabilities (PNG, PDF)
- Good integration with Streamlit
- Professional-looking charts suitable for negotiations
- Built-in export functionality

**Alternatives considered**:
- Matplotlib: Less interactive, harder to export
- Chart.js: Requires JavaScript knowledge
- Seaborn: More for data analysis than presentation

### OCR Engine: EasyOCR
**Decision**: Use EasyOCR 1.7.2 for screenshot parsing
**Rationale**:
- Better accuracy than Tesseract for stylized text
- Handles map markers and various text orientations
- Good performance on rental listing screenshots
- Python-native implementation

**Alternatives considered**:
- Tesseract: Lower accuracy on stylized text
- Google Vision API: Requires API key, not free
- Azure Computer Vision: Paid service

### Data Storage: SQLite
**Decision**: Use SQLite for local data persistence
**Rationale**:
- Zero infrastructure cost
- Simple setup and deployment
- Sufficient for personal use case (3-4 agreements)
- Built into Python standard library

**Alternatives considered**:
- PostgreSQL: Overkill, requires hosting
- JSON files: Less structured, harder to query
- Cloud databases: Additional cost and complexity

### Exchange Rate Source: TCMB
**Decision**: Use TCMB (Central Bank of Turkey) exclusively
**Rationale**:
- Most authoritative source for Turkish financial data
- Legally defensible in negotiations
- Free API access
- Historical data available

**Alternatives considered**:
- ExchangeRate-API: Less authoritative
- Fixer.io: Paid service
- Multiple sources: Creates inconsistencies

## Integration Patterns

### TCMB API Integration
**Pattern**: Direct HTTP requests with error handling
**Implementation**: Use requests library with retry logic
**Error handling**: Manual entry fallback if API unavailable

### Screenshot Processing Pipeline
**Pattern**: Upload → OCR → Parse → Validate → Store
**Implementation**: Streamlit file uploader → EasyOCR → Regex parsing → Validation
**Error handling**: User feedback for parsing failures

### Chart Generation
**Pattern**: Data → Plotly → Export
**Implementation**: Pandas data processing → Plotly charts → Export to PNG/PDF
**Export options**: PNG for WhatsApp, PDF for formal documents

## Performance Considerations

### Screenshot Processing
**Target**: <5 seconds for typical sahibinden.com screenshots
**Optimization**: Use EasyOCR with appropriate language settings
**Fallback**: Manual entry if OCR fails

### Chart Rendering
**Target**: <1 second for chart generation
**Optimization**: Pre-process data, use Plotly's efficient rendering
**Caching**: Cache exchange rate data locally

### Page Load
**Target**: <2 seconds initial load
**Optimization**: Lazy load charts, efficient data queries
**Database**: Index on date fields for fast queries

## Legal and Compliance

### Data Sources
- TCMB: Official central bank data (most authoritative)
- TÜFE: Official inflation data from TCMB
- Market data: User-provided screenshots (no liability for accuracy)

### Data Attribution
- All exports must include source attribution
- Clear labeling of data sources for transparency
- Legal disclaimer for market data accuracy

## Security Considerations

### Data Privacy
- All data stored locally (SQLite)
- No external data transmission except TCMB API
- No user authentication required (personal use)

### API Security
- TCMB API: Public endpoint, no authentication required
- Rate limiting: Respectful API usage
- Error handling: Graceful degradation

## Deployment Strategy

### Hosting: Streamlit Cloud
**Decision**: Use Streamlit Cloud for free hosting
**Rationale**:
- Free tier available
- Simple deployment from GitHub
- Automatic updates
- No server management required

**Alternatives considered**:
- Heroku: Paid service
- AWS/GCP: Overkill, requires setup
- Local deployment: Not shareable

### Data Persistence
**Strategy**: SQLite file in Streamlit Cloud storage
**Limitations**: Data may be lost on redeployment
**Mitigation**: Export functionality for data backup

## Testing Strategy

### Unit Tests
- Model validation
- Service layer logic
- Calculation accuracy
- Data parsing

### Integration Tests
- TCMB API integration
- Screenshot parsing pipeline
- Chart generation
- Export functionality

### Manual Testing
- End-to-end user workflows
- Different screenshot formats
- Edge cases (missing data, API failures)
- Cross-browser compatibility

## Future Considerations

### Scalability
- Current design supports personal use
- Could be extended for multiple users with authentication
- Database could be migrated to PostgreSQL if needed

### Feature Extensions
- Multiple currency support
- Advanced market analysis
- Historical trend analysis
- Automated market data collection

### Maintenance
- Regular dependency updates
- TCMB API changes monitoring
- OCR accuracy improvements
- User feedback incorporation