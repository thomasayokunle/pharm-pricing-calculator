# ==============================================================
# Pricing Calculator - Demo Version
# ==============================================================

import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pricing Calculator Demo", layout="wide")

# --- HEADER ---
st.title("🧪 Pricing Calculator Demo")
st.markdown("""
Try out the pricing calculator with your own data. Enter your product details below to see instant profitability analysis.

**Note:** This is a limited demo. The full version includes Google Sheets integration, multi-product support, 
advanced volume modeling, and much more.
""")

st.markdown("---")

def round50(value):
    return int(round(value / 50.0)) * 50

# --- DEMO INPUTS ---
st.subheader("Enter Your Product Details")

col1, col2 = st.columns(2)

with col1:
    product_name = st.text_input("Product/Test Name", value="Sample Product", 
                                 help="Enter the name of your product or test")
    cost_price = st.number_input("Cost Price (COGS) - ₦", min_value=0, value=5000, step=100,
                                 help="Your cost to acquire or produce this product")
    current_selling_price = st.number_input("Current Selling Price - ₦", min_value=0, value=8000, step=100,
                                            help="What you currently charge for this product")

with col2:
    opex_percent = st.slider("Operating Expenses (% of Revenue)", 0, 50, 25, 1,
                             help="What percentage of revenue goes to operating costs (staff, rent, utilities, etc.)")
    proposed_price = st.number_input("Proposed New Price - ₦", min_value=0, value=9000, step=50,
                                    help="Test a new price to see how it affects profitability")
    volume = st.slider("Expected Volume (units)", 1, 100, 10, 1,
                      help="How many units do you expect to sell")

# --- CALCULATIONS ---
opex_rate = opex_percent / 100

# Current scenario
current_revenue = current_selling_price
current_cogs = cost_price
current_gross_profit = current_revenue - current_cogs
current_opex = opex_rate * current_revenue
current_profit = current_gross_profit - current_opex
current_margin = (current_profit / current_revenue * 100) if current_revenue > 0 else 0

# Proposed scenario
proposed_revenue = proposed_price
proposed_cogs = cost_price
proposed_gross_profit = proposed_revenue - proposed_cogs
proposed_opex = opex_rate * proposed_revenue
proposed_profit = proposed_gross_profit - proposed_opex
proposed_margin = (proposed_profit / proposed_revenue * 100) if proposed_revenue > 0 else 0

# Total for volume
total_revenue = proposed_price * volume
total_profit = proposed_profit * volume

# Check if profitable
if proposed_margin < 15:
    status = "🔴 Low Margin"
    status_color = "red"
elif proposed_margin < 25:
    status = "🟡 Moderate Margin"
    status_color = "orange"
else:
    status = "🟢 Healthy Margin"
    status_color = "green"

# --- DISPLAY RESULTS ---
st.markdown("---")
st.subheader(f"Results: {product_name}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Proposed Price",
        f"₦{round50(proposed_price):,.0f}",
        f"{((proposed_price - current_selling_price) / current_selling_price * 100):+.1f}%"
    )

with col2:
    st.metric(
        "Profit Margin",
        f"{proposed_margin:.1f}%",
        status
    )

with col3:
    st.metric(
        "Total Revenue",
        f"₦{total_revenue:,.0f}",
        f"{volume} units"
    )

with col4:
    st.metric(
        "Total Profit",
        f"₦{total_profit:,.0f}",
        f"{proposed_margin:.1f}% margin"
    )

# --- COMPARISON TABLE ---
st.markdown("---")
st.subheader("Per Unit Breakdown")

comparison = pd.DataFrame({
    "Metric": [
        "Selling Price (₦)",
        "Cost Price (₦)",
        "Gross Profit (₦)",
        "Operating Cost (₦)",
        "Net Profit (₦)",
        "Profit Margin (%)"
    ],
    "Current": [
        f"₦{round50(current_revenue):,.0f}",
        f"₦{round50(current_cogs):,.0f}",
        f"₦{round50(current_gross_profit):,.0f}",
        f"₦{round50(current_opex):,.0f}",
        f"₦{round50(current_profit):,.0f}",
        f"{current_margin:.1f}%"
    ],
    "Proposed": [
        f"₦{round50(proposed_revenue):,.0f}",
        f"₦{round50(proposed_cogs):,.0f}",
        f"₦{round50(proposed_gross_profit):,.0f}",
        f"₦{round50(proposed_opex):,.0f}",
        f"₦{round50(proposed_profit):,.0f}",
        f"{proposed_margin:.1f}%"
    ]
})

st.dataframe(comparison, use_container_width=True, hide_index=True)

# --- SIMPLE RECOMMENDATION ---
st.markdown("---")
st.subheader("Quick Analysis")

if proposed_margin < 15:
    st.error(f"""
    **Low Margin Alert:** At ₦{round50(proposed_price):,.0f}, your profit margin is only {proposed_margin:.1f}%.
    
    Consider:
    - Increasing price
    - Reducing operating costs
    - Reviewing cost price with suppliers
    """)
elif proposed_margin < 25:
    st.warning(f"""
    **Moderate Margin:** At ₦{round50(proposed_price):,.0f}, margin is {proposed_margin:.1f}%.
    
    This works but leaves limited room for unexpected costs or discounts.
    """)
else:
    st.success(f"""
    **Healthy Margin:** At ₦{round50(proposed_price):,.0f}, margin is {proposed_margin:.1f}%.
    
    You have {(proposed_margin - 20):.1f}% cushion above a typical 20% target.
    """)

# --- CALL TO ACTION ---
st.markdown("---")
st.subheader("Ready for the Full Solution?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Full Version Benefits:**
    - Connect directly to your Google Sheets
    - Manage hundreds of products
    - Multiple business units
    - Real-time updates
    - Professional interface
    - Team collaboration
    - Mobile access
    """)

with col2:
    st.markdown("""
    **Pricing:**
    - Single Unit: ₦450,000 one-time
    - Multiple Units: ₦700,000 one-time
    - Enterprise: ₦1M - ₦1.2M
    
    Optional quarterly support available.
    
    **[Schedule a Free Demo](mailto:your-email@example.com)**
    """)

# --- FOOTER ---
st.markdown("---")
st.caption("**Demo Version** - Limited functionality for evaluation purposes")
st.markdown(
    "<p style='text-align:center; font-size:14px;'>Pricing Intelligence System by <b>Ayokunle Thomas</b> – Data Scientist</p>",
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    .footer-links {
        text-align: center;
        font-size: 12px;
        font-style: italic;
        color: #888888;
    }
    .footer-links a {
        color: #888888;
        text-decoration: none;
        margin: 0 6px;
        transition: color 0.3s ease;
    }
    .footer-links a:hover {
        color: #1f77b4;
    }
    </style>
    <div class="footer-links">
        <a href="https://www.linkedin.com/in/ayokunle-thomas" target="_blank">LinkedIn</a> |
        <a href="https://github.com/ThomasAyokunle" target="_blank">GitHub</a> |
        <a href="mailto:your-email@example.com">Contact</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("© 2025 - All Rights Reserved")