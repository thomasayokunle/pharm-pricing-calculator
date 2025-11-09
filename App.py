# ==============================================================
# Pharmacy Volume–Price & Margin Sensitivity Calculator
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing Calculator", layout="wide")
st.title("Pharmacy Volume–Price & Margin Sensitivity Calculator")
st.caption("Analyze how changes in markup and volume affect profitability per department, using live Google Sheet data.")

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

markup_base = st.sidebar.slider("Current Markup (×)", 1.0, 3.0, 1.5, 0.05)
markup_min = st.sidebar.slider("Min Markup to Test (×)", 1.0, markup_base, 1.2, 0.05)
markup_max = st.sidebar.slider("Max Markup to Test (×)", markup_base, 3.0, 2.0, 0.05)
volume_growth_range = st.sidebar.slider("Volume Growth Range (%)", -50, 300, (0, 200), 10)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity (%)", 0, 100, 10, 5)
min_margin = st.sidebar.number_input("Minimum Acceptable Margin (%)", 0.0, 100.0, 15.0, 0.5)

# --- LOAD SELECTED DEPARTMENT DATA ---
row = df[df["departments"] == department].iloc[0]
revenue = row["revenue"]
cogs = row["cogs"]
volume = row["volume sold"]
opex_percent = row["opex%"] / 100

base_price = revenue / volume if volume else 0
base_cost = cogs / volume if volume else 0

st.markdown(f"### 📊 Department Selected: **{department}**")
st.markdown(
    f"**Current Metrics:** Revenue ₦{revenue:,.0f}, COGS ₦{cogs:,.0f}, Volume {volume:,.0f}, OPEX {row['opex%']}%"
)

# --- SIMULATION ---
volume_growth_values = range(volume_growth_range[0], volume_growth_range[1] + 10, 10)
markup_values = np.arange(markup_min, markup_max + 0.01, 0.05)

simulation = []
for mg in markup_values:
    for vg in volume_growth_values:
        new_volume = volume * (1 + vg / 100)
        new_price = base_cost * mg
        new_revenue = new_price * new_volume
        new_cogs = base_cost * new_volume
        new_opex = (opex_percent * new_revenue) * (1 + opex_sensitivity / 100)
        ebitda = new_revenue - new_cogs - new_opex
        margin = (ebitda / new_revenue) * 100 if new_revenue > 0 else 0
        meets_threshold = margin >= min_margin
        simulation.append([mg, vg, new_revenue, ebitda, margin, meets_threshold])

simulation_df = pd.DataFrame(simulation, columns=["Markup", "Volume Growth (%)", "Revenue", "EBITDA", "EBITDA Margin (%)", "Meets Threshold"])

# --- ALERT BOX ---
safe_scenarios = simulation_df[simulation_df["Meets Threshold"]]

if not safe_scenarios.empty:
    lowest_safe_markup = safe_scenarios.groupby("Markup")["EBITDA Margin (%)"].mean().idxmin()
    st.success(
        f"✅ Profitability is safe — at least one markup–volume combination maintains "
        f"a margin above **{min_margin:.1f}%**.\n\n"
        f"🔹 Lowest safe markup: **{lowest_safe_markup:.2f}×**"
    )
else:
    st.error(
        f"🚨 All tested markup–volume combinations fall below your {min_margin:.1f}% minimum margin. "
        f"Consider increasing markup or reducing OPEX."
    )

# --- TABLE & CHART ---
styled_df = simulation_df.pivot_table(index="Volume Growth (%)", columns="Markup", values="EBITDA Margin (%)")

def highlight_margin(val):
    color = "#d4edda" if val >= min_margin else "#f8d7da"  # green for safe, red for risky
    return f"background-color: {color}"

st.dataframe(styled_df.style.applymap(highlight_margin), use_container_width=True)

chart_data = simulation_df.pivot(index="Volume Growth (%)", columns="Markup", values="EBITDA Margin (%)")
st.line_chart(chart_data)

# --- INSIGHT ---
best_combo = simulation_df.loc[simulation_df["EBITDA"].idxmax()]
st.info(
    f"📊 Best outcome at **{best_combo['Markup']:.2f}×** markup and "
    f"**{best_combo['Volume Growth (%)']:.0f}%** volume growth → "
    f"EBITDA margin **{best_combo['EBITDA Margin (%)']:.1f}%**."
)

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:14px;'>Created by <b>Ayokunle Thomas</b> – Data Analyst</p>",
    unsafe_allow_html=True,
)
st.caption("ExCare Services Pharmacy Department Pricing Calculator © 2025")
