"""
Kira Prolongation Support - Streamlit Application
Main entry point for the rental fee negotiation support tool.
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
    ScreenshotParserService,
    CalculationService,
    ExportService
)
from src.models import RentalAgreement, MarketRate
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
    """Initialize all services with DataStore"""
    data_store = DataStore()
    return {
        'data_store': data_store,
        'exchange_rate_service': ExchangeRateService(data_store),
        'inflation_service': InflationService(data_store),
        'screenshot_parser': ScreenshotParserService(),
        'calculation_service': CalculationService(),
        'export_service': ExportService(),
        'chart_generator': ChartGenerator()
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
        "🏘️ Market Comparison",
        "📈 Visualizations",
        "🤝 Negotiation Summary",
        "📊 Inflation Data"
    ]
)

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

elif page == "🏘️ Market Comparison":
    st.title("🏘️ Market Comparison")
    st.markdown("Upload screenshots from sahibinden.com to compare market rental rates.")
    
    # Screenshot upload
    st.subheader("📸 Upload Screenshot")
    
    uploaded_file = st.file_uploader(
        "Choose a screenshot",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a screenshot from sahibinden.com showing rental prices"
    )
    
    if uploaded_file:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Screenshot", use_column_width=True)
        
        if st.button("🔍 Parse Screenshot"):
            with st.spinner("Processing with OCR..."):
                try:
                    # Parse screenshot
                    market_rates = services['screenshot_parser'].parse_screenshot(
                        image,
                        uploaded_file.name
                    )
                    
                    if market_rates:
                        st.success(f"✅ Found {len(market_rates)} rental prices!")
                        
                        # Display and save
                        for i, rate in enumerate(market_rates):
                            with st.expander(f"Rate {i+1}: {rate.amount_tl:,.0f} TL"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Amount**: {rate.amount_tl:,.0f} TL")
                                    if rate.location:
                                        st.write(f"**Location**: {rate.location}")
                                with col2:
                                    if st.button(f"💾 Save Rate {i+1}", key=f"save_{i}"):
                                        services['data_store'].save_market_rate(rate)
                                        st.success("Saved!")
                    else:
                        st.warning("⚠️ No rental prices found in screenshot. Try a clearer image.")
                        
                except Exception as e:
                    st.error(f"❌ OCR Error: {e}")
                    st.exception(e)
    
    # Display saved market rates
    st.markdown("---")
    st.subheader("📊 Saved Market Rates")
    
    market_rates = services['data_store'].get_market_rates()
    
    if market_rates:
        for rate in market_rates:
            with st.expander(f"{rate.amount_tl:,.0f} TL - {rate.location or 'Unknown'} ({rate.date_captured})"):
                st.write(f"**Screenshot**: {rate.screenshot_filename}")
                if rate.raw_ocr_text:
                    with st.expander("View raw OCR text"):
                        st.text(rate.raw_ocr_text)
    else:
        st.info("No market rates saved yet.")

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
        st.plotly_chart(fig1, use_container_width=True)
        
        # Payment comparison
        st.subheader("📊 Payment Comparison")
        fig2 = services['chart_generator'].create_payment_comparison_bar_chart(payments)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Market comparison
        market_rates = services['data_store'].get_market_rates()
        if market_rates and len(market_rates) > 0:
            st.subheader("🏘️ Market Comparison")
            latest_payment = sorted(payments, key=lambda p: (p.year, p.month))[-1]
            fig3 = services['chart_generator'].create_market_comparison_chart(
                latest_payment.amount_tl,
                market_rates
            )
            st.plotly_chart(fig3, use_container_width=True)

elif page == "🤝 Negotiation Summary":
    st.title("🤝 Negotiation Summary")
    st.markdown("Key statistics and data points to support your rent negotiation.")
    
    # Get latest data
    payments = services['data_store'].get_payment_records()
    agreements = services['data_store'].get_rental_agreements()
    market_rates = services['data_store'].get_market_rates()
    
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
        
        # Market comparison
        if market_rates:
            st.subheader("🏘️ Market Position")
            comparison = services['calculation_service'].calculate_market_comparison(
                latest_payment.amount_tl,
                market_rates
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Average", f"{comparison['market_avg']:,.0f} TL")
            with col2:
                st.metric("Your Position", comparison['position'].replace('_', ' ').title())
            with col3:
                st.metric("vs Market Avg", f"{comparison['user_vs_avg_percent']:,.1f}%")
        
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

