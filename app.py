"""
Kira Prolongation Support - Streamlit Application
Main entry point for the rental fee negotiation support tool.

Features:
- Historical TL/USD payment tracking
- Market rate comparison and analysis
- Future payment projections
- TCMB exchange rate integration
- TÜFE (Turkish CPI) data management with secure TCMB API integration
- Legal rent increase calculations (25% cap until June 2024, TÜFE after July 2024)
- Negotiation mode settings (Calm/Assertive)
- Data source attribution and export functionality
- Secure API key management for TCMB EVDS API
- TÜFE data caching with 24-hour expiration
"""
import streamlit as st
from decimal import Decimal
from datetime import date, datetime
from PIL import Image
import io

# Import services and models
from src.storage import DataStore
from src.services import (
    ExchangeRateService,
    InflationService,
    CalculationService,
    ExportService,
    NegotiationSettingsService,
    LegalRuleService,
    TufeDataSourceService,
    TufeApiKeyService,
    TufeCacheService,
    TCMBApiClient,
    TufeConfigService
)
from src.services.oecd_api_client import OECDApiClient
from src.services.rate_limit_handler import RateLimitHandler
from src.services.data_validator import DataValidator
from src.models import RentalAgreement
from src.utils import ChartGenerator

# Page configuration
st.set_page_config(
    page_title="Kira Prolongation Support",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services (cached)
@st.cache_resource
def init_services():
    """
    Initialize all services with DataStore.
    
    Returns:
        dict: Dictionary containing all initialized services including:
            - Core services: data_store, exchange_rate_service, inflation_service, 
              calculation_service, export_service, chart_generator
            - Negotiation services: negotiation_settings_service, legal_rule_service
            - TÜFE data source services: tufe_data_source_service, tufe_api_key_service,
              tufe_cache_service, tufe_config_service, tcmb_api_client
    """
    data_store = DataStore()
    return {
        # Core services
        'data_store': data_store,
        'exchange_rate_service': ExchangeRateService(data_store),
        'inflation_service': InflationService(data_store),
        'calculation_service': CalculationService(),
        'export_service': ExportService(),
        'chart_generator': ChartGenerator(),
        
        # Negotiation services
        'negotiation_settings_service': NegotiationSettingsService(),
        'legal_rule_service': LegalRuleService(data_store),
        
        # TÜFE data source services for secure TCMB API integration
        'tufe_data_source_service': TufeDataSourceService(data_store),  # Manages TÜFE data sources
        'tufe_api_key_service': TufeApiKeyService(data_store),          # Manages API keys securely
        'tufe_cache_service': TufeCacheService(data_store),             # Manages TÜFE data caching
        'tufe_config_service': TufeConfigService(),                     # Manages TÜFE configuration
        'tcmb_api_client': None,  # Will be initialized with actual API key when needed
        
        # OECD API services for easy TÜFE data fetching
        'oecd_api_client': OECDApiClient(),                             # OECD SDMX API client
        'rate_limit_handler': RateLimitHandler(),                       # Rate limiting handler
        'data_validator': DataValidator()                               # Data validation service
    }

services = init_services()

# Sidebar navigation
st.sidebar.title("🏠 Kira Support")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "📋 Rental Agreements",
        "💱 Exchange Rates",
        "💰 Payment Records",
        "📈 Visualizations",
        "🤝 Negotiation Summary",
        "📊 Inflation Data"
    ]
)

st.sidebar.markdown("---")

# Negotiation Mode Selector
# NEW FEATURE: User-selectable negotiation mode (Calm/Assertive)
# - Calm mode: Hides growth arrows, tones down visuals
# - Assertive mode: Highlights changes, bold numbers
st.sidebar.subheader("🎯 Negotiation Mode")
current_mode = services['negotiation_settings_service'].get_current_mode()
new_mode = st.sidebar.radio(
    "Select mode:",
    ["calm", "assertive"],
    index=0 if current_mode == "calm" else 1,
    format_func=lambda x: "😌 Calm" if x == "calm" else "💪 Assertive"
)

if new_mode != current_mode:
    services['negotiation_settings_service'].set_mode(new_mode)
    st.sidebar.success(f"Mode changed to: {'😌 Calm' if new_mode == 'calm' else '💪 Assertive'}")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Start by adding your rental agreements, then fetch exchange rates.")

