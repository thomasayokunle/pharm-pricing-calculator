# ==============================================================
# Pharmacy Pricing Calculator (Marketing Edition)
# ==============================================================

import streamlit as st
import pandas as pd
import math
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="ExCare Pharmacy Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Pharmacy Pricing Calculator")
st.markdown("""
Test pricing scenarios for negotiations. Compare different prices and volumes 
to find the optimal balance between competitiveness and profitability.
""")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4"

def load_sheet(sheet_name):
    """Loads a Google Sheet as CSV and converts numeric columns safely."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.title()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

def round50(value):
    """Round to nearest 50 for clean pricing."""
    try:
        return int(round(value / 50.0)) * 50
    except:
        return 0

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Scenario Settings")

pharm = st.sidebar.selectbox("Department", ["REFILL", "VACCINE"])
df = load_sheet(pharm)

selected_product = st.sidebar.multiselect("Product", df["Product Name"].unique(), default=[df["Product Name"].iloc[0]])

st.sidebar.markdown("---")
st.sidebar.subheader("Pricing Options")

st.sidebar.markdown("---")
st.sidebar.subheader("Volume & Costs")
volume = st.sidebar.slider("Projected Volume (units)", 0, 500, 20, 5, help="Total units expected to sell. Higher volumes may justify lower prices if partner commits to bulk orders"
)
opex_adjustment = st.sidebar.slider("OPEX Adjustment (%)", -50, 100, 0, 5, 
                                    help="Extra costs beyond normal operations, like special storage, additional staff,or extra logistics fee")

st.sidebar.markdown("---")
st.sidebar.subheader("Target Margin")
target_margin = st.sidebar.slider("Minimum Net Margin (%)", 0, 50, 20, 1, help="Your minimum acceptable profit margin. Price will be flagged if it falls below this threshold"
)

# --- FETCH PRODUCT DETAILS ---
product = df[df["Product Name"].isin(selected_product)]
current_price = float(product["Current Price"].mean())
cogs_per_unit = float(product["Cogs"].mean())

# Get OPEX % from sheet
if "Opex%" in df.columns or "Opex %" in df.columns:
    opex_col = "Opex%" if "Opex%" in df.columns else "Opex %"
    opex_percent = df[opex_col].dropna().iloc[0] / 100
else:
    opex_percent = 0.10  # fallback default (25%)

# --- PRICE CALCULATION ---
opex_factor = 1 + (opex_adjustment / 100)
denominator = 1 - (opex_percent * opex_factor) - (target_margin / 100)
if denominator <= 0:
    st.error("OPEX% + Target Margin% exceeds 100%. Adjust your inputs.")
    st.stop()
proposed_price_per_unit = round50(cogs_per_unit / denominator)

# --- CURRENT SCENARIO (Per Unit) ---
current_revenue_per_unit = current_price
current_cogs_per_unit = cogs_per_unit
current_gross_profit_per_unit = current_revenue_per_unit - current_cogs_per_unit
current_opex_per_unit = opex_percent * current_revenue_per_unit
current_ebitda_per_unit = current_gross_profit_per_unit - current_opex_per_unit
current_margin = round((current_ebitda_per_unit / current_revenue_per_unit) * 100, 1) if current_revenue_per_unit != 0 else 0

# --- PROPOSED SCENARIO (Total for Volume) ---

proposed_opex_per_unit = (opex_percent * proposed_price_per_unit) * opex_factor

# Per unit calculations
proposed_revenue_per_unit = proposed_price_per_unit
proposed_cogs_per_unit = cogs_per_unit
proposed_gross_profit_per_unit = proposed_revenue_per_unit - proposed_cogs_per_unit
proposed_ebitda_per_unit = proposed_gross_profit_per_unit - proposed_opex_per_unit
proposed_margin = round((proposed_ebitda_per_unit / proposed_revenue_per_unit) * 100, 1) if proposed_revenue_per_unit != 0 else 0

# Total calculations (for volume)
total_revenue = proposed_price_per_unit * volume
total_cogs = cogs_per_unit * volume
total_gross_profit = total_revenue - total_cogs
total_opex = proposed_opex_per_unit * volume
total_ebitda = total_gross_profit - total_opex

# --- MINIMUM MARGIN CHECK ---
min_required_price = (cogs_per_unit + proposed_opex_per_unit) / (1 - (target_margin / 100))
margin_gap = proposed_price_per_unit - min_required_price

if margin_gap < 0:
    st.warning(f"**Price below minimum threshold!** Need ₦{round50(min_required_price):,.0f} to achieve {target_margin}% margin.")
    price_status = "Below Target"
    price_status_color = "red"
elif margin_gap < 500:
    price_status = "At Minimum"
    price_status_color = "orange"
else:
    price_status = "Healthy Margin"
    price_status_color = "green"

# --- MAIN DISPLAY ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Proposed Price", f"₦{proposed_price_per_unit:,.0f}", 
              f"{((proposed_price_per_unit - current_price) / current_price * 100):+.1f}%")
with col2:
    st.metric("Net Margin", f"{proposed_margin:.1f}%", 
              f"{(proposed_margin - current_margin):+.1f}%")
with col3:
    st.metric("Total Revenue", f"₦{total_revenue:,.0f}", 
              f"{volume} units")
with col4:
    st.metric("Total EBITDA", f"₦{total_ebitda:,.0f}", 
              price_status)

st.markdown("---")

# --- PER UNIT COMPARISON ---
st.subheader("Average Per Unit Economics (across selected products)")

per_unit_comparison = pd.DataFrame({
    "Metric": [
        "Price per Unit (₦)",
        "COGS per Unit (₦)", 
        "Gross Profit per Unit (₦)",
        "OPEX per Unit (₦)",
        "EBITDA per Unit (₦)",
        "Net Margin (%)"
    ],
    "Current": [
        round50(current_revenue_per_unit),
        round50(current_cogs_per_unit),
        round50(current_gross_profit_per_unit),
        round50(current_opex_per_unit),
        round50(current_ebitda_per_unit),
        current_margin
    ],
    "Proposed": [
        round50(proposed_revenue_per_unit),
        round50(proposed_cogs_per_unit),
        round50(proposed_gross_profit_per_unit),
        round50(proposed_opex_per_unit),
        round50(proposed_ebitda_per_unit),
        proposed_margin
    ],
    "Difference": [
        round50(proposed_revenue_per_unit - current_revenue_per_unit),
        0,  # COGS stays same per unit
        round50(proposed_gross_profit_per_unit - current_gross_profit_per_unit),
        round50(proposed_opex_per_unit - current_opex_per_unit),
        round50(proposed_ebitda_per_unit - current_ebitda_per_unit),
        round(proposed_margin - current_margin, 1)
    ]
})

st.dataframe(
    per_unit_comparison.style.format({
        "Current": "{:,.0f}",
        "Proposed": "{:,.0f}",
        "Difference": lambda x: f"{x:+,.0f}" if isinstance(x, (int, float)) else x
    }),
    use_container_width=True
)

# --- TOTAL VOLUME SUMMARY ---
st.subheader("Total Volume Impact")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Scenario Summary:**
    - **Volume**: {volume} units
    - **Price per Unit**: ₦{proposed_price_per_unit:,.0f}
    - **Total Revenue**: ₦{total_revenue:,.0f}
    - **Total EBITDA**: ₦{total_ebitda:,.0f}
    - **Net Margin**: {proposed_margin:.1f}%
    """)

