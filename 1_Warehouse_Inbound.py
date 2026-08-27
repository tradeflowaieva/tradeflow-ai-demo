import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="TradeFlow AI - Warehouse Inbound",
    page_icon="📦",
    layout="wide"
)

st.title("📦 TradeFlow AI")
st.subheader("Warehouse Inbound Exception")
st.caption("Fast warehouse exception reporting — Proof of Concept / fictional demo only")

st.info(
    "Goal: scan the item, choose the problem, and let the system create the exception report automatically."
)

ISSUE_TYPES = [
    "Missing item",
    "Extra item / over delivery",
    "Wrong item",
    "Wrong destination",
    "Damaged goods",
    "Wrong label / marking",
    "Other discrepancy",
]

if "inbound_cases" not in st.session_state:
    st.session_state.inbound_cases = []

tab1, tab2 = st.tabs(["⚡ Quick report", "📋 Exception queue"])

with tab1:
    st.markdown("### 1. Scan item")
    barcode = st.text_input(
        "Scan barcode / enter SKU",
        placeholder="Scan with warehouse scanner or type product number"
    )

    st.markdown("### 2. Choose what is wrong")
    issue = st.selectbox("Problem", ISSUE_TYPES)

    expected = 0
    received = 0

    if issue in ["Missing item", "Extra item / over delivery"]:
        c1, c2 = st.columns(2)
        with c1:
            expected = st.number_input("Expected quantity", min_value=0, step=1, value=0)
        with c2:
            received = st.number_input("Received quantity", min_value=0, step=1, value=0)

    destination = ""
    if issue == "Wrong destination":
        destination = st.text_input(
            "Where should it have gone?",
            placeholder="Other warehouse / customer / location"
        )

    photo = None
    if issue in ["Wrong item", "Damaged goods", "Wrong label / marking"]:
        photo = st.file_uploader(
            "Optional photo",
            type=["jpg", "jpeg", "png"]
        )

    note = st.text_input(
        "Optional short note",
        placeholder="Only if something extra needs explaining"
    )

    qty_text = ""
    priority = "NORMAL"

    if issue == "Missing item":
        diff = max(expected - received, 0)
        qty_text = f"Expected {expected}, received {received}. Missing quantity: {diff}."
        priority = "MEDIUM"
    elif issue == "Extra item / over delivery":
        diff = max(received - expected, 0)
        qty_text = f"Expected {expected}, received {received}. Extra quantity: {diff}."
        priority = "MEDIUM"
    elif issue in ["Wrong item", "Wrong destination", "Damaged goods"]:
        priority = "HIGH"

    summary_parts = [
        f"Inbound exception: {issue}.",
        f"Item/SKU: {barcode or 'Not scanned'}."
    ]

    if qty_text:
        summary_parts.append(qty_text)

    if destination:
        summary_parts.append(f"Expected destination: {destination}.")

    if note.strip():
        summary_parts.append(f"Note: {note.strip()}")

    auto_summary = " ".join(summary_parts)

    st.markdown("### 3. Automatic report")
    st.success(auto_summary)
    st.write(f"**Suggested priority:** {priority}")

    if st.button("Submit exception", type="primary", use_container_width=True):
        case_id = f"INB-{len(st.session_state.inbound_cases)+1:04d}"

        st.session_state.inbound_cases.append({
            "Case ID": case_id,
            "Created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Item / SKU": barcode or "Not scanned",
            "Issue": issue,
            "Expected": int(expected),
            "Received": int(received),
            "Destination": destination or "",
            "Priority": priority,
            "Photo": "Yes" if photo else "No",
            "Status": "NEW",
            "Report": auto_summary,
        })

        st.success(f"✅ {case_id} created. No manual exception text needed.")

with tab2:
    st.markdown("### Digital exception queue")

    df = pd.DataFrame(st.session_state.inbound_cases)

    if df.empty:
        st.write("No inbound exceptions registered yet.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Open", int((df["Status"] != "RESOLVED").sum()))
        c2.metric("High priority", int((df["Priority"] == "HIGH").sum()))
        c3.metric("Resolved", int((df["Status"] == "RESOLVED").sum()))

        st.dataframe(
            df[
                [
                    "Case ID",
                    "Created",
                    "Item / SKU",
                    "Issue",
                    "Priority",
                    "Status",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Update case")
        selected = st.selectbox("Case", df["Case ID"].tolist())
        status = st.selectbox("Status", ["NEW", "IN PROGRESS", "RESOLVED"])

        if st.button("Save status"):
            for case in st.session_state.inbound_cases:
                if case["Case ID"] == selected:
                    case["Status"] = status
                    break
            st.success(f"{selected} updated to {status}.")
            st.rerun()

        st.markdown("### Full automatic report")
        chosen_case = next(
            case for case in st.session_state.inbound_cases
            if case["Case ID"] == selected
        )
        st.write(chosen_case["Report"])

st.divider()
st.caption(
    "Future version: barcode integration, automatic lookup from WMS/ERP, label OCR, "
    "supplier/PO lookup, routing to the responsible team, and supplier error analytics."
)
