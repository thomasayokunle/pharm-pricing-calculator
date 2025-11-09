# ==============================================================
# Pharmacy Department Pricing Sensitivity App (OPEX-adjusted)
# ExCare Services Limited – by Ayokunle Thomas
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing Sensitivity", layout="wide")

# --- HEADER ---
st.title("💊 Pharmacy Department Pricing Sensitivity Dashboard")
st.caption("Understand how volume and price markup changes affect profitability at the department level.")

# --- DATA SOURCE ---
sheet_url = "https://docs.google.com/spreadsheets/d/1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4/export?format=csv&gid=876068924"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

required_cols = ["departments", "revenue", "cogs", "volume sold", "opex%"]
if not all(col in df.columns for col in required_cols):
    st.error(f"The sheet must include: {', '.join(required_cols)}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Simulation Controls")

department = st.sidebar.selectbox("Select Department", df["departments"].unique())
volume_growth = st.sidebar.slider("Projected Volume Growth (%)", -50, 300, 0, 10)
markup = st.sidebar.slider("Proposed Markup Multiplier (×)", 0.8, 3.0, 1.2, 0.05)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity to Volume (%)", 0, 100, 15, 5)
margin_threshold = st.sidebar.number_input("Minimum Acceptable Margin (%)", 0.0, 100.0, 20.0)

# --- GET DEPARTMENT DATA ---
data = df[df["departments"] == department].iloc[0]
revenue = data["revenue"]
cogs = data["cogs"]
volume = data["volume sold"]
opex_percent = data["opex%"] / 100

# --- BASE VALUES ---
price_per_unit = revenue / volume
cost_per_unit = cogs / volume
current_markup = price_per_unit / cost_per_unit
current_opex = opex_percent * revenue
current_profit = revenue - cogs - current_opex
current_margin = (current_profit / revenue) * 100 if revenue > 0 else 0

# --- PROPOSED SCENARIO ---
new_volume = volume * (1 + volume_growth / 100)
new_price = cost_per_unit * markup
new_revenue = new_volume * new_price
new_cogs = new_volume * cost_per_unit

# OPEX is semi-fixed: 70% fixed, 30% variable
opex_fixed_ratio = 0.7
opex_variable_ratio = 0.3
new_opex = current_opex * (
    opex_fixed_ratio + opex_variable_ratio * (1 + opex_sensitivity / 100) * (new_volume / volume)
)

new_profit = new_revenue - new_cogs - new_opex
new_margin = (new_profit / new_revenue) * 100 if new_revenue > 0 else 0

# --- ALERT BOX ---
if new_margin < margin_threshold:
    st.error(f"⚠️ Margin drops to {new_margin:.1f}%, below target ({margin_threshold}%)")
elif new_margin >= margin_threshold + 5:
    st.success(f"✅ Margin improves to {new_margin:.1f}%, comfortably above target.")
else:
    st.info(f"ℹ️ Margin is {new_margin:.1f}%, near the threshold ({margin_threshold}%).")

# --- COMPARISON TABLE ---
st.subheader(f"📊 Department Analysis: {department}")

summary = pd.DataFrame({
    "Metric": ["Revenue (₦)", "COGS (₦)", "OPEX (₦)", "Net Profit (₦)", "Net Margin (%)", "Markup (×)", "Volume Sold"],
    "Current": [revenue, cogs, current_opex, current_profit, current_margin, current_markup, volume],
    "Proposed": [new_revenue, new_cogs, new_opex, new_profit, new_margin, markup, new_volume]
})

summary["Change (%)"] = ((summary["Proposed"] - summary["Current"]) / summary["Current"]) * 100
summary["Change (%)"] = summary["Change (%)"].apply(lambda x: f"{x:.1f}%" if np.isfinite(x) else "–")

st.dataframe(
    summary.style.format({
        "Current": "₦{:,.0f}",
        "Proposed": "₦{:,.0f}",
        "Change (%)": "{}"
    })
)

# --- INSIGHT ---
change = new_margin - current_margin
direction = "increase" if change > 0 else "drop"

st.markdown(f"""
### 💡 Insight Summary  
At a proposed markup of **×{markup:.2f}** and a projected volume change of **{volume_growth}%**,  
**{department}** sees net margin move from **{current_margin:.1f}% → {new_margin:.1f}%**,  
representing a **{abs(change):.1f}% {direction}** in profitability after adjusting for realistic OPEX behavior.
""")

# --- FOOTER ---
st.markdown("---")
st.caption("💡 *OPEX now models 70% fixed and 30% variable costs for better realism, subject to change from financial figures.*")
st.markdown("<p style='text-align:center;'>Created by <b>Ayokunle Thomas</b> – Data Scientist | ExCare Services Limited © 2025</p>", unsafe_allow_html=True)
