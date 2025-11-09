# --- VOLUME–PRICE IMPACT & MARGIN SIMULATION ---
st.subheader("Volume–Price Sensitivity and Margin Analysis")

st.caption("This simulation helps assess how volume changes affect profitability at different markup levels — while keeping margins above a set minimum threshold.")

# Input controls
st.sidebar.markdown("### Simulation Controls")
base_markup = st.sidebar.slider("Current Markup (×)", 1.0, 3.0, 1.5, 0.05)
min_markup = st.sidebar.slider("Min Markup to Test (×)", 1.0, base_markup, 1.3, 0.05)
max_markup = st.sidebar.slider("Max Markup to Test (×)", base_markup, 3.0, 2.0, 0.05)
volume_growth_range = st.sidebar.slider("Volume Growth Range (%)", -50, 300, (0, 200), 10)
opex_sensitivity = st.sidebar.slider("OPEX Sensitivity (%)", 0, 100, 10, 5)
min_margin = st.sidebar.number_input("Minimum Acceptable Margin (%)", 0.0, 100.0, 15.0, 0.5)

# Create simulation table
volume_growth_values = range(volume_growth_range[0], volume_growth_range[1] + 10, 10)
markup_values = np.arange(min_markup, max_markup + 0.01, 0.05)

simulation = []
for mg in markup_values:
    for vg in volume_growth_values:
        new_volume = volume * (1 + vg / 100)
        new_price = (cogs / volume) * mg
        new_revenue = new_price * new_volume
        new_cogs = (cogs / volume) * new_volume
        new_opex = (opex_percent * new_revenue) * (1 + opex_sensitivity / 100)
        ebitda = new_revenue - new_cogs - new_opex
        margin = (ebitda / new_revenue) * 100
        meets_threshold = margin >= min_margin
        simulation.append([mg, vg, new_revenue, ebitda, margin, meets_threshold])

simulation_df = pd.DataFrame(simulation, columns=["Markup", "Volume Growth (%)", "Revenue", "EBITDA", "EBITDA Margin (%)", "Meets Threshold"])

# --- MAIN ALERT BOX ---
safe_scenarios = simulation_df[simulation_df["Meets Threshold"]]

if not safe_scenarios.empty:
    lowest_safe_markup = safe_scenarios.groupby("Markup")["EBITDA Margin (%)"].mean().idxmin()
    st.success(
        f"Profitability is safe. At least one markup–volume combination maintains "
        f"a margin above your {min_margin:.1f}% threshold.\n\n"
        f"🔹 The lowest safe markup is approximately **{lowest_safe_markup:.2f}×**."
    )
else:
    st.error(
        f"All tested markup–volume combinations fall below your {min_margin:.1f}% minimum margin. "
        f"Consider increasing markup or reducing OPEX."
    )

# --- HIGHLIGHTED TABLE ---
styled_df = simulation_df.pivot_table(index="Volume Growth (%)", columns="Markup", values="EBITDA Margin (%)")

def highlight_margin(val):
    color = "#d4edda" if val >= min_margin else "#f8d7da"  # green for safe, red for below
    return f"background-color: {color}"

st.dataframe(styled_df.style.applymap(highlight_margin), use_container_width=True)

# --- CHART ---
st.line_chart(simulation_df.pivot(index="Volume Growth (%)", columns="Markup", values="EBITDA Margin (%)"))

# --- INSIGHT SECTION ---
best_combo = simulation_df.loc[simulation_df["EBITDA"].idxmax()]

st.info(
    f"Best outcome at **{best_combo['Markup']:.2f}×** markup and "
    f"**{best_combo['Volume Growth (%)']:.0f}%** volume growth → "
    f"EBITDA margin **{best_combo['EBITDA Margin (%)']:.1f}%**."
)

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:14px;'>Created by <b>Ayokunle Thomas</b> – Data Analyst</p>",
    unsafe_allow_html=True
)
st.markdown(
    """
    <div class="footer-links">
        <a href="https://www.linkedin.com/in/ayokunle-thomas" target="_blank">LinkedIn</a> |
        <a href="https://github.com/ThomasAyokunle" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("ExCare Services Pharmacy Department Pricing Calculator © 2025")
