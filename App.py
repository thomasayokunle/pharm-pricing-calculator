# ==============================================================
# Pharmacy Pricing Calculator (Google Sheet Integrated)
# ==============================================================

import streamlit as st
import pandas as pd
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Pharmacy Pricing Calculator")
st.markdown("""
This calculator estimates and compares pricing scenarios for pharmacy departments.  
It helps you visualize how price, cost, and OPEX adjustments affect profitability.
""")

# --- LOAD DATA ---
sheet_url = "https://docs.google.com/spreadsheets/d/1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4/export?format=csv"
df = pd.read_csv(sheet_url)

# --- CLEAN COLUMN NAMES ---
df.columns = df.columns.str.strip().str.lower()

required_cols = ["departments", "revenue", "cogs", "volume sold", "opex%"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"This sheet must include the following columns: {', '.join(required_cols)}")
    st.stop()

# --- CLEAN DATA ---
df["opex%"] = df["opex%"].fillna(df["opex%"].mean())
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
df["cogs"] = pd.to_numeric(df["cogs"], errors="coerce")
df["volume sold"] = pd.to_numeric(df["volume sold"], errors="coerce")

# --- SIDEBAR FILTERS ---
st.sidebar.header("⚙️ Calculator Settings")

department = st.sidebar.selectbox("Select Department", df["departments"].dropna().unique())

price_change = st.sidebar.slider("Proposed Price Change (%)", -20, 50, 10)
opex_adjustment = st.sidebar.slider("OPEX Adjustment (%)", -10, 20, 0)
volume_growth = st.sidebar.slider("Expected Volume Growth (%)", -20, 50, 10)

# --- DATA SELECTION ---
row = df[df["departments"] == department].iloc[0]
revenue = row["revenue"]
cogs = row["cogs"]
volume = row["volume sold"]
base_opex = row["opex%"]

# --- CALCULATIONS ---
current_margin = ((revenue - cogs - (revenue * base_opex / 100)) / revenue) * 100

proposed_revenue = revenue * (1 + price_change / 100) * (1 + volume_growth / 100)
proposed_cogs = cogs * (1 + volume_growth / 100)
proposed_opex = base_opex * (1 + opex_adjustment / 100)

proposed_margin = ((proposed_revenue - proposed_cogs - (proposed_revenue * proposed_opex / 100)) / proposed_revenue) * 100

# --- INSIGHTS ---
st.markdown("### 📊 Analytical Summary")
st.markdown(f"""
| Metric | Current | Proposed |
|:--|:--:|:--:|
| **Revenue (₦)** | ₦{revenue:,.0f} | ₦{proposed_revenue:,.0f} |
| **COGS (₦)** | ₦{cogs:,.0f} | ₦{proposed_cogs:,.0f} |
| **OPEX%** | {base_opex:.1f}% | {proposed_opex:.1f}% |
| **Net Profit Margin** | {current_margin:.1f}% | {proposed_margin:.1f}% |
""")

# --- SUMMARY NOTE ---
price_note = (
    "Profitability improves with price and volume growth."
    if proposed_margin > current_margin
    else "Profitability declines under the current scenario."
)

st.markdown(f"""
**Summary Insight**  
At a proposed price change of **{price_change}%** and volume growth of **{volume_growth}%**,  
the EBITDA margin moves from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**.  
OPEX is adjusted by **{opex_adjustment}%**, moving from **{base_opex:.1f}%** to **{proposed_opex:.1f}%**.  
{price_note}
""")

st.caption("*OPEX Adjustment reflects operational cost sensitivity as volume and pricing change.*")

# --- FOOTER ---
st.write("---")
st.caption("Pharmacy Pricing Calculator © 2025 ExCare Services Limited")
