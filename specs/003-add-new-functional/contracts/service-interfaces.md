# Service Interfaces: Add New Functional Requirements

**Feature**: Add New Functional Requirements for Rental Fee Negotiation Support Tool  
**Date**: 2025-10-05  
**Branch**: 003-add-new-functional

## Service Extensions

### CalculationService (Extended)
**File**: `src/services/calculation_service.py`

**New Methods**:
```python
def get_legal_rule_for_date(self, date: datetime) -> str:
    """
    Determine applicable legal rule for given date.
    
    Args:
        date: Date to check legal rule for
        
    Returns:
        "25%_cap" for dates up to June 30, 2024
        "cpi_based" for dates after July 1, 2024
    """

def get_legal_rule_label(self, date: datetime) -> str:
    """
    Get human-readable label for legal rule.
    
    Args:
        date: Date to get label for
        
    Returns:
        "+25% (limit until July 2024)" or "+CPI (Yearly TÜFE)"
    """

def calculate_legal_max_increase(self, agreement: RentalAgreement, date: datetime) -> Decimal:
    """
    Calculate legal maximum rent increase for given date.
    
    Args:
        agreement: Rental agreement to calculate for
        date: Date to calculate for
        
    Returns:
        Legal maximum increase amount in TL
    """
```

### ChartGenerator (Extended)
**File**: `src/utils/chart_generator.py`

**New Methods**:
```python
def create_negotiation_mode_chart(self, data: Dict, mode: str) -> go.Figure:
    """
    Create chart with negotiation mode styling.
    
    Args:
        data: Chart data
        mode: "calm" or "assertive"
        
    Returns:
        Plotly Figure with appropriate styling
    """

def add_agreement_markers(self, fig: go.Figure, agreements: List[RentalAgreement]) -> go.Figure:
    """
    Add vertical markers for agreement periods.
    
    Args:
        fig: Existing Plotly Figure
        agreements: List of rental agreements
        
    Returns:
        Updated Figure with agreement markers
    """

def apply_negotiation_mode_styling(self, fig: go.Figure, mode: str) -> go.Figure:
    """
    Apply negotiation mode styling to chart.
    
    Args:
        fig: Plotly Figure to style
        mode: "calm" or "assertive"
        
    Returns:
        Styled Figure
    """
```

### ExportService (Extended)
**File**: `src/services/export_service.py`

**New Methods**:
```python
def add_data_source_disclosure(self, content: str) -> str:
    """
    Add data source disclosure to export content.
    
    Args:
        content: Export content to add disclosure to
        
    Returns:
        Content with data source disclosure appended
    """

def generate_negotiation_summary(self, agreement: RentalAgreement, mode: str) -> str:
    """
    Generate negotiation summary with neutral phrasing.
    
    Args:
        agreement: Rental agreement to summarize
        mode: Negotiation mode for styling
        
    Returns:
        Formatted negotiation summary
    """
```

### InflationService (Extended)
**File**: `src/services/inflation_service.py`

**New Methods**:
```python
def get_yearly_tufe(self, year: int) -> Optional[Decimal]:
    """
    Get yearly TÜFE rate for given year.
    
    Args:
        year: Year to get TÜFE for
        
    Returns:
        TÜFE rate as Decimal or None if not available
    """

def is_tufe_available(self, year: int) -> bool:
    """
    Check if TÜFE data is available for given year.
    
    Args:
        year: Year to check
        
    Returns:
        True if TÜFE data is available
    """

def fetch_tufe_from_tcmb(self, year: int) -> Optional[Decimal]:
    """
    Fetch TÜFE data from TCMB API.
    
    Args:
        year: Year to fetch TÜFE for
        
    Returns:
        TÜFE rate as Decimal or None if not available
    """
```

## New Services

### NegotiationSettingsService
**File**: `src/services/negotiation_settings_service.py`

**Methods**:
```python
def get_current_mode(self) -> str:
    """
    Get current negotiation mode.
    
    Returns:
        "calm" or "assertive"
    """

def set_mode(self, mode: str) -> None:
    """
    Set negotiation mode.
    
    Args:
        mode: "calm" or "assertive"
    """

def save_to_session_state(self, mode: str) -> None:
    """
    Save mode to Streamlit session state.
    
    Args:
        mode: Mode to save
    """

def load_from_session_state(self) -> str:
    """
    Load mode from Streamlit session state.
    
    Returns:
        Current mode or default "calm"
    """
```

### LegalRuleService
**File**: `src/services/legal_rule_service.py`

**Methods**:
```python
def get_applicable_rule(self, date: datetime) -> LegalRule:
    """
    Get applicable legal rule for given date.
    
    Args:
        date: Date to check
        
    Returns:
        Applicable LegalRule object
    """

def get_all_rules(self) -> List[LegalRule]:
    """
    Get all legal rules from database.
    
    Returns:
        List of all LegalRule objects
    """

def initialize_default_rules(self) -> None:
    """
    Initialize default legal rules in database.
    """
```

## API Contracts

### Streamlit UI Components

#### Negotiation Mode Selector
```python
def render_negotiation_mode_selector() -> str:
    """
    Render negotiation mode selector in Streamlit UI.
    
    Returns:
        Selected mode ("calm" or "assertive")
    """
```

#### Legal Rule Display
```python
def render_legal_rule_info(agreement: RentalAgreement, date: datetime) -> None:
    """
    Render legal rule information in UI.
    
    Args:
        agreement: Rental agreement
        date: Date to show rule for
    """
```

#### Agreement Period Annotations
```python
def render_agreement_annotations(agreements: List[RentalAgreement]) -> None:
    """
    Render agreement period annotations on charts.
    
    Args:
        agreements: List of rental agreements
    """
```

## Error Handling

### New Exceptions
```python
class NegotiationModeError(ServiceError):
    """Raised when invalid negotiation mode is provided."""

class LegalRuleError(ServiceError):
    """Raised when legal rule cannot be determined."""

class TufeDataError(ServiceError):
    """Raised when TÜFE data is unavailable or invalid."""
```

### Error Scenarios
1. **Invalid negotiation mode**: Return default "calm" mode
2. **Missing TÜFE data**: Display "TÜFE data pending" and allow manual entry
3. **Invalid date for legal rule**: Return most recent applicable rule
4. **Chart generation failure**: Fall back to basic chart without styling

## Performance Requirements

### Response Times
- Legal rule determination: < 100ms
- Negotiation mode changes: < 50ms
- Chart styling updates: < 200ms
- TÜFE data lookup: < 500ms

### Caching
- Legal rules: Cache in memory for session
- Negotiation mode: Store in Streamlit session state
- TÜFE data: Cache for 24 hours

## Integration Points

### Existing Services
- **DataStore**: Extended to support new entities
- **ExchangeRateService**: No changes required
- **CalculationService**: Extended with legal rule logic

### External APIs
- **TCMB API**: Extended to fetch TÜFE data
- **Streamlit**: Used for session state management

### Database
- **SQLite**: Extended with new tables for settings and legal rules
- **Migrations**: Required for new table creation
