# ==============================================================
# Pharmacy Department P&L Sensitivity App (All Departments)
# ExCare Services Limited – by Ayokunle Thomas
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing P&L Sensitivity", layout="wide")

# --- HEADER ---
st.title("Pharmacy Department Pricing & P&L Sensitivity Dashboard")
st.caption("Analyze how changes in markup, sales volume, and OPEX affect gross and net profitability by department.")

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
st.sidebar.header("⚙️ Scenario Controls")

department = st.sidebar.selectbox("Focus on Department (Optional)", ["All"] + list(df["departments"].unique()))
volume_growth = st.sidebar.slider("Projected Volume Growth (%)", -50, 300, 0, 10)
markup = st.sidebar.slider("Proposed Markup Multiplier (×)", 0.8, 3.0, 1.2, 0.05)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity to Volume (%)", 0, 100, 15, 5)
margin_threshold = st.sidebar.number_input("Minimum Acceptable Net Margin (%)", 0.0, 100.0, 20.0)

# --- BASE CALCULATIONS FOR ALL DEPARTMENTS ---
df["price_per_unit"] = df["revenue"] / df["volume sold"]
df["cost_per_unit"] = df["cogs"] / df["volume sold"]
df["current_gross_profit"] = df["revenue"] - df["cogs"]
df["current_opex"] = df["opex%"] / 100 * df["revenue"]
df["current_net_profit"] = df["current_gross_profit"] - df["current_opex"]
df["current_gross_margin"] = (df["current_gross_profit"] / df["revenue"]) * 100
df["current_net_margin"] = (df["current_net_profit"] / df["revenue"]) * 100

# --- SCENARIO CALCULATIONS ---
df["new_volume"] = df["volume sold"] * (1 + volume_growth / 100)
df["new_price"] = df["cost_per_unit"] * markup
df["new_revenue"] = df["new_volume"] * df["new_price"]
df["new_cogs"] = df["new_volume"] * df["cost_per_unit"]
df["new_gross_profit"] = df["new_revenue"] - df["new_cogs"]

# --- Semi-Fixed OPEX ---
opex_fixed_ratio = 0.7
opex_variable_ratio = 0.3
df["opex_fixed"] = df["current_opex"] * opex_fixed_ratio
df["opex_variable"] = df["current_opex"] * opex_variable_ratio
df["opex_per_unit_variable"] = df["opex_variable"] / df["volume sold"]
df["new_opex"] = df["opex_fixed"] + df["opex_per_unit_variable"] * df["new_volume"] * (1 + opex_sensitivity / 100)

df["new_net_profit"] = df["new_gross_profit"] - df["new_opex"]
df["new_gross_margin"] = (df["new_gross_profit"] / df["new_revenue"]) * 100
df["new_net_margin"] = (df["new_net_profit"] / df["new_revenue"]) * 100

# --- FILTER FOR FOCUS DEPARTMENT ---
if department != "All":
    df_display = df[df["departments"] == department]
else:
    df_display = df.copy()

# --- ALERTS PER DEPARTMENT ---
for _, row in df_display.iterrows():
    if row["new_net_margin"] < margin_threshold:
        st.error(f"{row['departments']}: Net Margin drops to {row['new_net_margin']:.1f}%, below target ({margin_threshold}%)")
    elif row["new_net_margin"] >= margin_threshold + 5:
        st.success(f"{row['departments']}: Net Margin improves to {row['new_net_margin']:.1f}%, comfortably above target.")
    else:
        st.info(f"{row['departments']}: Net Margin is {row['new_net_margin']:.1f}%, near the threshold ({margin_threshold}%).")

# --- COMPARISON TABLE ---
summary = pd.DataFrame({
    "Department": df_display["departments"],
    "Revenue (₦)": df_display["revenue"],
    "COGS (₦)": df_display["cogs"],
    "Gross Profit (₦)": df_display["current_gross_profit"],
    "OPEX (₦)": df_display["current_opex"],
    "Net Profit (₦)": df_display["current_net_profit"],
    "Volume Sold": df_display["volume sold"],
    "Proposed Revenue (₦)": df_display["new_revenue"],
    "Proposed COGS (₦)": df_display["new_cogs"],
    "Proposed Gross Profit (₦)": df_display["new_gross_profit"],
    "Proposed OPEX (₦)": df_display["new_opex"],
    "Proposed Net Profit (₦)": df_display["new_net_profit"],
    "Proposed Volume Sold": df_display["new_volume"]
})

summary["Change (%)"] = ((summary["Proposed Net Profit (₦)"] - summary["Net Profit (₦)"]) / summary["Net Profit (₦)"]) * 100
summary["Change (%)"] = summary["Change (%)"].apply(lambda x: f"{x:.1f}%" if np.isfinite(x) else "–")

st.subheader("Department P&L Comparison")
st.dataframe(summary.style.format({
    "Revenue (₦)": "{:,.0f}",
    "COGS (₦)": "{:,.0f}",
    "Gross Profit (₦)": "{:,.0f}",
    "OPEX (₦)": "{:,.0f}",
    "Net Profit (₦)": "{:,.0f}",
    "Proposed Revenue (₦)": "{:,.0f}",
    "Proposed COGS (₦)": "{:,.0f}",
    "Proposed Gross Profit (₦)": "{:,.0f}",
    "Proposed OPEX (₦)": "{:,.0f}",
    "Proposed Net Profit (₦)": "{:,.0f}",
    "Volume Sold": "{:,.0f}",
    "Proposed Volume Sold": "{:,.0f}"
}))

# --- FOOTER ---
st.markdown("---")
st.caption("*OPEX modeled as 70% fixed and 30% variable for accurate cost behavior.*")
st.markdown("<p style='text-align:center;'>Created by <b>Ayokunle Thomas</b> – Data Analyst | ExCare Services Limited © 2025</p>", unsafe_allow_html=True)
