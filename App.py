# ==============================================================
# Pharmacy Department Pricing Calculator
# Mirrors the Lab Calculator logic — Department-level view
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Pharmacy Pricing Calculator")
st.caption("_Estimate profitability and EBITDA across pharmacy departments_")

# --- LOAD DATA ---
sheet_url = "https://docs.google.com/spreadsheets/d/1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4/export?format=csv"
df = pd.read_csv(sheet_url)

# --- CLEANUP ---
df.columns = df.columns.str.strip().str.lower()

# Ensure numeric columns
for col in ["revenue", "cogs", "opex%"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# --- SIDEBAR CONFIG ---
st.sidebar.header("Configuration")

# Department selection
if "departments" in df.columns:
    department = st.sidebar.selectbox("Select Department", df["departments"].dropna().unique())
else:
    st.error("❌ 'departments' column not found in the Google Sheet.")
    st.stop()

# Get base OPEX from the sheet (if available)
if "opex%" in df.columns and not df["opex%"].dropna().empty:
    base_opex_percent = df["opex%"].dropna().iloc[0]
else:
    base_opex_percent = 10  # fallback

# Allow manual OPEX adjustment
opex_percent = st.sidebar.slider("Adjust OPEX (%)", 0.0, 50.0, float(base_opex_percent), step=0.5)
opex_increase_rate = st.sidebar.slider("OPEX Sensitivity (%)", 0.0, 50.0, 10.0, step=1.0)

# Price and volume inputs
proposed_price = st.sidebar.number_input("Proposed Price (₦)", min_value=0.0, step=100.0, value=1000.0)
volume = st.sidebar.number_input("Volume Sold", min_value=1, step=1, value=100)

# --- DATA SELECTION ---
df_selected = df[df["departments"] == department].iloc[0]
revenue = df_selected["revenue"]
cogs = df_selected["cogs"]

# --- CALCULATIONS ---
base_opex = (opex_percent / 100) * revenue
proposed_opex = base_opex * (1 + (opex_increase_rate / 100))

# Profitability
gross_profit = revenue - cogs
ebitda = gross_profit - base_opex

# Proposed values
proposed_revenue = proposed_price * volume
proposed_cogs = cogs * (proposed_revenue / revenue) if revenue > 0 else 0
proposed_gross_profit = proposed_revenue - proposed_cogs
proposed_ebitda = proposed_gross_profit - proposed_opex

# Margins
current_margin = (ebitda / revenue) * 100 if revenue > 0 else 0
proposed_margin = (proposed_ebitda / proposed_revenue) * 100 if proposed_revenue > 0 else 0
net_change = proposed_margin - current_margin

# --- DISPLAY ---
st.subheader(f"Department: {department}")
st.dataframe(df.style.format({"revenue": "₦{:,.0f}", "cogs": "₦{:,.0f}", "opex%": "{:.1f}%"}))

# --- SUMMARY BLOCK ---
st.markdown(f"""
**Summary Insight**  
At a proposed price of **₦{proposed_price:,.0f}**, revenue and COGS scale with **{volume} units**.  
EBITDA margin improved from **{current_margin:.1f}%** to **{proposed_margin:.1f}%** 
(**{net_change:+.1f}% change**).  
OPEX increased by **{opex_increase_rate}%** for higher volumes, from 
₦{base_opex:,.0f} to ₦{proposed_opex:,.0f}.  

**Net Profit Margin:** **{proposed_margin:.1f}%**
""")

st.caption("💡 *Opex Sensitivity controls how much operating cost grows as volume increases.*")

# --- FOOTER LINKS ---
st.markdown("""
<hr style="border: 0.5px solid #ddd;">
<div style='text-align: center; font-size: 13px; font-style: italic; color: #666;'>
<a href='https://www.linkedin.com/in/ayokunle-thomas' target='_blank' style='color: #888; text-decoration: none;'>LinkedIn</a> |
<a href='https://github.com/ThomasAyokunle' target='_blank' style='color: #888; text-decoration: none;'>GitHub</a>
</div>
<style>
a:hover { color: #4b9cea !important; }
</style>
""", unsafe_allow_html=True)