# Main content based on selected page
if page == "📋 Rental Agreements":
    st.title("📋 Rental Agreements")
    st.markdown("Manage your rental agreement history.")
    
    # Display existing agreements
    agreements = services['data_store'].get_rental_agreements()
    
    if agreements:
        st.subheader("📖 Your Agreements")
        for agreement in agreements:
            with st.expander(f"Agreement: {agreement.start_date} - {agreement.end_date or 'Ongoing'}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Base Rent", f"{agreement.base_amount_tl:,.0f} TL")
                with col2:
                    st.metric("Start Date", agreement.start_date.strftime("%b %Y"))
                with col3:
                    if agreement.end_date:
                        st.metric("End Date", agreement.end_date.strftime("%b %Y"))
                    else:
                        st.metric("Status", "Ongoing")
                
                if agreement.has_conditional_pricing():
                    st.info(f"📝 Conditional Pricing: {len(agreement.conditional_rules.get('rules', []))} rules")
                
                if agreement.notes:
                    st.caption(f"Notes: {agreement.notes}")
    else:
        st.info("No rental agreements yet. Add one below!")
    
    # Add new agreement
    st.subheader("➕ Add New Agreement")
    
    with st.form("new_agreement"):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", value=date(2022, 11, 1))
            base_amount = st.number_input("Base Monthly Rent (TL)", min_value=0, value=15000, step=1000)
        
        with col2:
            end_date = st.date_input("End Date (leave empty for ongoing)", value=None)
            notes = st.text_area("Notes", placeholder="Optional notes about this agreement")
        
        # Conditional pricing
        st.markdown("**Conditional Pricing (Optional)**")
        has_conditional = st.checkbox("This agreement has conditional pricing rules")
        
        conditional_rules = None
        if has_conditional:
            st.caption("Example: If exchange rate < 40 TL/USD, rent is 35,000 TL; otherwise 40,000 TL")
            rule_count = st.number_input("Number of rules", min_value=1, max_value=5, value=2)
            
            rules = []
            for i in range(rule_count):
                st.markdown(f"**Rule {i+1}**")
                col_cond, col_amt = st.columns(2)
                with col_cond:
                    condition = st.text_input(f"Condition", value="< 40" if i == 0 else ">= 40", key=f"cond_{i}")
                with col_amt:
                    amount = st.number_input(f"Amount (TL)", min_value=0, value=35000 if i == 0 else 40000, key=f"amt_{i}")
                
                rules.append({"condition": condition, "amount_tl": int(amount)})
            
            conditional_rules = {"rules": rules}
        
        submitted = st.form_submit_button("💾 Save Agreement")
        
        if submitted:
            try:
                agreement = RentalAgreement(
                    start_date=start_date,
                    end_date=end_date if end_date else None,
                    base_amount_tl=Decimal(str(base_amount)),
                    conditional_rules=conditional_rules,
                    notes=notes if notes else None
                )
                
                agreement_id = services['data_store'].save_rental_agreement(agreement)
                st.success(f"✅ Agreement saved! ID: {agreement_id}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving agreement: {e}")

