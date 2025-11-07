# ==============================================================
# Pharmacy Pricing Calculator (Google Sheet Integrated)
# ==============================================================

import streamlit as st
import pandas as pd
import math
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="D-Rock Pharmacy Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Pharmacy Pricing Calculator")
st.markdown("""
This calculator estimates and compares pricing scenarios for pharmacy departments.  
It helps you understand how pricing, OPEX, and volume affect overall profitability.
""")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4"  # your live sheet ID

def load_sheet(sheet_name):
    """Loads a Google Sheet as CSV and converts numeric columns safely."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

department = st.sidebar.selectbox("Select Department", ["PHARMACY"])
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 5.0, 1.5, 0.1)
volume_growth = st.sidebar.slider("Volume Growth (%)", -50, 200, 0, 10)
opex_increase_rate = st.sidebar.slider("OPEX Sensitivity (%)", 0, 100, 10, 5)

# --- LOAD DATA ---
df = load_sheet(department)

required_cols = ["DEPARTMENT", "REVENUE", "COGS", "OPEX%"]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# --- GLOBAL CALCULATIONS ---
df["OPEX%"] = df["OPEX%"].fillna(df["OPEX%"].mean())
df["OPEX"] = df["REVENUE"] * (df["OPEX%"] / 100)
df["GROSS_PROFIT"] = df["REVENUE"] - df["COGS"]
df["EBITDA"] = df["GROSS_PROFIT"] - df["OPEX"]
df["MARGIN (%)"] = (df["EBITDA"] / df["REVENUE"]) * 100

# Simulate Markup, Volume, and OPEX Sensitivity
df["PROPOSED_REVENUE"] = df["REVENUE"] * markup * (1 + (volume_growth / 100))
df["PROPOSED_COGS"] = df["COGS"] * (1 + (volume_growth / 100))
df["PROPOSED_OPEX"] = (df["PROPOSED_REVENUE"] * (df["OPEX%"] / 100)) * (1 + (opex_increase_rate / 100))
df["PROPOSED_GROSS_PROFIT"] = df["PROPOSED_REVENUE"] - df["PROPOSED_COGS"]
df["PROPOSED_EBITDA"] = df["PROPOSED_GROSS_PROFIT"] - df["PROPOSED_OPEX"]
df["PROPOSED_MARGIN (%)"] = (df["PROPOSED_EBITDA"] / df["PROPOSED_REVENUE"]) * 100

# --- KPI SUMMARY ---
total_revenue = df["PROPOSED_REVENUE"].sum()
total_ebitda = df["PROPOSED_EBITDA"].sum()
avg_margin = round(df["PROPOSED_MARGIN (%)"].mean(), 1)
total_departments = len(df)

st.subheader(f"{department} Summary")
kpi_cols = st.columns(4)
kpi_cols[0].metric("Departments", f"{total_departments}")
kpi_cols[1].metric("Total Revenue (₦)", f"{total_revenue:,.0f}")
kpi_cols[2].metric("Total EBITDA (₦)", f"{total_ebitda:,.0f}")
kpi_cols[3].metric("Average Margin (%)", f"{avg_margin:.1f}%")

# --- DATA TABLE ---
st.subheader("Department Overview")
preview = df[[
    "DEPARTMENT", "REVENUE", "COGS", "OPEX%", "EBITDA", "MARGIN (%)",
    "PROPOSED_REVENUE", "PROPOSED_EBITDA", "PROPOSED_MARGIN (%)"
]]
st.dataframe(
    preview.style.format({
        "REVENUE": "{:,.0f}",
        "COGS": "{:,.0f}",
        "EBITDA": "{:,.0f}",
        "MARGIN (%)": "{:,.1f}",
        "PROPOSED_REVENUE": "{:,.0f}",
        "PROPOSED_EBITDA": "{:,.0f}",
        "PROPOSED_MARGIN (%)": "{:,.1f}"
    }),
    use_container_width=True
)

# --- ANALYTICAL SUMMARY BLOCK ---
current_margin = df["MARGIN (%)"].mean()
proposed_margin = df["PROPOSED_MARGIN (%)"].mean()
net_change = proposed_margin - current_margin
base_opex = df["OPEX"].sum()
proposed_opex = df["PROPOSED_OPEX"].sum()

st.markdown(f"""
**Summary Insight**  
With a markup of **×{markup:.1f}** and **{volume_growth}%** volume change,  
EBITDA margin improved from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**  
(**{net_change:+.1f}% change** overall).  
OPEX increased by **{opex_increase_rate}%** for higher volumes, from  
₦{base_opex:,.0f} to ₦{proposed_opex:,.0f}.  

**Net Profit Margin:** **{proposed_margin:.1f}%**, reflecting overall profitability after OPEX adjustments.  
""")

st.caption("💡 *Opex Sensitivity controls how much operating cost grows as volume increases.*")

# --- EBITDA SENSITIVITY CHART ---
st.subheader("OPEX Sensitivity Projection")
projection = pd.DataFrame({
    "OPEX Sensitivity (%)": range(0, 101, 5),
    "EBITDA (₦)": [
        (df["PROPOSED_GROSS_PROFIT"].sum() - 
         ((df["PROPOSED_REVENUE"].sum() * (df["OPEX%"].mean() / 100)) * (1 + (r / 100))))
        for r in range(0, 101, 5)
    ]
})
st.line_chart(projection.set_index("OPEX Sensitivity (%)"))

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
