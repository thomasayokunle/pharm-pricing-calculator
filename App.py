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
This calculator estimates and compares pricing scenarios for our pharmacy products.  
It helps us understand how Pricing, OPEX, and Volume affect Profitability.
""")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4"

def load_sheet(sheet_name):
    """Loads a Google Sheet as CSV and converts numeric columns safely."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    # Standardize column names to title case and strip whitespace
    df.columns = df.columns.str.strip().str.title()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

pharm = st.sidebar.selectbox("Select Department", ["REFILL", "VACCINE"])
df = load_sheet(pharm)

# Display available columns for debugging (optional - can remove later)
# st.sidebar.write("Available columns:", list(df.columns))

selected_product = st.sidebar.selectbox("Select Product", df["Product Name"].unique())
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 5.0, 1.5, 0.05)
custom_price = st.sidebar.number_input("Or Enter Proposed Price (₦)", min_value=0.0, value=0.0, step=500.0)
volume = st.sidebar.slider("Projected Volume", 0, 500, 20, 5)
opex_increase_rate = st.sidebar.slider("OPEX Volume Sensitivity (%)", 0, 100, 0, 5)

# 🔸 Adjustable minimum margin threshold
min_margin_percent = st.sidebar.slider("Minimum Profit Margin (%)", 0, 50, 20, 1)

# --- FETCH PRODUCT DETAILS ---
product = df[df["Product Name"] == selected_product].iloc[0]
current_price = float(product["Current Price"])
cogs_per_product = float(product["Cogs"])

# --- HELPER FUNCTION ---
def round50(value):
    try:
        return int(round(value / 50.0)) * 50
    except:
        return 0

# --- PRICE CALCULATIONS ---
proposed_price = custom_price if custom_price > 0 else cogs_per_product * markup
proposed_price = round50(proposed_price)

# --- CURRENT SCENARIO ---
current_revenue = current_price
current_cogs = cogs_per_product
current_gross_profit = current_revenue - current_cogs

# --- OPEX % HANDLING ---
# If OPEX % column exists, read the first non-empty value and apply it.
if "Opex%" in df.columns or "Opex %" in df.columns:
    opex_col = "Opex%" if "Opex%" in df.columns else "Opex %"
    opex_percent = df[opex_col].dropna().iloc[0] / 100
else:
    opex_percent = 0.25  # fallback default (25%)

base_opex = opex_percent * current_revenue

current_ebitda = current_gross_profit - base_opex
current_margin = round((current_ebitda / current_revenue) * 100, 1) if current_revenue != 0 else 0

# --- PROPOSED SCENARIO ---
proposed_revenue = proposed_price * volume
proposed_cogs = cogs_per_product * volume
proposed_gross_profit = proposed_revenue - proposed_cogs

# Apply the same opex_percent logic with sensitivity and volume scaling
opex_factor = 1 + (opex_increase_rate / 100)
proposed_opex = (opex_percent * proposed_revenue) * (1 + 0.1 * math.log1p(volume / 50)) * opex_factor

proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1) if proposed_revenue != 0 else 0

# --- MINIMUM MARGIN CHECK (Dynamic) ---
min_required_price = (proposed_cogs + proposed_opex) / (1 - (min_margin_percent / 100)) / volume if volume > 0 else 0
if proposed_price < min_required_price:
    proposed_price = round50(min_required_price)
    proposed_revenue = proposed_price * volume
    proposed_gross_profit = proposed_revenue - proposed_cogs
    proposed_ebitda = proposed_gross_profit - proposed_opex
    proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1) if proposed_revenue != 0 else 0
    price_note = f"⚠️ Price adjusted to ₦{proposed_price:,.0f} to maintain ≥ {min_margin_percent}% profit margin"
else:
    price_note = f"✅ Within target margin range (≥ {min_margin_percent}%)"

# --- ROUND KEY FIGURES ---
def r50(x): return round50(x)
current_revenue, proposed_revenue = r50(current_revenue), r50(proposed_revenue)
current_cogs, proposed_cogs = r50(current_cogs), r50(proposed_cogs)
base_opex, proposed_opex = r50(base_opex), r50(proposed_opex)
current_ebitda, proposed_ebitda = r50(current_ebitda), r50(proposed_ebitda)

# --- COMPARISON TABLE ---
comparison = pd.DataFrame({
    "Metric": [
        "Revenue (₦)", "COGS (₦)", "Gross Profit (₦)",
        "OPEX (₦)", "EBITDA (₦)", "Profit Margin (%)"
    ],
    "Current": [
        current_revenue, current_cogs, current_gross_profit,
        base_opex, current_ebitda, current_margin
    ],
    "Proposed": [
        proposed_revenue, proposed_cogs, proposed_gross_profit,
        proposed_opex, proposed_ebitda, proposed_margin
    ],
    "Change": [
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

# Apply numeric formatting only to numeric columns
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
At a proposed price of **₦{proposed_price:,.0f}**, Revenue and COGS scale with **{volume} units**.  
EBITDA margin moves from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**.  
OPEX increases by **{opex_increase_rate}%** sensitivity for higher volumes, rising from 
₦{base_opex:,.0f} to ₦{proposed_opex:,.0f}.  

{price_note}
""")
st.caption("💡 *OPEX Sensitivity controls how much operating cost grows as volume increases.*")

# --- VOLUME SIMULATION (EBITDA vs Volume) ---
st.subheader("Volume Projection (EBITDA Impact)")

projection = pd.DataFrame({
    "Volume": range(1, volume + 1),
    "Total Revenue": [proposed_price * v for v in range(1, volume + 1)],
    "Total EBITDA": [
        (proposed_price * v - cogs_per_product * v -
         opex_percent * proposed_price * v * (1 + 0.1 * math.log1p(v / 50)) * (1 + (opex_increase_rate / 100)))
        for v in range(1, volume + 1)
    ]
})
st.line_chart(projection.set_index("Volume"))

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
        color: #1f77b4; /* Subtle blue hover */
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
