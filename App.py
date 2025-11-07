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
This calculator estimates and compares pricing scenarios for Pharmacy Departments.  
It helps you understand how markup, OPEX, and volume growth affect profitability.
""")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4"
SHEET_NAME = "PHARMACY"

def load_sheet(sheet_name):
    """Loads a Google Sheet as CSV and cleans numeric fields."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- LOAD DATA ---
df = load_sheet(SHEET_NAME)

# --- CLEAN OPEX COLUMN ---
if "OPEX%" in df.columns:
    df["OPEX%"] = pd.to_numeric(df["OPEX%"], errors="coerce")
    if df["OPEX%"].notna().any():
        df["OPEX%"] = df["OPEX%"].fillna(df["OPEX%"].mean())
    else:
        df["OPEX%"] = 25.0
else:
    df["OPEX%"] = 25.0

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

# Select from the DEPARTMENTS column
department = st.sidebar.selectbox("Select Department", df["DEPARTMENTS"].unique())
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 5.0, 1.5, 0.1)
volume_growth = st.sidebar.slider("Projected Volume Growth (%)", -50, 200, 20, 5)
opex_increase_rate = st.sidebar.slider("OPEX Volume Sensitivity (%)", 0, 100, 10, 5)

# --- FILTER SELECTED DEPARTMENT ---
dept_data = df[df["DEPARTMENTS"] == department].iloc[0]

revenue = float(dept_data["REVENUE"])
cogs = float(dept_data["COGS"])
opex_percent = float(dept_data["OPEX%"]) / 100

# --- HELPER FUNCTION ---
def round100(value):
    try:
        return int(math.ceil(value / 100.0)) * 100
    except:
        return 0

# --- CURRENT SCENARIO ---
current_revenue = revenue
current_cogs = cogs
current_gross_profit = current_revenue - current_cogs
current_opex = opex_percent * current_revenue
current_ebitda = current_gross_profit - current_opex
current_margin = (current_ebitda / current_revenue) * 100 if current_revenue else 0
current_net_profit = current_ebitda * 0.85  # post-tax (15% tax assumption)

# --- PROPOSED SCENARIO ---
proposed_revenue = current_revenue * markup * (1 + volume_growth / 100)
proposed_cogs = current_cogs * (1 + volume_growth / 100)
proposed_gross_profit = proposed_revenue - proposed_cogs

opex_factor = 1 + (opex_increase_rate / 100)
proposed_opex = opex_percent * proposed_revenue * opex_factor
proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = (proposed_ebitda / proposed_revenue) * 100 if proposed_revenue else 0
proposed_net_profit = proposed_ebitda * 0.85

# --- ROUND VALUES ---
def r100(x): return round100(x)
current_revenue, proposed_revenue = r100(current_revenue), r100(proposed_revenue)
current_cogs, proposed_cogs = r100(current_cogs), r100(proposed_cogs)
current_opex, proposed_opex = r100(current_opex), r100(proposed_opex)
current_ebitda, proposed_ebitda = r100(current_ebitda), r100(proposed_ebitda)
current_net_profit, proposed_net_profit = r100(current_net_profit), r100(proposed_net_profit)

# --- COMPARISON TABLE ---
comparison = pd.DataFrame({
    "Metric": [
        "Revenue (₦)", "COGS (₦)", "Gross Profit (₦)",
        "OPEX (₦)", "EBITDA (₦)", "Profit Margin (%)", "Net Profit (₦)"
    ],
    "Current": [
        current_revenue, current_cogs, current_gross_profit,
        current_opex, current_ebitda, round(current_margin, 1), current_net_profit
    ],
    "Proposed": [
        proposed_revenue, proposed_cogs, proposed_gross_profit,
        proposed_opex, proposed_ebitda, round(proposed_margin, 1), proposed_net_profit
    ],
    "Change": [
        proposed_revenue - current_revenue,
        proposed_cogs - current_cogs,
        proposed_gross_profit - current_gross_profit,
        proposed_opex - current_opex,
        proposed_ebitda - current_ebitda,
        round(proposed_margin - current_margin, 1),
        proposed_net_profit - current_net_profit
    ]
})

# --- DISPLAY TABLE ---
st.subheader(f"Pricing Simulation: {department}")
st.dataframe(
    comparison.style.format({
        "Current": "{:,.0f}",
        "Proposed": "{:,.0f}",
        "Change": "{:,.0f}"
    }),
    use_container_width=True
)

# --- ANALYTICAL SUMMARY ---
st.markdown(f"""
**Summary Insight**  
At a markup of **×{markup:.1f}**, and **{volume_growth}%** projected growth,  
revenue and COGS scale accordingly for the **{department}** department.  
EBITDA margin shifts from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**,  
while **Net Profit** rises from **₦{current_net_profit:,.0f}** to **₦{proposed_net_profit:,.0f}**.  
OPEX increases by **{opex_increase_rate}%** sensitivity as volume grows.
""")
st.caption("💡 *Net Profit = EBITDA less 15% tax; Opex Sensitivity models operational scaling.*")

# --- VOLUME SIMULATION CHART ---
st.subheader("Volume Projection (EBITDA Impact)")

projection = pd.DataFrame({
    "Volume Growth %": range(-50, 201, 10),
    "EBITDA (₦)": [
        (revenue * markup * (1 + v/100) - cogs * (1 + v/100) -
         (opex_percent * revenue * markup * (1 + v/100) * (1 + opex_increase_rate / 100)))
        for v in range(-50, 201, 10)
    ]
})
st.line_chart(projection.set_index("Volume Growth %"))

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
