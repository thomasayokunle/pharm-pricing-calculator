# ==============================================================
# Pharmacy Pricing & Volume Sensitivity Calculator
# ==============================================================

import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing Calculator", layout="wide")

st.title("Pharmacy Pricing & Volume Sensitivity Calculator")
st.caption("Analyze how price, volume, and OPEX adjustments impact departmental profitability.")

# --- LOAD DATA ---
url = "https://docs.google.com/spreadsheets/d/1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4/export?format=csv&gid=876068924"

try:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
except Exception as e:
    st.error(f"Error loading Google Sheet: {e}")
    st.stop()

required_cols = ["departments", "revenue", "cogs", "volume sold", "opex%"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"This sheet must include the following columns: {', '.join(required_cols)}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Simulation Controls")

department = st.sidebar.selectbox("Select Department", df["departments"].unique())
markup = st.sidebar.slider("Markup Multiplier (×)", 0.5, 3.0, 1.2, 0.05)
volume_growth = st.sidebar.slider("Projected Volume Growth (%)", -50, 200, 20, 5)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity to Volume (%)", 0, 100, 10, 5)

# --- FILTER SELECTED DEPARTMENT ---
data = df[df["departments"] == department].iloc[0]

# --- BASE METRICS ---
revenue = data["revenue"]
cogs = data["cogs"]
volume = data["volume sold"]
opex_percent = data["opex%"] / 100

# Base average price
base_price = revenue / volume if volume > 0 else 0

# --- PROPOSED SCENARIO CALCULATIONS ---
proposed_volume = volume * (1 + volume_growth / 100)
proposed_price = base_price * markup
proposed_revenue = proposed_price * proposed_volume
proposed_cogs = (cogs / volume) * proposed_volume
proposed_opex = (opex_percent * proposed_revenue) * (1 + opex_sensitivity / 100)

# --- PROFITABILITY CALCULATIONS ---
base_opex = opex_percent * revenue
base_profit = revenue - cogs - base_opex
proposed_profit = proposed_revenue - proposed_cogs - proposed_opex

base_margin = (base_profit / revenue) * 100 if revenue > 0 else 0
proposed_margin = (proposed_profit / proposed_revenue) * 100 if proposed_revenue > 0 else 0

# --- ALERT BANNER ---
if proposed_margin < base_margin:
    st.warning("Proposed changes may reduce profit margin. Consider adjusting price or volume.")
elif proposed_margin > base_margin + 5:
    st.success("Proposed changes significantly improve profitability. Monitor demand response.")
else:
    st.info("Profitability change within normal range. Fine-tune parameters for optimization.")

# --- SUMMARY BLOCK ---
st.markdown(f"""
### 📊 Department Summary: **{department}**
| Metric | Current | Proposed | Change |
|:--|--:|--:|--:|
| **Average Price (₦)** | ₦{base_price:,.2f} | ₦{proposed_price:,.2f} | {((proposed_price/base_price - 1)*100):.1f}% |
| **Volume Sold** | {volume:,.0f} | {proposed_volume:,.0f} | {volume_growth:.1f}% |
| **Revenue (₦)** | ₦{revenue:,.0f} | ₦{proposed_revenue:,.0f} | {((proposed_revenue/revenue - 1)*100):.1f}% |
| **COGS (₦)** | ₦{cogs:,.0f} | ₦{proposed_cogs:,.0f} | {((proposed_cogs/cogs - 1)*100):.1f}% |
| **OPEX (₦)** | ₦{base_opex:,.0f} | ₦{proposed_opex:,.0f} | {((proposed_opex/base_opex - 1)*100):.1f}% |
| **Profit (₦)** | ₦{base_profit:,.0f} | ₦{proposed_profit:,.0f} | {((proposed_profit/base_profit - 1)*100 if base_profit else 0):.1f}% |
| **Net Profit Margin (%)** | {base_margin:.1f}% | {proposed_margin:.1f}% | {proposed_margin - base_margin:+.1f} pts |
""")

# --- ANALYTICAL INSIGHT ---
st.markdown(f"""
**Insight Summary**  
At a proposed markup of **{markup}×** and a projected volume change of **{volume_growth}%**,  
department **{department}** expects revenue of **₦{proposed_revenue:,.0f}**, with COGS and OPEX scaling accordingly.  
EBITDA margin shifts from **{base_margin:.1f}%** to **{proposed_margin:.1f}%**, driven by volume sensitivity and OPEX dynamics.  
""")

st.caption("*OPEX sensitivity shows how operating expenses change relative to revenue growth.*")

# --- VOLUME-PRICE IMPACT SIMULATION ---
st.subheader("📈 Volume–Price Sensitivity (EBITDA Projection)")

simulation = pd.DataFrame({
    "Volume Growth (%)": range(-50, 201, 10)
})
simulation["Volume"] = volume * (1 + simulation["Volume Growth (%)"] / 100)
simulation["Proposed Revenue"] = proposed_price * simulation["Volume"]
simulation["Proposed COGS"] = (cogs / volume) * simulation["Volume"]
simulation["Proposed OPEX"] = (opex_percent * simulation["Proposed Revenue"]) * (1 + opex_sensitivity / 100)
simulation["Proposed EBITDA"] = simulation["Proposed Revenue"] - simulation["Proposed COGS"] - simulation["Proposed OPEX"]
simulation["EBITDA Margin (%)"] = (simulation["Proposed EBITDA"] / simulation["Proposed Revenue"]) * 100

st.line_chart(simulation.set_index("Volume Growth (%)")[["EBITDA Margin (%)"]])

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:14px;'>Created by <b>Ayokunle Thomas</b> – Data Analyst</p>",
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

st.caption("ExCare Services Pharmacy Department Pricing Calculator © 2025")
st.caption("Business Insight Unit")
