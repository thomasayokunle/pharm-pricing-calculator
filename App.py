# ==============================================================
# Pharmacy Department Pricing Calculator
# Mirrors Lab Calculator logic – Department-level summary
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Pharmacy Pricing Calculator")
st.markdown("""
This calculator estimates and compares profitability for each pharmacy department.  
It helps evaluate how pricing, OPEX, and volume affect EBITDA and margins.
""")

# --- LOAD DATA FROM GOOGLE SHEET ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4/export?format=csv"
df = pd.read_csv(SHEET_URL)

# --- CLEANUP ---
df.columns = df.columns.str.strip().str.lower()

# Ensure numeric columns
for col in ["revenue", "cogs", "volume sold", "opex%"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

if "departments" not in df.columns:
    st.error("The sheet must include a 'Departments' column.")
    st.stop()

department = st.sidebar.selectbox("Select Department", df["departments"].dropna().unique())

# Get OPEX% from the sheet (first non-empty value)
if "opex%" in df.columns and not df["opex%"].dropna().empty:
    base_opex_percent = df["opex%"].dropna().iloc[0]
else:
    base_opex_percent = 10  # fallback default

# Editable OPEX adjustment
opex_percent = st.sidebar.slider("OPEX (%)", 0.0, 50.0, float(base_opex_percent), step=0.5)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity (%)", 0.0, 50.0, 10.0, step=1.0)

# Proposed price input
proposed_price = st.sidebar.number_input("Proposed Price (₦)", min_value=0.0, step=100.0, value=1000.0)

# --- SELECTED DEPARTMENT DATA ---
df_dept = df[df["departments"] == department].iloc[0]

revenue = df_dept["revenue"]
cogs = df_dept["cogs"]
volume = df_dept["volume sold"]

# --- CURRENT SCENARIO ---
opex = (opex_percent / 100) * revenue
gross_profit = revenue - cogs
ebitda = gross_profit - opex
current_margin = (ebitda / revenue) * 100 if revenue != 0 else 0

# --- PROPOSED SCENARIO ---
proposed_revenue = proposed_price * volume
proposed_cogs = cogs * (proposed_revenue / revenue) if revenue > 0 else 0
proposed_opex = (opex_percent / 100) * proposed_revenue * (1 + (opex_sensitivity / 100))
proposed_gross_profit = proposed_revenue - proposed_cogs
proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = (proposed_ebitda / proposed_revenue) * 100 if proposed_revenue != 0 else 0
margin_change = proposed_margin - current_margin

# --- COMPARISON TABLE ---
comparison = pd.DataFrame({
    "Metric": ["Revenue (₦)", "COGS (₦)", "Gross Profit (₦)", "OPEX (₦)", "EBITDA (₦)", "EBITDA Margin (%)"],
    "Current": [revenue, cogs, gross_profit, opex, ebitda, current_margin],
    "Proposed": [proposed_revenue, proposed_cogs, proposed_gross_profit, proposed_opex, proposed_ebitda, proposed_margin],
    "Change": [
        proposed_revenue - revenue,
        proposed_cogs - cogs,
        proposed_gross_profit - gross_profit,
        proposed_opex - opex,
        proposed_ebitda - ebitda,
        margin_change
    ]
})

# --- DISPLAY ---
st.subheader(f"Department Overview: {department}")
st.dataframe(
    comparison.style.format({
        "Current": "₦{:,.0f}",
        "Proposed": "₦{:,.0f}",
        "Change": "₦{:,.0f}"
    }),
    use_container_width=True
)

# --- ANALYTICAL SUMMARY ---
st.markdown(f"""
**Summary Insight**  
At a proposed price of **₦{proposed_price:,.0f}**, revenue and COGS scale with **{int(volume)} units sold**.  
EBITDA margin moves from **{current_margin:.1f}%** to **{proposed_margin:.1f}%** (**{margin_change:+.1f}% change**).  
OPEX grows from ₦{opex:,.0f} to ₦{proposed_opex:,.0f} under a **{opex_sensitivity}%** sensitivity setting.  
""")
st.info(f"**Net Profit Margin:** {proposed_margin:.1f}%")

st.caption("*OPEX Sensitivity adjusts how operating cost grows with increased revenue or volume.*")

# --- VISUAL INSIGHT ---
projection = pd.DataFrame({
    "Volume": range(1, int(volume) + 1),
    "Total Revenue": [proposed_price * v for v in range(1, int(volume) + 1)],
    "Total EBITDA": [
        (proposed_price * v - (cogs / volume) * v -
         ((opex_percent / 100) * proposed_price * v * (1 + (opex_sensitivity / 100))))
        for v in range(1, int(volume) + 1)
    ]
})
st.subheader("EBITDA Impact by Volume")
st.line_chart(projection.set_index("Volume"))

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; font-size:13px; font-style:italic; color:#888;'>
        Created by <b>Ayokunle Thomas</b> — Data Scientist<br>
        <a href='https://www.linkedin.com/in/ayokunle-thomas' target='_blank' style='color:#888;'>LinkedIn</a> |
        <a href='https://github.com/ThomasAyokunle' target='_blank' style='color:#888;'>GitHub</a>
    </div>
    <style>
    a:hover { color: #4b9cea !important; }
    </style>
    """,
    unsafe_allow_html=True
)