with col2:
    st.markdown(f"""
    **Cost Breakdown:**
    - **Total COGS**: ₦{total_cogs:,.0f} ({(total_cogs/total_revenue*100):.1f}%)
    - **Total OPEX**: ₦{total_opex:,.0f} ({(total_opex/total_revenue*100):.1f}%)
    - **Gross Margin**: {((total_gross_profit/total_revenue)*100):.1f}%
    """)

# --- BREAK-EVEN ANALYSIS ---
#st.markdown("---")
#st.subheader("📊 Break-Even Analysis")

# Calculate break-even volume at different margin targets
#margin_targets = [0, 10, 15, 20, 25, 30]
#breakeven_volumes = []

#for target in margin_targets:
 #   if target == 0:
        # Break-even = cover COGS + OPEX only
  #      be_vol = 1 if proposed_ebitda_per_unit >= 0 else 0
   # else:
        # Need to solve: (Price - COGS - OPEX) / Price = Target%
        # This is already calculated per unit, so if per-unit margin meets target, volume=1
    #    be_vol = 1 if proposed_margin >= target else 0
    #breakeven_volumes.append(be_vol if be_vol > 0 else "N/A")

#breakeven_df = pd.DataFrame({
 #   "Target Margin": [f"{t}%" for t in margin_targets],
  #  "Current Price": [f"₦{current_price:,.0f}"] * len(margin_targets),
   # "Proposed Price": [f"₦{proposed_price_per_unit:,.0f}"] * len(margin_targets),
    #"Achievable?": ["✅" if proposed_margin >= t else "❌" for t in margin_targets]