elif page == "💱 Exchange Rates":
    st.title("💱 Exchange Rates")
    st.markdown("Fetch and view USD/TRY exchange rates.")
    
    # Fetch rates
    st.subheader("🔄 Fetch Exchange Rates")
    
    col1, col2 = st.columns(2)
    with col1:
        start_month = st.selectbox("Start Month", range(1, 13), index=10, format_func=lambda x: date(2000, x, 1).strftime("%B"))
        start_year = st.number_input("Start Year", min_value=2020, max_value=2030, value=2022)
    
    with col2:
        end_month = st.selectbox("End Month", range(1, 13), index=9, format_func=lambda x: date(2000, x, 1).strftime("%B"))
        end_year = st.number_input("End Year", min_value=2020, max_value=2030, value=datetime.now().year)
    
    if st.button("🌐 Fetch Exchange Rates"):
        with st.spinner("Fetching exchange rates..."):
            try:
                rates = services['exchange_rate_service'].fetch_rate_range(
                    start_month, start_year, end_month, end_year
                )
                st.success(f"✅ Fetched {len(rates)} exchange rates!")
                
                # Display rates
                if rates:
                    st.subheader("📊 Fetched Rates")
                    for rate in rates:
                        st.write(f"**{rate.year}-{rate.month:02d}**: {rate.rate_tl_per_usd:.4f} TL/USD ({rate.source})")
            except Exception as e:
                st.error(f"❌ Error fetching rates: {e}")
    
    # Manual entry
    st.markdown("---")
    st.subheader("✍️ Manual Entry")
    
    with st.form("manual_rate"):
        col1, col2, col3 = st.columns(3)
        with col1:
            manual_month = st.selectbox("Month", range(1, 13), format_func=lambda x: date(2000, x, 1).strftime("%B"), key="manual_month")
        with col2:
            manual_year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year, key="manual_year")
        with col3:
            manual_rate = st.number_input("Rate (TL per 1 USD)", min_value=0.0, value=30.0, step=0.1)
        
        if st.form_submit_button("💾 Save Rate"):
            try:
                from src.models import ExchangeRate
                rate = ExchangeRate(
                    month=manual_month,
                    year=manual_year,
                    rate_tl_per_usd=Decimal(str(manual_rate)),
                    source="Manual Entry"
                )
                services['data_store'].save_exchange_rate(rate)
                st.success("✅ Exchange rate saved!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

elif page == "💰 Payment Records":
    st.title("💰 Payment Records")
    st.markdown("View calculated payment records combining agreements and exchange rates.")
    
    # Get agreements
    agreements = services['data_store'].get_rental_agreements()
    
    if not agreements:
        st.warning("⚠️ No rental agreements found. Add one in the Rental Agreements page first.")
    else:
        # Select agreement
        selected_agreement = st.selectbox(
            "Select Agreement",
            agreements,
            format_func=lambda a: f"{a.start_date} - {a.end_date or 'Ongoing'} ({a.base_amount_tl:,.0f} TL)"
        )
        
        if st.button("🔄 Calculate Payment Records"):
            with st.spinner("Calculating payments..."):
                try:
                    # Generate payment records for this agreement
                    start_date = selected_agreement.start_date
                    end_date = selected_agreement.end_date or date.today()
                    
                    current_date = start_date
                    payments_generated = 0
                    
                    while current_date <= end_date:
                        # Get exchange rate for this month
                        rate = services['exchange_rate_service'].fetch_rate(current_date.month, current_date.year)
                        
                        # Calculate amount (considering conditional rules)
                        amount_tl = services['calculation_service'].apply_conditional_rules(
                            selected_agreement,
                            rate.rate_tl_per_usd
                        )
                        
                        # Calculate USD equivalent
                        amount_usd = services['calculation_service'].calculate_usd_equivalent(
                            amount_tl,
                            rate.rate_tl_per_usd
                        )
                        
                        # Save payment record
                        from src.models import PaymentRecord
                        payment = PaymentRecord(
                            agreement_id=selected_agreement.id,
                            month=current_date.month,
                            year=current_date.year,
                            amount_tl=amount_tl,
                            amount_usd=amount_usd,
                            exchange_rate_id=rate.id
                        )
                        services['data_store'].save_payment_record(payment)
                        payments_generated += 1
                        
                        # Move to next month
                        if current_date.month == 12:
                            current_date = date(current_date.year + 1, 1, 1)
                        else:
                            current_date = date(current_date.year, current_date.month + 1, 1)
                    
                    st.success(f"✅ Generated/updated {payments_generated} payment records!")
                    
                except Exception as e:
                    st.error(f"❌ Error calculating payments: {e}")
                    st.exception(e)
        
        # Display existing payment records
        st.subheader("📋 Payment History")
        payments = services['data_store'].get_payment_records(agreement_id=selected_agreement.id)
        
        if payments:
            # Create table
            data = []
            for p in payments:
                data.append({
                    "Period": f"{p.year}-{p.month:02d}",
                    "TL Amount": f"{p.amount_tl:,.2f}",
                    "USD Amount": f"${p.amount_usd:,.2f}"
                })
            
            st.dataframe(data, use_container_width=True)
            
            # Summary statistics
            summary = services['calculation_service'].calculate_payment_summary(payments)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Payments", summary['count'])
            with col2:
                st.metric("Avg TL", f"{summary['avg_tl']:,.2f} TL")
            with col3:
                st.metric("Avg USD", f"${summary['avg_usd']:,.2f}")
        else:
            st.info("No payment records yet. Click 'Calculate Payment Records' to generate them.")

elif page == "📈 Visualizations":
    st.title("📈 Visualizations")
    st.markdown("Interactive charts showing your rental payment trends.")
    
    # Get payment records
    payments = services['data_store'].get_payment_records()
    
    if not payments:
        st.warning("⚠️ No payment data available. Generate payment records first.")
    else:
        # TL vs USD chart
        st.subheader("💱 TL vs USD Equivalent Over Time")
        fig1 = services['chart_generator'].create_tl_vs_usd_chart(payments)
        
        # Add agreement period annotations
        # NEW FEATURE: Agreement Period Annotations
        # - Adds vertical markers labeled "New Agreement (YYYY)" to show contract boundaries
        agreements = services['data_store'].get_rental_agreements()
        if agreements:
            fig1 = services['chart_generator'].add_agreement_markers(fig1, agreements)
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Payment comparison
        st.subheader("📊 Payment Comparison")
        fig2 = services['chart_generator'].create_payment_comparison_bar_chart(payments)
        st.plotly_chart(fig2, use_container_width=True)
        

elif page == "🤝 Negotiation Summary":
    st.title("🤝 Negotiation Summary")
    st.markdown("Key statistics and data points to support your rent negotiation.")
    
    # Get latest data
    payments = services['data_store'].get_payment_records()
    agreements = services['data_store'].get_rental_agreements()
    
    if not payments or not agreements:
        st.warning("⚠️ Need payment records and agreements to generate summary.")
    else:
        # Latest payment
        latest_payment = sorted(payments, key=lambda p: (p.year, p.month))[-1]
        first_payment = sorted(payments, key=lambda p: (p.year, p.month))[0]
        
        # Calculate changes
        tl_increase_pct = services['calculation_service'].calculate_percentage_increase(
            first_payment.amount_tl,
            latest_payment.amount_tl
        )
        
        usd_change_pct = services['calculation_service'].calculate_percentage_increase(
            first_payment.amount_usd,
            latest_payment.amount_usd
        )
        
        # Display metrics
        st.subheader("📊 Key Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "TL Increase",
                f"{tl_increase_pct:,.1f}%",
                delta=f"{latest_payment.amount_tl - first_payment.amount_tl:,.0f} TL"
            )
        
        with col2:
            st.metric(
                "USD Change",
                f"{usd_change_pct:,.1f}%",
                delta=f"${latest_payment.amount_usd - first_payment.amount_usd:,.2f}"
            )
        
        with col3:
            st.metric(
                "Current Rent (TL)",
                f"{latest_payment.amount_tl:,.0f} TL"
            )
        
        with col4:
            st.metric(
                "Current Rent (USD)",
                f"${latest_payment.amount_usd:,.2f}"
            )
        
        # Legal Rule Display
        # NEW FEATURE: Legal CPI/Cap Context
        # - Automatically determines legal rule based on date
        # - Shows +25% cap for periods up to June 30, 2024
        # - Shows +CPI (Yearly TÜFE) for periods after July 1, 2024
        st.subheader("⚖️ Legal Context")
        
        # Get current date for legal rule determination
        current_date = datetime.now()
        
        # Get legal rule for current date
        legal_rule_type = services['calculation_service'].get_legal_rule_for_date(current_date)
        legal_rule_label = services['calculation_service'].get_legal_rule_label(current_date)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Legal Max Increase**: {legal_rule_label}")
        
        with col2:
            # Calculate legal max increase for latest agreement
            if agreements:
                latest_agreement = agreements[-1]
                legal_max_increase = services['calculation_service'].calculate_legal_max_increase(
                    latest_agreement, current_date
                )
                st.info(f"**Max Increase Amount**: {legal_max_increase:,.2f} TL")
        
        # Export section
        st.markdown("---")
        st.subheader("💾 Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📸 Export Charts as PNG"):
                with st.spinner("Generating image..."):
                    try:
                        # Generate charts
                        fig1 = services['chart_generator'].create_tl_vs_usd_chart(payments)
                        
                        # Export
                        img_bytes = services['export_service'].create_whatsapp_optimized_image([fig1])
                        
                        st.download_button(
                            label="⬇️ Download PNG",
                            data=img_bytes,
                            file_name=f"rent_analysis_{datetime.now().strftime('%Y%m%d')}.png",
                            mime="image/png"
                        )
                        
                        st.success("✅ Image ready for download!")
                    except Exception as e:
                        st.error(f"❌ Export error: {e}")
        
        with col2:
            st.info("💡 **Tip**: Share the exported image via WhatsApp with your landlord!")
        
        # Data Source Disclosure
        # NEW FEATURE: Data Source Disclosure
        # - Every exported summary includes "Data source: TCMB (exchange rates), TÜFE (inflation)"
        # - Uses neutral negotiation phrasing ("Aligned with market average")
        st.markdown("---")
        st.subheader("📋 Data Source Disclosure")
        
        # Generate negotiation summary with data source disclosure
        if agreements:
            latest_agreement = agreements[-1]
            current_mode = services['negotiation_settings_service'].get_current_mode()
            summary = services['export_service'].generate_negotiation_summary(latest_agreement, current_mode)
            
            st.text_area(
                "Negotiation Summary (with data source disclosure):",
                value=summary,
                height=200,
                disabled=True
            )

elif page == "📊 Inflation Data":
    st.title("📊 Turkish Inflation Data")
    st.markdown("Manage official inflation rates for legal maximum rent calculations.")
    
    # CSV Import
    st.subheader("📥 Import from CSV")
    
    uploaded_csv = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="CSV format: month,year,inflation_rate_percent,source"
    )
    
    if uploaded_csv:
        if st.button("📤 Import CSV"):
            with st.spinner("Importing inflation data..."):
                try:
                    csv_content = uploaded_csv.getvalue().decode('utf-8')
                    count = services['inflation_service'].import_from_csv(csv_content)
                    st.success(f"✅ Imported {count} inflation data points!")
                except Exception as e:
                    st.error(f"❌ Import error: {e}")
    
    # Manual entry
    st.markdown("---")
    st.subheader("✍️ Manual Entry")
    
    with st.form("manual_inflation"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            inf_month = st.selectbox(
                "Month",
                range(1, 13),
                format_func=lambda x: date(2000, x, 1).strftime("%B")
            )
        with col2:
            inf_year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year)
        with col3:
            inf_rate = st.number_input("Inflation Rate (%)", min_value=0.0, value=50.0, step=0.1)
        
        if st.form_submit_button("💾 Save Inflation Data"):
            try:
                services['inflation_service'].save_manual_entry(
                    month=inf_month,
                    year=inf_year,
                    inflation_rate_percent=Decimal(str(inf_rate)),
                    source="Manual Entry"
                )
                st.success("✅ Inflation data saved!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # TCMB API Key Configuration
    st.markdown("---")
    st.subheader("🔑 TCMB API Configuration")
    
    # Documentation for TCMB API integration
    with st.expander("ℹ️ About TCMB API Integration"):
        st.markdown("""
        **TCMB EVDS API Integration**
        
        This section provides secure integration with the Turkish Central Bank (TCMB) 
        Electronic Data Delivery System (EVDS) API for fetching official TÜFE (Turkish CPI) data.
        
        **Features:**
        - 🔐 **Secure API Key Management**: API keys are encrypted and stored securely
        - 📊 **Official TÜFE Data**: Direct access to official Turkish inflation rates
        - ⚡ **Smart Caching**: 24-hour cache to minimize API calls and improve performance
        - 🔄 **Automatic Fallback**: Falls back to manual entry if API is unavailable
        - 📈 **Data Source Attribution**: All exports include proper data source attribution
        
        **How to get a TCMB API Key:**
        1. Visit [TCMB EVDS](https://evds2.tcmb.gov.tr/)
        2. Register for an account
        3. Generate an API key from your dashboard
        4. Enter the key below to start fetching official TÜFE data
        
        **Note**: If you get a "Connection error" when validating, this is common with TCMB API due to firewall restrictions. You can still save your API key and test it when fetching data.
        """)
    
    # Check if API key is configured
    is_api_configured = services['tufe_config_service'].is_api_key_configured()
    api_key_valid = False
    
    if is_api_configured:
        api_key_valid = services['tufe_config_service'].validate_api_key()
        if api_key_valid:
            st.success("✅ TCMB API key is configured and valid")
        else:
            st.warning("⚠️ TCMB API key is configured but not valid")
    else:
        st.warning("⚠️ TCMB API key is not configured")
    
    # Debug section
    if st.button("🔍 Debug API Key Status"):
        st.write("**Current API Key Status:**")
        st.write(f"- Configured: {is_api_configured}")
        if is_api_configured:
            api_key = services['tufe_config_service'].get_tcmb_api_key()
            if api_key:
                st.write(f"- API Key Length: {len(api_key)}")
                st.write(f"- API Key Preview: {api_key[:20]}...")
            else:
                st.write("- API Key: None")
        
        # Check session state
        if 'tcmb_api_key' in st.session_state:
            st.write(f"- Session State Key Length: {len(st.session_state['tcmb_api_key'])}")
            st.write(f"- Session State Key Preview: {st.session_state['tcmb_api_key'][:20]}...")
        else:
            st.write("- Session State: No API key stored")
    
    # Test API key setting
    if st.button("🧪 Test: Set Sample API Key"):
        test_key = "test_tcmb_api_key_12345678901234567890123456789012"
        services['tufe_config_service'].set_tcmb_api_key(test_key)
        st.session_state['tcmb_api_key'] = test_key
        st.success("✅ Test API key set!")
        st.rerun()
    
    # API Key Configuration Form
    with st.expander("⚙️ Configure TCMB API Key", expanded=not is_api_configured):
        st.info("Get your TCMB EVDS API key from: https://evds2.tcmb.gov.tr/index.php?/evds/login")
        
        with st.form("tcmb_api_config"):
            api_key = st.text_input(
                "TCMB EVDS API Key",
                type="password",
                help="Enter your TCMB EVDS API key for secure TÜFE data fetching",
                placeholder="Enter your API key here..."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🔑 Validate API Key"):
                    if api_key:
                        try:
                            # Test the API key with detailed feedback
                            test_client = TCMBApiClient(api_key)
                            validation_result = test_client.validate_api_key_detailed()
                            
                            if validation_result["valid"]:
                                # Save the API key
                                services['tufe_config_service'].set_tcmb_api_key(api_key)
                                st.success(f"✅ {validation_result['message']}")
                                st.rerun()
                            else:
                                # Show detailed error message
                                st.error(f"❌ {validation_result['message']}")
                                
                                # Provide additional help based on error type
                                if validation_result["error"] == "unauthorized":
                                    st.info("💡 **Help**: Make sure you copied the API key correctly from your TCMB EVDS dashboard.")
                                elif validation_result["error"] == "forbidden":
                                    st.info("💡 **Help**: Your API key might be valid but your account may not have permission to access TÜFE data.")
                                elif validation_result["error"] == "connection_error":
                                    st.info("💡 **Help**: Check your internet connection and try again.")
                                elif validation_result["error"] == "timeout":
                                    st.info("💡 **Help**: The TCMB API is taking too long to respond. Try again in a few minutes.")
                                    
                        except Exception as e:
                            st.error(f"❌ Error validating API key: {e}")
                    else:
                        st.error("❌ Please enter an API key")
            
            with col2:
                if st.form_submit_button("💾 Save API Key (Skip Validation)"):
                    if api_key:
                        try:
                            # Save to configuration service
                            services['tufe_config_service'].set_tcmb_api_key(api_key)
                            
                            # Also save to session state as backup
                            st.session_state['tcmb_api_key'] = api_key
                            
                            st.success("✅ API key saved successfully!")
                            st.info("ℹ️ **Note**: API key saved without validation. You can test it later when fetching TÜFE data.")
                            
                            # Debug info
                            st.write(f"🔍 **Debug**: API key length: {len(api_key)}")
                            st.write(f"🔍 **Debug**: API key starts with: {api_key[:10]}...")
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error saving API key: {e}")
                            import traceback
                            st.error(f"Full error: {traceback.format_exc()}")
                    else:
                        st.error("❌ Please enter an API key")
    
    # OECD API Integration
    st.markdown("---")
    st.subheader("🌍 OECD API Integration")
    
    # Documentation for OECD API integration
    with st.expander("ℹ️ About OECD API Integration"):
        st.markdown("""
        **OECD SDMX API Integration**
        
        This section provides easy access to Turkish inflation (TÜFE) data from the 
        Organisation for Economic Co-operation and Development (OECD) API.
        
        **Features:**
        - 🚀 **One-Click Fetching**: Get TÜFE data with a single button click
        - 📊 **Official Data**: Access to official OECD Turkish CPI data
        - ⚡ **Smart Caching**: Automatic caching with TTL for optimal performance
        - 🔄 **Rate Limiting**: Respects OECD API rate limits automatically
        - 🛡️ **Error Handling**: Graceful fallback to manual entry if needed
        - 📈 **Data Validation**: Ensures data quality before storage
        
        **Data Source**: OECD SDMX API - Turkish Consumer Price Index (CPI)
        **Update Frequency**: Monthly data available
        **Coverage**: Historical data from 2000 to present
        
        **Note**: This is a free, public API that doesn't require authentication.
        """)
    
    # OECD API Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**OECD API Status**")
        try:
            is_healthy = services['oecd_api_client'].is_healthy()
            if is_healthy:
                st.success("✅ OECD API is healthy and accessible")
            else:
                st.warning("⚠️ OECD API is not accessible")
        except Exception as e:
            st.error(f"❌ Error checking OECD API status: {e}")
    
    with col2:
        st.write("**Rate Limit Status**")
        try:
            rate_limit_status = services['rate_limit_handler'].get_rate_limit_status()
            can_make_request = rate_limit_status.get('can_make_request', True)
            if can_make_request:
                st.success("✅ Rate limit OK - requests allowed")
            else:
                st.warning("⚠️ Rate limited - please wait")
        except Exception as e:
            st.error(f"❌ Error checking rate limit: {e}")
    
    # OECD API Actions
    st.markdown("---")
    st.subheader("🎯 OECD API Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Fetch TÜFE Data**")
        current_year = datetime.now().year
        
        if st.button("🚀 Fetch TÜFE from OECD API", key="oecd_fetch_current"):
            with st.spinner("Fetching TÜFE data from OECD API..."):
                try:
                    # Fetch data for current year
                    inflation_data = services['inflation_service'].fetch_and_cache_oecd_tufe_data(
                        current_year, current_year
                    )
                    
                    if inflation_data:
                        st.success(f"✅ Successfully fetched {len(inflation_data)} TÜFE data points for {current_year}")
                        
                        # Show the data
                        for item in inflation_data:
                            st.write(f"📊 {item.year}-{item.month:02d}: {item.tufe_rate}%")
                    else:
                        st.warning("⚠️ No TÜFE data found for the current year")
                        
                except Exception as e:
                    st.error(f"❌ Error fetching from OECD API: {e}")
                    st.info("💡 You can still enter TÜFE data manually below")
    
    with col2:
        st.write("**Fetch Historical Data**")
        
        # Year range selector
        start_year = st.number_input(
            "Start Year", 
            min_value=2000, 
            max_value=current_year, 
            value=current_year-1,
            key="oecd_start_year"
        )
        end_year = st.number_input(
            "End Year", 
            min_value=start_year, 
            max_value=current_year, 
            value=current_year,
            key="oecd_end_year"
        )
        
        if st.button("📈 Fetch Historical TÜFE", key="oecd_fetch_historical"):
            with st.spinner(f"Fetching TÜFE data for {start_year}-{end_year}..."):
                try:
                    inflation_data = services['inflation_service'].fetch_and_cache_oecd_tufe_data(
                        start_year, end_year
                    )
                    
                    if inflation_data:
                        st.success(f"✅ Successfully fetched {len(inflation_data)} TÜFE data points")
                        
                        # Show summary
                        years_covered = set(item.year for item in inflation_data)
                        st.write(f"📊 Years covered: {sorted(years_covered)}")
                    else:
                        st.warning("⚠️ No TÜFE data found for the selected period")
                        
                except Exception as e:
                    st.error(f"❌ Error fetching historical data: {e}")
    
    with col3:
        st.write("**Cache Management**")
        
        if st.button("🗄️ View Cache Statistics", key="oecd_cache_stats"):
            try:
                cache_stats = services['tufe_cache_service'].get_cache_statistics()
                
                st.write("**Cache Statistics:**")
                st.write(f"📊 Total entries: {cache_stats['total_entries']}")
                st.write(f"✅ Active entries: {cache_stats['active_entries']}")
                st.write(f"⏰ Expired entries: {cache_stats['expired_entries']}")
                st.write(f"🎯 Total hits: {cache_stats['total_hits']}")
                st.write(f"📈 Hit rate: {cache_stats['hit_rate']:.2%}")
                st.write(f"⚡ Avg fetch duration: {cache_stats['avg_fetch_duration']:.2f}s")
                st.write(f"🔧 Cache efficiency: {cache_stats['cache_efficiency']:.2f}")
                
            except Exception as e:
                st.error(f"❌ Error getting cache statistics: {e}")
        
        if st.button("🧹 Cleanup Expired Cache", key="oecd_cleanup"):
            with st.spinner("Cleaning up expired cache entries..."):
                try:
                    cleaned_count = services['tufe_cache_service'].cleanup_expired_cache()
                    st.success(f"✅ Cleaned up {cleaned_count} expired cache entries")
                except Exception as e:
                    st.error(f"❌ Error cleaning cache: {e}")
    
    # TÜFE Data Handling
    # NEW FEATURE: TÜFE Data Handling
    # - Handles TÜFE data unavailability with fallback to manual entry
    # - Shows "TÜFE data pending" when official data is unavailable
    # - Allows manual entry of official CPI rate for legal calculations
    st.markdown("---")
    st.subheader("📈 TÜFE Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**TÜFE Data Status**")
        current_year = datetime.now().year
        
        # Check TÜFE availability
        is_available = services['inflation_service'].is_tufe_available(current_year)
        if is_available:
            tufe_rate = services['inflation_service'].get_yearly_tufe(current_year)
            st.success(f"✅ TÜFE data available for {current_year}: {tufe_rate}%")
        else:
            st.warning(f"⚠️ TÜFE data pending for {current_year}")
            
            # Manual TÜFE entry option
            if st.button("📝 Enter TÜFE Manually"):
                tufe_input = st.number_input(
                    f"Enter TÜFE rate for {current_year} (%)",
                    min_value=0.0,
                    value=50.0,
                    step=0.1
                )
                if st.button("💾 Save TÜFE"):
                    try:
                        services['inflation_service'].save_manual_entry(
                            month=12,  # Year-end data
                            year=current_year,
                            inflation_rate_percent=Decimal(str(tufe_input)),
                            source="TÜFE Manual Entry"
                        )
                        st.success("✅ TÜFE data saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    with col2:
        st.write("**TÜFE Data Source**")
        st.info("📊 **Data source**: TCMB (exchange rates), TÜFE (inflation)")
        
        # Fetch from TCMB API button
        if st.button("🔄 Fetch from TCMB API"):
            if not is_api_configured:
                st.error("❌ Please configure TCMB API key first")
            else:
                with st.spinner("Fetching TÜFE data from TCMB API..."):
                    try:
                        # Try to get API key from config service first, then session state
                        api_key = services['tufe_config_service'].get_tcmb_api_key()
                        if not api_key and 'tcmb_api_key' in st.session_state:
                            api_key = st.session_state['tcmb_api_key']
                            st.info(f"🔍 **Debug**: Using API key from session state (length: {len(api_key)})")
                        
                        if not api_key:
                            st.error("❌ No API key found. Please configure your TCMB API key first.")
                        else:
                            st.info(f"🔍 **Debug**: Using API key (length: {len(api_key)}, starts with: {api_key[:10]}...)")
                            tufe_rate = services['inflation_service'].fetch_tufe_from_tcmb_api(current_year, api_key)
                            
                            if tufe_rate is not None:
                                # Save the fetched TÜFE data
                                services['inflation_service'].save_manual_entry(
                                    month=12,  # Year-end data
                                    year=current_year,
                                    inflation_rate_percent=tufe_rate,
                                    source="TCMB EVDS API"
                                )
                                st.success(f"✅ TÜFE data fetched from TCMB API: {tufe_rate}%")
                                st.rerun()
                            else:
                                st.warning("⚠️ TÜFE data not found in TCMB API. Please enter manually.")
                    except Exception as e:
                        st.error(f"❌ Error fetching from TCMB API: {e}")
                        st.info("Please enter TÜFE data manually.")
    
    # Cache Management
    st.markdown("---")
    st.subheader("🗄️ TÜFE Data Cache")
    
    # Documentation for cache management
    with st.expander("ℹ️ About TÜFE Data Cache"):
        st.markdown("""
        **TÜFE Data Cache Management**
        
        The cache system stores TÜFE data to improve performance and reduce API calls.
        
        **Cache Features:**
        - ⏰ **24-Hour Expiration**: Data is automatically refreshed after 24 hours
        - 📊 **Source Attribution**: Each cache entry tracks its data source
        - 🔄 **Automatic Cleanup**: Expired entries are automatically removed
        - 📈 **Performance Optimization**: Reduces API calls and improves response times
        - 🛡️ **Data Integrity**: Validates data before caching
        
        **Cache Operations:**
        - **Refresh**: Manually refresh expired cache entries
        - **Cleanup**: Remove expired entries to free up space
        - **Statistics**: View cache performance and usage metrics
        """)
    
    # Cache Statistics
    try:
        cache_stats = services['tufe_cache_service'].get_cache_stats()
        cache_summary = services['tufe_cache_service'].get_cache_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Entries", cache_stats['total_entries'])
        with col2:
            st.metric("Valid Entries", cache_stats['valid_entries'])
        with col3:
            st.metric("Expired Entries", cache_stats['expired_entries'])
        with col4:
            validity_rate = cache_stats['validity_rate'] * 100
            st.metric("Validity Rate", f"{validity_rate:.1f}%")
        
        # Cache Management Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Cleanup Expired Cache"):
                with st.spinner("Cleaning up expired cache entries..."):
                    try:
                        cleaned_count = services['tufe_cache_service'].cleanup_expired_cache()
                        st.success(f"✅ Cleaned up {cleaned_count} expired cache entries")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error cleaning cache: {e}")
        
        with col2:
            if st.button("🔄 Refresh Cache Status"):
                st.rerun()
        
        with col3:
            if st.button("📊 View Cache Details"):
                st.write("**Cached Years:**", cache_summary['cached_years'])
                if cache_summary['year_range']['min'] and cache_summary['year_range']['max']:
                    st.write(f"**Year Range:** {cache_summary['year_range']['min']} - {cache_summary['year_range']['max']}")
        
    except Exception as e:
        st.error(f"❌ Error loading cache information: {e}")
    
    # Display inflation data
    st.markdown("---")
    st.subheader("📋 Saved Inflation Data")
    
    inflation_data = services['inflation_service'].get_all_inflation_data()
    
    if inflation_data:
        data = []
        for inf in inflation_data:
            data.append({
                "Period": f"{inf.year}-{inf.month:02d}",
                "Inflation Rate": f"{inf.inflation_rate_percent:.2f}%",
                "Legal Max Multiplier": f"{inf.legal_max_increase_multiplier():.4f}x",
                "Source": inf.source
            })
        
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No inflation data saved yet.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Kira Prolongation Support v1.0")
st.sidebar.caption("Made with ❤️ and Streamlit")

