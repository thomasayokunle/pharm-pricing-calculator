# ==============================================================
# Pharmacy Pricing Calculator (Using Google Sheet)
# ==============================================================

import streamlit as st
import pandas as pd
import math
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="ExCare Pharmacy Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Pharmacy Pricing Calculator")
st.markdown("""
This calculator estimates and compares pricing scenarios for our laboratory tests.  
It helps us understand how Pricing, OPEX, and Volume affect Profitability.
""")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4"

def load_sheet(sheet_name):
    """Loads a Google Sheet as CSV and converts numeric columns safely."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

Pharm = st.sidebar.selectbox("Select Department", ["REFILL", "VACCINE"])
df = load_sheet(Pharm)

selected_product = st.sidebar.selectbox("Select Product", df["product name"].unique())
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 5.0, 1.5, 0.1)
custom_price = st.sidebar.number_input("Or Enter Proposed Price (₦)", min_value=0.0, value=0.0, step=500.0)
base_volume = st.sidebar.number_input("Base Volume", min_value=1, value=20, step=1)
volume_growth_rate = st.sidebar.slider("Expected Volume Growth (%)", 0, 200, 0, 5)
opex_increase_rate = st.sidebar.slider("OPEX Volume Sensitivity (%)", 0, 100, 0, 5)
min_margin_percent = st.sidebar.slider("Minimum Profit Margin (%)", 0, 50, 20, 1)

# --- FETCH TEST DETAILS ---
test = df[df["product name"] == selected_product].iloc[0]
current_price = float(test["current price"])
cogs_per_test = float(test["cogs"])

# --- HELPER FUNCTION ---
def round100(value):
    try:
        return int(math.ceil(value / 100.0)) * 100
    except:
        return 0

# --- PRICE CALCULATIONS ---
proposed_price = custom_price if custom_price > 0 else cogs_per_test * markup
proposed_price = round100(proposed_price)

# --- CURRENT SCENARIO ---
current_revenue = current_price
current_cogs = cogs_per_test
current_gross_profit = current_revenue - current_cogs

# --- OPEX % HANDLING ---
if "opex%" in df.columns:
    opex_percent = df["opex%"].dropna().iloc[0] / 100
else:
    opex_percent = 0.25  # fallback default (25%)

base_opex = opex_percent * current_revenue
current_ebitda = current_gross_profit - base_opex
current_margin = round((current_ebitda / current_revenue) * 100, 1) if current_revenue != 0 else 0

# --- APPLY VOLUME GROWTH ---
proposed_volume = base_volume * (1 + volume_growth_rate / 100)

# --- PROPOSED SCENARIO ---
proposed_revenue = proposed_price * proposed_volume
proposed_cogs = cogs_per_test * proposed_volume
proposed_gross_profit = proposed_revenue - proposed_cogs

opex_factor = 1 + (opex_increase_rate / 100)
proposed_opex = (opex_percent * proposed_revenue) * (1 + 0.1 * math.log1p(proposed_volume / 50)) * opex_factor

proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1) if proposed_revenue != 0 else 0

# --- DYNAMIC MINIMUM MARGIN CHECK ---
min_required_price = (proposed_cogs + proposed_opex) / (1 - (min_margin_percent / 100)) / proposed_volume
if proposed_price < min_required_price:
    proposed_price = round100(min_required_price)
    proposed_revenue = proposed_price * proposed_volume
    proposed_gross_profit = proposed_revenue - proposed_cogs
    proposed_ebitda = proposed_gross_profit - proposed_opex
    proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1)
    price_note = f"Adjusted upward to maintain ≥ {min_margin_percent}% profit margin"
else:
    price_note = f"Within target margin range (≥ {min_margin_percent}%)"

# --- ROUND KEY FIGURES ---
def r100(x): return round100(x)
current_revenue, proposed_revenue = r100(current_revenue), r100(proposed_revenue)
current_cogs, proposed_cogs = r100(current_cogs), r100(proposed_cogs)
base_opex, proposed_opex = r100(base_opex), r100(proposed_opex)
current_ebitda, proposed_ebitda = r100(current_ebitda), r100(proposed_ebitda)

# --- COMPARISON TABLE ---
comparison = pd.DataFrame({
    "Metric": [
        "Volume (Units)", "Revenue (₦)", "COGS (₦)", "Gross Profit (₦)",
        "OPEX (₦)", "EBITDA (₦)", "Profit Margin (%)"
    ],
    "Current": [
        base_volume, current_revenue, current_cogs, current_gross_profit,
        base_opex, current_ebitda, current_margin
    ],
    "Proposed": [
        proposed_volume, proposed_revenue, proposed_cogs, proposed_gross_profit,
        proposed_opex, proposed_ebitda, proposed_margin
    ],
    "Change": [
        proposed_volume - base_volume,
        proposed_revenue - current_revenue,
        proposed_cogs - current_cogs,
        proposed_gross_profit - current_gross_profit,
        proposed_opex - base_opex,
        proposed_ebitda - current_ebitda,
        round(proposed_margin - current_margin, 1)
    ]
})

# --- DISPLAY TABLE ---
st.subheader(f"Pricing Simulation: {selected_product}")
st.dataframe(
    comparison.style.format({
        "Current": "{:,.0f}",
        "Proposed": "{:,.0f}",
        "Change": "{:,.0f}"
    }),
    use_container_width=True
)

# --- SUMMARY ---
st.markdown(f"""
**Summary Insight**  
At a proposed price of **₦{proposed_price:,.0f}**, volume grows by **{volume_growth_rate}%** to **{proposed_volume:.0f} units**.  
EBITDA margin moves from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**.  
OPEX rises with sensitivity **{opex_increase_rate}%**, from ₦{base_opex:,.0f} to ₦{proposed_opex:,.0f}.  
{price_note}
""")
st.caption("*Volume growth simulates how scaling up sales affects profitability and cost behavior.*")

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