#})

#st.dataframe(breakeven_df, use_container_width=True)

# --- VOLUME SIMULATION ---
#st.markdown("---")
#st.subheader("📈 Volume Projection (EBITDA Growth)")

#max_vol = max(volume, 100)
#projection = pd.DataFrame({
 #   "Volume": range(1, max_vol + 1),
  #  "Total Revenue": [proposed_price_per_unit * v for v in range(1, max_vol + 1)],
   # "Total EBITDA": [
    #    proposed_ebitda_per_unit * v for v in range(1, max_vol + 1)
    #]
#})

#st.line_chart(projection.set_index("Volume"))

# --- PRICING RECOMMENDATIONS ---
st.markdown("---")
st.subheader("Pricing Recommendations")

if proposed_margin < target_margin:
    st.error(f"""
    **Price Too Low**: At ₦{proposed_price_per_unit:,.0f}, margin is {proposed_margin:.1f}% (target: {target_margin}%).
    
    **Recommended Actions:**
    - Increase price to ₦{round50(min_required_price):,.0f}
    - Reduce OPEX by {abs((min_required_price - proposed_price_per_unit) / proposed_price_per_unit * 100):.1f}%
    - Negotiate volume commitments for better terms
    """)
elif proposed_margin < target_margin + 5:
    st.warning(f"""
    **Tight Margin**: At ₦{proposed_price_per_unit:,.0f}, margin is {proposed_margin:.1f}% (target: {target_margin}%).
    
    Consider adding ₦{round50((min_required_price + 200) - proposed_price_per_unit):,.0f} buffer for safety.
    """)
else:
    st.success(f"""
    **Healthy Pricing**: At ₦{proposed_price_per_unit:,.0f}, margin is {proposed_margin:.1f}% ({(proposed_margin - target_margin):.1f}% above target).
    
    - Room for negotiation: Up to ₦{round50(margin_gap * 0.5):,.0f} discount possible
    - Competitive positioning: {'Premium' if proposed_price_per_unit > current_price * 1.2 else 'Competitive' if proposed_price_per_unit > current_price * 0.9 else 'Aggressive'}
    """)

# --- FOOTER ---
st.markdown("---")
st.caption("**Usage Tips**: **Tip:** Adjust the proposed price to see how it affects profit margin and total profit.")

st.markdown(
    "<p style='text-align:center; font-size:14px;'>Created by <b>Ayokunle Thomas</b> – Data Scientist</p>",
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
        <a href="https://github.com/ThomasAyokunle" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("ExCare Services Pharmacy Pricing Calculator © 2025")
