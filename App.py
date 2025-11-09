# ==============================================================
# Pharmacy Department Pricing Sensitivity App
# ExCare Services Limited – by Ayokunle Thomas
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pharmacy Pricing Sensitivity", layout="wide")

# --- HEADER ---
st.title("💊 Pharmacy Department Pricing Sensitivity Dashboard")
st.caption("Analyze how changes in price markup and volume affect EBITDA and Net Margin across departments.")

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
st.sidebar.header("Simulation Controls")

department = st.sidebar.selectbox("Select Department", df["departments"].unique())

selected = df[df["departments"] == department].iloc[0]
revenue = selected["revenue"]
cogs = selected["cogs"]
volume = selected["volume sold"]
opex_percent = selected["opex%"]

# Derived metrics
price_per_unit = revenue / volume
cogs_per_unit = cogs / volume
current_markup = price_per_unit / cogs_per_unit
current_opex = (opex_percent / 100) * revenue
current_ebitda = revenue - cogs - current_opex
current_margin = (current_ebitda / revenue) * 100

# --- USER INPUTS ---
st.sidebar.markdown("---")
markup = st.sidebar.slider("Proposed Markup Multiplier (×)", 0.8, 3.0, float(current_markup), 0.05)
volume_growth = st.sidebar.slider("Projected Volume Growth (%)", -50, 300, 0, 10)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity to Volume (%)", 0, 100, 10, 5)
margin_threshold = st.sidebar.number_input("Minimum Acceptable Margin (%)", 0.0, 100.0, 20.0)

# --- CALCULATIONS ---
new_volume = volume * (1 + volume_growth / 100)
new_price = cogs_per_unit * markup
new_revenue = new_volume * new_price
new_cogs = new_volume * cogs_per_unit
new_opex = (opex_percent / 100) * new_revenue * (1 + opex_sensitivity / 100)
new_ebitda = new_revenue - new_cogs - new_opex
new_margin = (new_ebitda / new_revenue) * 100

# --- ALERT BOX ---
if new_margin >= margin_threshold:
    st.success(f"✅ Margin maintained at {new_margin:.1f}%, above target ({margin_threshold}%)")
else:
    st.error(f"⚠️ Margin drops to {new_margin:.1f}%, below target ({margin_threshold}%)")

# --- DEPARTMENT SUMMARY TABLE ---
st.subheader(f"📊 Department Analysis: {department}")

summary = pd.DataFrame({
    "Metric": [
        "Revenue (₦)",
        "COGS (₦)",
        "OPEX (₦)",
        "EBITDA (₦)",
        "EBITDA Margin (%)",
        "Markup (×)",
        "Volume Sold"
    ],
    "Current": [
        revenue,
        cogs,
        current_opex,
        current_ebitda,
        current_margin,
        current_markup,
        volume
    ],
    "Proposed": [
        new_revenue,
        new_cogs,
        new_opex,
        new_ebitda,
        new_margin,
        markup,
        new_volume
    ]
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
department **{department}** sees EBITDA margin move from **{current_margin:.1f}% → {new_margin:.1f}%**  
representing a **{abs(change):.1f}% {direction}** in profitability.
""")

# --- FOOTER ---
st.markdown("---")
st.caption("💡 *OPEX sensitivity shows how operating expenses change relative to revenue growth.*")
st.markdown("<p style='text-align:center;'>Created by <b>Ayokunle Thomas</b> – Data Scientist | ExCare Services Limited © 2025</p>", unsafe_allow_html=True)
