# ==============================================================
# Pharmacy Department P&L Sensitivity App
# ExCare Services Limited – by Ayokunle Thomas
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing P&L Sensitivity", layout="wide")

# --- HEADER ---
st.title("Pharmacy Department Pricing & P&L Dashboard")
st.caption("Analyze how changes in markup, sales volume, and OPEX affect gross and net profitability by department.")

# --- DATA SOURCE ---
sheet_url = "https://docs.google.com/spreadsheets/d/1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4/export?format=csv&gid=876068924"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip().str.lower()
    # --- CLEANUP & CONVERT TYPES ---
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df["cogs"] = pd.to_numeric(df["cogs"], errors="coerce")
    df["volume sold"] = pd.to_numeric(df["volume sold"], errors="coerce")
    df["opex%"] = pd.to_numeric(df["opex%"], errors="coerce").fillna(0)
    return df

df = load_data()

required_cols = ["departments", "revenue", "cogs", "volume sold", "opex%"]
if not all(col in df.columns for col in required_cols):
    st.error(f"The sheet must include: {', '.join(required_cols)}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Scenario Controls")
department = st.sidebar.selectbox("Select Department", df["departments"].unique())
volume_growth = st.sidebar.slider("Projected Volume Growth (%)", -50, 300, 0, 10)
markup = st.sidebar.slider("Proposed Markup Multiplier (×)", 0.8, 3.0, 1.2, 0.05)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity to Volume (%)", 0, 100, 15, 5)
margin_threshold = st.sidebar.number_input("Minimum Acceptable Net Margin (%)", 0.0, 100.0, 20.0)

# --- GET DEPARTMENT DATA ---
data = df[df["departments"] == department].iloc[0]
revenue = data["revenue"]
cogs = data["cogs"]
volume = data["volume sold"]
opex_percent = float(data["opex%"]) / 100
st.write(f"OPEX% for {department}: {opex_percent:.2%}")


# --- BASE VALUES ---
price_per_unit = revenue / volume if volume > 0 else 0
cost_per_unit = cogs / volume if volume > 0 else 0
current_markup = price_per_unit / cost_per_unit if cost_per_unit > 0 else 0
current_opex = opex_percent * revenue

# --- CURRENT P&L ---
current_gross_profit = revenue - cogs
current_net_profit = current_gross_profit - current_opex
current_gross_margin = (current_gross_profit / revenue) * 100 if revenue > 0 else 0
current_net_margin = (current_net_profit / revenue) * 100 if revenue > 0 else 0

# --- PROPOSED SCENARIO ---
new_volume = volume * (1 + volume_growth / 100)
new_price = cost_per_unit * markup
new_revenue = new_volume * new_price
new_cogs = new_volume * cost_per_unit
new_gross_profit = new_revenue - new_cogs

# --- Semi-Fixed OPEX Model (70% Fixed, 30% Variable) ---
opex_fixed_ratio = 0.7
opex_variable_ratio = 0.3
new_opex = current_opex * (
    opex_fixed_ratio + opex_variable_ratio * (1 + (opex_sensitivity / 100) * (new_volume / volume))
)

# --- NEW P&L ---
new_net_profit = new_gross_profit - new_opex
new_gross_margin = (new_gross_profit / new_revenue) * 100 if new_revenue > 0 else 0
new_net_margin = (new_net_profit / new_revenue) * 100 if new_revenue > 0 else 0

# --- ALERT BANNER ---
if new_net_margin < margin_threshold:
    st.error(f"Net Margin drops to {new_net_margin:.1f}%, below target ({margin_threshold}%)")
elif new_net_margin >= margin_threshold + 5:
    st.success(f"Net Margin improves to {new_net_margin:.1f}%, comfortably above target.")
else:
    st.info(f"Net Margin is {new_net_margin:.1f}%, near the threshold ({margin_threshold}%).")

# --- COMPARISON TABLE ---
st.subheader(f"Department P&L Comparison: {department}")

summary = pd.DataFrame({
    "Metric": [
        "Revenue (₦)",
        "COGS (₦)",
        "Gross Profit (₦)",
        "OPEX (₦)",
        "Net Profit (₦)",
        "Gross Margin (%)",
        "Net Margin (%)",
        "Markup (×)",
        "Volume Sold"
    ],
    "Current": [
        revenue,
        cogs,
        current_gross_profit,
        current_opex,
        current_net_profit,
        current_gross_margin,
        current_net_margin,
        current_markup,
        volume
    ],
    "Proposed": [
        new_revenue,
        new_cogs,
        new_gross_profit,
        new_opex,
        new_net_profit,
        new_gross_margin,
        new_net_margin,
        markup,
        new_volume
    ]
})

summary["Change (%)"] = ((summary["Proposed"] - summary["Current"]) / summary["Current"]) * 100
summary["Change (%)"] = summary["Change (%)"].apply(lambda x: f"{x:.1f}%" if np.isfinite(x) else "–")

st.dataframe(
    summary.style.format({
        "Current": "{:,.2f}",
        "Proposed": "{:,.2f}",
        "Change (%)": "{}"
    })
)

# --- INSIGHT ---
net_change = new_net_margin - current_net_margin
direction = "increase" if net_change > 0 else "drop"

st.markdown(f"""
### Insight Summary
With a **markup of ×{markup:.2f}** and **volume change of {volume_growth}%**,  
**{department}**'s **Net Margin** moves from **{current_net_margin:.1f}% → {new_net_margin:.1f}%**,  
while **Gross Margin** changes from **{current_gross_margin:.1f}% → {new_gross_margin:.1f}%**.  
This represents a **{abs(net_change):.1f}% {direction}** in profitability after OPEX adjustment.
""")

# --- FOOTER ---
st.markdown("---")
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
        color: #1f77b4; /* Subtle blue hover */
    }
    </style>

    <div class="footer-links">
        <a href="https://www.linkedin.com/in/ayokunle-thomas" target="_blank">LinkedIn</a> |
        <a href="https://github.com/ThomasAyokunle" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("ExCare Health Pharmacy Pricing Calculator © 2025")
