import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="5S SmartStock", page_icon="📦", layout="wide")

st.title("📦 5S SmartStock")
st.subheader("AI-assisted Material Planning")
st.caption("TradeFlow AI – Proof of Concept")

st.info(
    "Demo with fictional data. SmartStock helps estimate when warehouse "
    "consumables should be reordered based on stock, usage, lead time "
    "and safety stock."
)

# Fictional demo data
demo_data = [
    {
        "Material": "Gloves",
        "Current stock": 4,
        "Weekly usage": 3,
        "Lead time (weeks)": 3,
        "Safety stock (weeks)": 1,
    },
    {
        "Material": "Tape",
        "Current stock": 20,
        "Weekly usage": 4,
        "Lead time (weeks)": 1,
        "Safety stock (weeks)": 1,
    },
    {
        "Material": "Safety knives",
        "Current stock": 7,
        "Weekly usage": 3,
        "Lead time (weeks)": 2,
        "Safety stock (weeks)": 1,
    },
    {
        "Material": "Pallets",
        "Current stock": 35,
        "Weekly usage": 10,
        "Lead time (weeks)": 1,
        "Safety stock (weeks)": 1,
    },
    {
        "Material": "Labels",
        "Current stock": 8,
        "Weekly usage": 5,
        "Lead time (weeks)": 2,
        "Safety stock (weeks)": 1,
    },
]

st.markdown("### 📝 Weekly 5S Check")

material = st.selectbox(
    "Material",
    ["Gloves", "Tape", "Safety knives", "Pallets", "Labels"]
)

col1, col2 = st.columns(2)

with col1:
    current_stock = st.number_input(
        "Current stock",
        min_value=0,
        value=4,
        step=1
    )

    weekly_usage = st.number_input(
        "Average weekly usage",
        min_value=0.0,
        value=3.0,
        step=1.0
    )

with col2:
    lead_time = st.number_input(
        "Supplier lead time (weeks)",
        min_value=0.0,
        value=3.0,
        step=0.5
    )

    safety_weeks = st.number_input(
        "Safety stock (weeks)",
        min_value=0.0,
        value=1.0,
        step=0.5
    )

if weekly_usage > 0:
    weeks_remaining = current_stock / weekly_usage
else:
    weeks_remaining = float("inf")

lead_time_demand = weekly_usage * lead_time
safety_stock = weekly_usage * safety_weeks
target_stock = lead_time_demand + safety_stock
recommended_order = max(0, math.ceil(target_stock - current_stock))

if current_stock <= lead_time_demand:
    status = "🔴 CRITICAL – Order now"
elif current_stock <= target_stock:
    status = "🟠 LOW – Plan order"
else:
    status = "🟢 OK"

if st.button("✨ Calculate SmartStock Recommendation"):
    st.markdown("### SmartStock Recommendation")

    c1, c2, c3 = st.columns(3)

    c1.metric("Stock available", current_stock)

    if weeks_remaining == float("inf"):
        c2.metric("Estimated weeks remaining", "N/A")
    else:
        c2.metric("Estimated weeks remaining", f"{weeks_remaining:.1f}")

    c3.metric("Recommended order", recommended_order)

    st.write(f"**Status:** {status}")
    st.write(f"**Material:** {material}")
    st.write(f"**Demand during lead time:** {lead_time_demand:.1f}")
    st.write(f"**Safety stock:** {safety_stock:.1f}")
    st.write(f"**Target stock:** {target_stock:.1f}")

    if recommended_order > 0:
        st.warning(
            f"Recommended action: Order approximately "
            f"{recommended_order} units of {material}."
        )
    else:
        st.success("Current stock is sufficient. No order is recommended now.")

st.divider()

st.markdown("### 📊 5S Material Overview")

df = pd.DataFrame(demo_data)

def calculate_row(row):
    lead_demand = row["Weekly usage"] * row["Lead time (weeks)"]
    safety = row["Weekly usage"] * row["Safety stock (weeks)"]
    target = lead_demand + safety
    order = max(0, math.ceil(target - row["Current stock"]))

    if row["Current stock"] <= lead_demand:
        status = "🔴 Critical"
    elif row["Current stock"] <= target:
        status = "🟠 Low"
    else:
        status = "🟢 OK"

    return pd.Series([status, order])

df[["Status", "Recommended order"]] = df.apply(calculate_row, axis=1)

st.dataframe(df, use_container_width=True, hide_index=True)

critical_items = len(df[df["Status"] == "🔴 Critical"])
low_items = len(df[df["Status"] == "🟠 Low"])
total_to_order = int(df["Recommended order"].sum())

st.markdown("### 📈 SmartStock Dashboard")

d1, d2, d3 = st.columns(3)
d1.metric("Critical materials", critical_items)
d2.metric("Low-stock materials", low_items)
d3.metric("Units recommended to order", total_to_order)

st.caption(
    "Proof of concept only. A future version could connect to real-time "
    "inventory, historical consumption and supplier lead-time data."
)
