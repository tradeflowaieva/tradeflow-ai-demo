import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="TradeFlow AI - Inbound Exception", page_icon="📦", layout="wide")

st.title("📦 TradeFlow AI")
st.subheader("Warehouse Inbound Exception Assistant")
st.caption("Independent Proof of Concept — fictional/demo data only")

st.info(
    "Use this demo to register inbound warehouse discrepancies digitally. "
    "No real company or customer data should be entered without approval."
)

ISSUE_TYPES = [
    "Missing item",
    "Over delivery",
    "Wrong item",
    "Wrong destination",
    "Damaged goods",
    "Wrong label / marking",
    "Other discrepancy",
]

if "exceptions" not in st.session_state:
    st.session_state.exceptions = []

def build_summary(issue_type, supplier, po, sku, expected, received, comment):
    diff = received - expected
    if diff < 0:
        qty_note = f"{abs(diff)} unit(s) missing."
    elif diff > 0:
        qty_note = f"{diff} extra unit(s) received."
    else:
        qty_note = "Expected and received quantity match."

    parts = [
        f"Issue: {issue_type}.",
        f"Supplier: {supplier or 'Not entered'}.",
        f"PO/Order: {po or 'Not entered'}.",
        f"SKU: {sku or 'Not entered'}.",
        f"Expected: {expected}. Received: {received}.",
        qty_note,
    ]
    if comment.strip():
        parts.append(f"Comment: {comment.strip()}")
    return " ".join(parts)

tab1, tab2 = st.tabs(["➕ Register exception", "📋 Exception dashboard"])

with tab1:
    st.markdown("### New inbound exception")

    col1, col2 = st.columns(2)

    with col1:
        issue_type = st.selectbox("What is the problem?", ISSUE_TYPES)
        supplier = st.text_input("Supplier", placeholder="Example Supplier AB")
        po = st.text_input("PO / Order number", placeholder="PO-458921")
        sku = st.text_input("SKU / Product number", placeholder="SKU-78123")

    with col2:
        expected = st.number_input("Expected quantity", min_value=0, step=1, value=0)
        received = st.number_input("Received quantity", min_value=0, step=1, value=0)
        destination = st.text_input("Expected destination", placeholder="Warehouse / site / customer")
        comment = st.text_area("Comment", placeholder="Short description of what happened")

    uploaded_photo = st.file_uploader(
        "Optional photo of label / package (demo only)",
        type=["jpg", "jpeg", "png"]
    )

    summary = build_summary(issue_type, supplier, po, sku, expected, received, comment)

    st.markdown("### Auto-generated exception summary")
    st.write(summary)

    if issue_type in ["Wrong destination", "Wrong item", "Damaged goods"]:
        priority = "HIGH"
    elif expected != received:
        priority = "MEDIUM"
    else:
        priority = "NORMAL"

    st.write(f"**Suggested priority:** {priority}")

    if st.button("Submit exception", type="primary", use_container_width=True):
        case_id = f"EXC-{len(st.session_state.exceptions)+1:04d}"
        st.session_state.exceptions.append({
            "Case ID": case_id,
            "Created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Issue": issue_type,
            "Supplier": supplier or "Not entered",
            "PO / Order": po or "Not entered",
            "SKU": sku or "Not entered",
            "Expected": int(expected),
            "Received": int(received),
            "Difference": int(received - expected),
            "Destination": destination or "Not entered",
            "Priority": priority,
            "Status": "NEW",
            "Summary": summary,
            "Photo": "Yes" if uploaded_photo else "No",
        })
        st.success(f"{case_id} created and sent to the exception queue.")

with tab2:
    st.markdown("### Inbound exception dashboard")

    df = pd.DataFrame(st.session_state.exceptions)

    if df.empty:
        st.write("No exceptions registered yet.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Open cases", int((df["Status"] != "RESOLVED").sum()))
        m2.metric("High priority", int((df["Priority"] == "HIGH").sum()))
        m3.metric("Missing / shortage", int((df["Difference"] < 0).sum()))
        m4.metric("Over deliveries", int((df["Difference"] > 0).sum()))

        st.dataframe(
            df[
                [
                    "Case ID", "Created", "Issue", "Supplier", "PO / Order",
                    "SKU", "Expected", "Received", "Priority", "Status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Update case status")
        case = st.selectbox("Choose case", df["Case ID"].tolist())
        new_status = st.selectbox("New status", ["NEW", "IN PROGRESS", "RESOLVED"])

        if st.button("Update status"):
            for item in st.session_state.exceptions:
                if item["Case ID"] == case:
                    item["Status"] = new_status
                    break
            st.success(f"{case} updated to {new_status}.")
            st.rerun()

        st.markdown("### Supplier / issue overview")
        supplier_counts = df.groupby("Supplier").size().reset_index(name="Exceptions")
        supplier_counts = supplier_counts.sort_values("Exceptions", ascending=False)
        st.dataframe(supplier_counts, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "PoC only. Future version can scan labels, read delivery documents, create AI summaries, "
    "notify the responsible team, and analyse recurring supplier problems."
)
